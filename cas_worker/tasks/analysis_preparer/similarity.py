import logging as log
from collections import Counter
from heapq import nlargest

import faiss
import numpy as np
import torch
from spacy import load, Language
from string import punctuation
from spacy.lang.ru.stop_words import STOP_WORDS
from spacy.tokens.span import Span
from transformers import AutoTokenizer, AutoModel, RobertaTokenizerFast, RobertaModel

from cas_shared.db.models import (
    Product,
    ProductSimilarityAnalysis,
    Customer,
    CustomerSimilarityAnalysis,
    Review,
    Comment
)
from cas_shared.db.repository import (
    ProductRepository,
    CustomerRepository,
    ReviewRepository,
    CommentRepository
)
from cas_worker.tasks.analysis_preparer.base import AnalysisPreparer
from config import WorkerTasks


class BaseSimilarityAnalysisPreparer(AnalysisPreparer):
    logger = log.getLogger('similarity_analysis_preparer_logger')

    def __init__(self):
        super().__init__()
        self.tokenizer: RobertaTokenizerFast = AutoTokenizer.from_pretrained('sentence-transformers/nli-distilroberta-base-v2')
        self.model: RobertaModel = AutoModel.from_pretrained('sentence-transformers/nli-distilroberta-base-v2')
        self.spacy_nlp: Language = load("ru_core_news_lg")
        self.logger.info('SimilarityAnalysisPreparer initialized.')

    @staticmethod
    def _mean_pooling(model_output, attention_mask):
        """
        Mean Pooling - Take attention mask into account for correct averaging

        :param model_output:
        :param attention_mask:
        :return:
        """
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    @staticmethod
    def _calculate_similarity(embeddings):
        index = faiss.IndexFlatIP(embeddings.shape[1])
        faiss.normalize_L2(embeddings)
        index.add(embeddings)

        D, I = index.search(embeddings, k=len(embeddings))
        return D

    def _summarize_sentence(self, sentence: str) -> str:
        doc = self.spacy_nlp(sentence)
        # Filtering tokens
        keyword = []
        stopwords = list(STOP_WORDS)
        pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB']  # parts-of-speech list
        for token in doc:
            if token.text in stopwords or token.text in punctuation:
                continue
            if token.pos_ in pos_tag:
                keyword.append(token.text)
        freq_word = Counter(keyword)
        # Normalization
        max_freq = 1
        if keyword:
            max_freq = freq_word.most_common(1)[0][1]
        for word in freq_word.keys():
            freq_word[word] = freq_word[word] / max_freq
        # Weighing sentences
        sent_strength = {}
        for sent in doc.sents:
            for word in sent:
                if word.text in freq_word.keys():
                    if sent in sent_strength.keys():
                        sent_strength[sent] += freq_word[word.text]
                    else:
                        sent_strength[sent] = freq_word[word.text]
        # Summarizing the string
        summarized_sentences: list[Span] = nlargest(2, sent_strength, key=sent_strength.get)
        final_sentences = [w.text for w in summarized_sentences]
        summary = " ".join(final_sentences)

        return summary

    def _summarize_sentences(self, sentences: list[str]) -> list[str]:
        return [self._summarize_sentence(sentence) for sentence in sentences]

    def _tokenize_and_get_vector_representations(self, sentences: list[str]):
        """
        Tokenize the input sentences and get a representation for faiss

        :param sentences:
        :return:
        """
        encoded_input = self.tokenizer(self._summarize_sentences(sentences),
                                       padding=True,
                                       max_length=300,
                                       truncation=True,
                                       return_tensors='pt')
        with torch.no_grad():
            self.logger.info('Begin model.')
            model_output = self.model(**encoded_input)
            self.logger.info('End model.')
            sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
            embeddings = sentence_embeddings.numpy().astype('float32')  # transformations for faiss

        return embeddings

    def _get_similarity_scores(self, sentences: list[str]):
        self.logger.info('Begin tokenize.')
        embeddings = self._tokenize_and_get_vector_representations(sentences)
        self.logger.info('End tokenize.')
        self.logger.info('Begin calculate similarity.')
        similarities = self._calculate_similarity(embeddings)
        self.logger.info('End calculate similarity.')

        return similarities

    def get_mean_similarity_for_all_sentence(self, sentences: list[str]) -> float:
        if len(sentences) <= 1:  # take at least two sentences for similarity analysis
            return None
        similarity_scores = self._get_similarity_scores(sentences)
        similarity = np.mean(similarity_scores)
        self.logger.info(f'Gets similarity value: {similarity} for the set of {len(sentences)} sentences')
        return float(similarity)

    def _init_reviews_comments_for_product(self, product: Product):
        review_repo: ReviewRepository = ReviewRepository(self.session)
        comment_repo: CommentRepository = CommentRepository(self.session)
        reviews: list[Review] = review_repo.get_all_reviews_for_product(product.name_id)
        comments: list[Comment] = comment_repo.get_all_comments_for_product(product.name_id)
        return reviews, comments

    def _init_reviews_comments_for_customer(self, customer: Customer):
        review_repo: ReviewRepository = ReviewRepository(self.session)
        comment_repo: CommentRepository = CommentRepository(self.session)
        reviews: list[Review] = review_repo.get_all_reviews_for_customer(customer.name_id)
        comments: list[Comment] = comment_repo.get_all_comments_for_customer(customer.name_id)
        return reviews, comments


