import logging as log

import faiss
import numpy as np
import torch
from sqlmodel import Session
from transformers import AutoTokenizer, AutoModel

from cas_worker.db.models import Product, ProductSimilarityAnalysis, Customer, \
    CustomerSimilarityAnalysis, Review, Comment
from cas_worker.db.repository import ProductRepository, CustomerRepository, ReviewRepository, \
    CommentRepository
from cas_worker.tests.preparer.base import Preparer


class SimilarityAnalysisPreparer(Preparer):
    logger = log.getLogger('similarity_analysis_preparer_logger')

    def __init__(self, session: Session):
        super().__init__(session)
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/nli-distilroberta-base-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/nli-distilroberta-base-v2')
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

    def _tokenize_and_get_vector_representations(self, sentences: list[str]):
        """
        Tokenize the input sentences and get a representation for faiss

        :param sentences:
        :return:
        """
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
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

    def execute_similarity_analysis_products(self, version_mark: str, is_override: bool = False):
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

    def execute_similarity_analysis_customers(self, version_mark: str, is_override: bool = False):
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
                    if similarity_value_reviews is None and similarity_value_comments is None:
                        self.logger.info(
                            f'[{count}] Customer {customer.name_id} skipped (no valid amount reviews and comments).')
                        count += 1
                        continue
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
