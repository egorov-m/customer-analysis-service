from scrapy.item import Item, Field


class InfoToFindAllCustomers(Item):
    customer_name_id = Field()
    review_id = Field()


class Review(Item):
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
    year_service = Field()
    general_impression = Field()
    star_rating = Field()
    recommend_friends = Field()


class Comment(Item):
    """
    The information is supposed to be taken from the page with all comments user
    example url: https://otzovik.com/?author_comments={user}
    """
    review_id = Field()
    customer_name_id = Field()  # name only (acts as an identifier)
    reg_datetime = Field()
    text_comment = Field()


class Product(Item):
    """
    example url: https://otzovik.com/reviews/{title_id}/info/
    """
    name_id = Field()  # at the address line
    fullname = Field()
    image_url = Field()
    description = Field()


class Customer(Item):
    """
    example url: https://otzovik.com/profile/{name_id}
    """
    name_id = Field()
    reputation = Field()
    country = Field()
    city = Field()
    profession = Field()
    reg_date = Field()
    count_subscribers = Field()
    # last_activity_date = Field()