class SimilarityAnalysisProductsPreparer(BaseSimilarityAnalysisPreparer):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_similarity_preparer_products

    def run(self, version_mark: str, is_override: bool = False):
        self.logger.info('Similarity analysis process launched for all products.')

        product_repo: ProductRepository = ProductRepository(self.session)
        products: list[Product] = product_repo.get_all_products()
        count: int = 1
        self.logger.info(f'{len(products)} products found.')

        for product in products:
            products_similarity_analysis: list[
                ProductSimilarityAnalysis] = product_repo.get_products_similarity_analysis(product.name_id,
                                                                                           version_mark)
            if len(products_similarity_analysis) > 0:
                product_similarity_analysis: ProductSimilarityAnalysis = products_similarity_analysis[0]
                if is_override:
                    reviews, comments = self._init_reviews_comments_for_product(product)
                    similarity_value_reviews: float = self.get_mean_similarity_for_all_sentence(
                        [item.text_review for item in reviews])
                    similarity_value_comments: float = self.get_mean_similarity_for_all_sentence(
                        [item.text_comment for item in comments])
                    if similarity_value_reviews is None and similarity_value_comments is None:
                        self.logger.info(
                            f'[{count}] Product {product.name_id} skipped (no valid amount reviews and comments).')
                        count += 1
                        continue
                    product_repo.update_similarity_values_product_similarity_analysis(product_similarity_analysis,
                                                                                      similarity_value_reviews,
                                                                                      similarity_value_comments)
                    self.logger.info(
                        f'[{count}] Product {product.name_id} updated: r - {similarity_value_reviews}, c - {similarity_value_comments}.')
                else:
                    self.logger.info(f'[{count}] Product {product.name_id} skipped.')

                count += 1
            else:
                reviews, comments = self._init_reviews_comments_for_product(product)
                similarity_value_reviews: float = self.get_mean_similarity_for_all_sentence(
                    [item.text_review for item in reviews])
                similarity_value_comments: float = self.get_mean_similarity_for_all_sentence(
                    [item.text_comment for item in comments])
                if similarity_value_reviews is None and similarity_value_comments is None:
                    self.logger.info(
                        f'[{count}] Product {product.name_id} skipped (no valid amount reviews and comments).')
                    count += 1
                    continue

                product_similarity_analysis: ProductSimilarityAnalysis = ProductSimilarityAnalysis()
                product_similarity_analysis.product_name_id = product.name_id
                product_similarity_analysis.version_mark = version_mark
                product_similarity_analysis.similarity_reviews_value = similarity_value_reviews
                product_similarity_analysis.similarity_comments_value = similarity_value_comments
                product_repo.add_product_sentiment_analysis(product_similarity_analysis)
                self.logger.info(
                    f'[{count}] Similarity analysis added product: {product.name_id}: r - {similarity_value_reviews}, c - {similarity_value_comments}.')
                count += 1

        self.logger.info('Similarity analysis of all products is complete.')


