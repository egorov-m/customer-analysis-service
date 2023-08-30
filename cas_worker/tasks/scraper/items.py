from scrapy.item import Item, Field


class ReviewItem(Item):
    """
    Information from the full review page
    example url: https://otzovik.com/review_{id}.html
    """
    id = Field()  # at the address line

    # is displayed above the title (1, etc. from left to right)
    ru_category_1 = Field()
    ru_category_2 = Field()
    ru_category_3 = Field()
    ru_category_4 = Field()

    href_category_1 = Field()
    href_category_2 = Field()
    href_category_3 = Field()
    href_category_4 = Field()

    evaluated_product_name_id = Field()

    customer_name_id = Field()  # name only (acts as an identifier)

    count_user_recommend_review = Field()
    count_comments_review = Field()
    date_review = Field()
    advantages = Field()
    disadvantages = Field()
    text_review = Field()
    general_impression = Field()
    star_rating = Field()
    recommend_friends = Field()


class CommentItem(Item):
    """
    The information is supposed to be taken from the page with all comments user
    example url: https://otzovik.com/?author_comments={user}
    """
    review_id = Field()
    customer_name_id = Field()  # name only (acts as an identifier)
    reg_datetime = Field()
    text_comment = Field()


class ProductItem(Item):
    """
    example url: https://otzovik.com/reviews/{title_id}/info/
    """
    name_id = Field()  # at the address line
    fullname = Field()
    image_url = Field()
    description = Field()


class CustomerItem(Item):
    """
    example url: https://otzovik.com/profile/{name_id}
    """
    name_id = Field()
    reputation = Field()
    country_ru = Field()
    country_en = Field()
    city_ru = Field()
    city_en = Field()
    profession = Field()
    reg_date = Field()
    count_subscribers = Field()
