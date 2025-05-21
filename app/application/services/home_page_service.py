from app.domain.models import Product
from app.infrastructure.persistence.product_repository import ProductRepository
from app.infrastructure.persistence.category_repository import CategoryRepository
from app.infrastructure.persistence.review_repository import ReviewRepository


class HomePageService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.category_repo = CategoryRepository()
        self.review_repo = ReviewRepository()

    def get_home_page_data(self):
        # Отримуємо всі товари
        all_products = self.product_repo.find_all()

        # Додаємо середній рейтинг до кожного продукту
        for product in all_products:
            reviews = self.review_repo.get_reviews_by_product_id(product.product_id)
            product.average_rating = (sum(review.rating for review in reviews) / len(reviews)) if reviews else 0
            product.reviews_count = len(reviews)

        # Сортуємо товари за середнім рейтингом (від найвищого до найнижчого)
        top_rated_products = sorted(
            all_products,
            key=lambda x: x.average_rating,
            reverse=True
        )[:8]

        return {
            'featured_products': top_rated_products,
            'new_arrivals': self.product_repo.find_new_arrivals(),
            'featured_categories': self.category_repo.find_featured(limit=None),
            'reviews': self.review_repo.get_random_reviews(limit=10)
        }