class SimilarityAnalysisCustomersPreparer(BaseSimilarityAnalysisPreparer):
    def __init__(self):
        super().__init__()
        self.name = WorkerTasks.analyser_similarity_preparer_customers

    def run(self, version_mark: str, is_override: bool = False):
        self.logger.info('Similarity analysis process launched for all customers.')
        customer_repo: CustomerRepository = CustomerRepository(self.session)
        customers: list[Customer] = customer_repo.get_all_customers()
        count: int = 1
        self.logger.info(f'{len(customers)} customers found.')

        for customer in customers:
            customers_similarity_analysis: list[
                CustomerSimilarityAnalysis] = customer_repo.get_customers_similarity_analysis(customer.name_id,
                                                                                              version_mark)
            if len(customers_similarity_analysis) > 0:
                customer_similarity_analysis: CustomerSimilarityAnalysis = customers_similarity_analysis[0]
                if is_override:
                    reviews, comments = self._init_reviews_comments_for_customer(customer)
                    self.logger.info(f'Product: r - {len(reviews)}, c - {len(comments)}')
                    similarity_value_reviews: float = self.get_mean_similarity_for_all_sentence(
                        [item.text_review for item in reviews])
                    similarity_value_comments: float = self.get_mean_similarity_for_all_sentence(
                        [item.text_comment for item in comments])
                    # if similarity_value_reviews is None and similarity_value_comments is None:
                    #     self.logger.info(
                    #         f'[{count}] Customer {customer.name_id} skipped (no valid amount reviews and comments).')
                    #     count += 1
                    #     continue
                    customer_repo.update_similarity_values_customer_similarity_analysis(customer_similarity_analysis,
                                                                                        similarity_value_reviews,
                                                                                        similarity_value_comments)
                    self.logger.info(
                        f'[{count}] Customer {customer.name_id} updated: r - {similarity_value_reviews}, c - {similarity_value_comments}.')
                else:
                    self.logger.info(f'[{count}] Customer {customer.name_id} skipped.')

                count += 1
            else:
                reviews, comments = self._init_reviews_comments_for_customer(customer)
                self.logger.info(f'Product: r - {len(reviews)}, c - {len(comments)}')
                similarity_value_reviews: float = self.get_mean_similarity_for_all_sentence(
                    [item.text_review for item in reviews])
                similarity_value_comments: float = self.get_mean_similarity_for_all_sentence(
                    [item.text_comment for item in comments])
                if similarity_value_reviews is None and similarity_value_comments is None:
                    self.logger.info(
                        f'[{count}] Customer {customer.name_id} skipped (no valid amount reviews and comments).')
                    count += 1
                    continue

                customer_similarity_analysis: CustomerSimilarityAnalysis = CustomerSimilarityAnalysis()
                customer_similarity_analysis.customer_name_id = customer.name_id
                customer_similarity_analysis.version_mark = version_mark
                customer_similarity_analysis.similarity_reviews_value = similarity_value_reviews
                customer_similarity_analysis.similarity_comments_value = similarity_value_comments
                customer_repo.add_product_sentiment_analysis(customer_similarity_analysis)
                self.logger.info(
                    f'[{count}] Similarity analysis added customer: {customer.name_id}: r - {similarity_value_reviews}, c - {similarity_value_comments}.')
                count += 1

        self.logger.info('Similarity analysis of all customers is complete.')
