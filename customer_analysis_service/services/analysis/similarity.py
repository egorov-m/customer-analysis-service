import logging as log

import faiss
import numpy as np
import torch
from sqlmodel import select, Session
from transformers import AutoTokenizer, AutoModel

from customer_analysis_service.api.v1.schemas.analysis import data_to_schema, CustomerReputationAnalysisValue
from customer_analysis_service.db.models import Review, Comment, Product, ProductSimilarityAnalysis, Customer, \
    CustomerSimilarityAnalysis
from customer_analysis_service.db.repository import ProductRepository, CustomerRepository, ReviewRepository, \
    CommentRepository
from customer_analysis_service.services.analysis.base import BaseService


class SimilarityAnalysisService(BaseService):
    logger = log.getLogger('similarity_analysis_service_logger')

    def __init__(self, session: Session, is_init_model: bool = False):
        super().__init__(session)
        if is_init_model:
            self._init_model()
        else:
            self.tokenizer = None
            self.model = None
        self.logger.info('SimilarityAnalysisService initialized.')

    def _init_model(self):
        # Load model from HuggingFace Hub
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/nli-distilroberta-base-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/nli-distilroberta-base-v2')

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
        encoded_input = self.tokenizer(sentences,  padding=True, truncation=True, return_tensors='pt')
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
            products_similarity_analysis: list[ProductSimilarityAnalysis] = product_repo.get_products_similarity_analysis(product.name_id, version_mark)
            if len(products_similarity_analysis) > 0:
                product_similarity_analysis: ProductSimilarityAnalysis = products_similarity_analysis[0]
                if is_override:
                    reviews, comments = self._init_reviews_comments_for_product(product)
                    similarity_value_reviews: float = self.get_mean_similarity_for_all_sentence(
                        [item.text_review for item in reviews])
                    similarity_value_comments: float = self.get_mean_similarity_for_all_sentence(
                        [item.text_comment for item in comments])
                    if similarity_value_reviews is None and similarity_value_comments is None:
                        self.logger.info(f'[{count}] Product {product.name_id} skipped (no valid amount reviews and comments).')
                        count += 1
                        continue
                    product_repo.update_similarity_values_product_similarity_analysis(product_similarity_analysis,
                                                                                      similarity_value_reviews,
                                                                                      similarity_value_comments)
                    self.logger.info(f'[{count}] Product {product.name_id} updated: r - {similarity_value_reviews}, c - {similarity_value_comments}.')
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
                    self.logger.info(f'[{count}] Product {product.name_id} skipped (no valid amount reviews and comments).')
                    count += 1
                    continue

                product_similarity_analysis: ProductSimilarityAnalysis = ProductSimilarityAnalysis()
                product_similarity_analysis.product_name_id = product.name_id
                product_similarity_analysis.version_mark = version_mark
                product_similarity_analysis.similarity_reviews_value = similarity_value_reviews
                product_similarity_analysis.similarity_comments_value = similarity_value_comments
                product_repo.add_product_sentiment_analysis(product_similarity_analysis)
                self.logger.info(f'[{count}] Similarity analysis added product: {product.name_id}: r - {similarity_value_reviews}, c - {similarity_value_comments}.')
                count += 1

        self.logger.info('Similarity analysis of all products is complete.')

    def execute_similarity_analysis_customers(self, version_mark: str, is_override: bool = False):
        self.logger.info('Similarity analysis process launched for all customers.')
        customer_repo: CustomerRepository = CustomerRepository(self.session)
        customers: list[Customer] = customer_repo.get_all_customers()
        count: int = 1
        self.logger.info(f'{len(customers)} customers found.')

        for customer in customers:
            customers_similarity_analysis: list[CustomerSimilarityAnalysis] = customer_repo.get_customers_similarity_analysis(customer.name_id, version_mark)
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
                        self.logger.info(f'[{count}] Customer {customer.name_id} skipped (no valid amount reviews and comments).')
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
                    self.logger.info(f'[{count}] Customer {customer.name_id} skipped (no valid amount reviews and comments).')
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

    def get_customer_by_reputation_similarity_analysis_product_by_comments(self, product_name_id: str):
        """
        SELECT similarity_comments_value, c.reputation
        FROM customer_similarity_analysis
        JOIN customer c on c.name_id = customer_similarity_analysis.customer_name_id
        WHERE customer_name_id IN (SELECT comment.customer_name_id
                                   FROM comment
                                   JOIN review r on r.id = comment.review_id
                                   WHERE r.evaluated_product_name_id = 'product_name_id');
        :param product_name_id:
        :return:
        """
        with self.session as session:
            subquery = select(Comment.customer_name_id).distinct()\
                .join(Review, Comment.review_id == Review.id)\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = select(Customer.reputation, CustomerSimilarityAnalysis.similarity_comments_value).\
                join(Customer, CustomerSimilarityAnalysis.customer_name_id == Customer.name_id)\
                .where(Customer.name_id.in_(subquery))

            result = session.execute(query).all()

            return data_to_schema(result, CustomerReputationAnalysisValue)

    def get_customer_by_reputation_similarity_analysis_product_by_reviews(self, product_name_id: str):
        """
        SELECT similarity_reviews_value, c.reputation
        FROM customer_similarity_analysis
        JOIN customer c on c.name_id = customer_similarity_analysis.customer_name_id
        WHERE customer_name_id IN (SELECT review.customer_name_id
                                   FROM review
                                   WHERE evaluated_product_name_id = product_name_id);
        :param product_name_id:
        :return:
        """
        with self.session as session:
            subquery = select(Review.customer_name_id).distinct()\
                .where(Review.evaluated_product_name_id == product_name_id)

            query = select(Customer.reputation, CustomerSimilarityAnalysis.similarity_reviews_value)\
                .join(Customer, CustomerSimilarityAnalysis.customer_name_id == Customer.name_id)\
                .where(Customer.name_id.in_(subquery))

            result = session.execute(query).all()

            return data_to_schema(result, CustomerReputationAnalysisValue)
