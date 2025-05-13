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
        return {
            'featured_products': self.product_repo.find_featured(),
            'new_arrivals': self.product_repo.find_new_arrivals(),
            'featured_categories': self.category_repo.find_featured(limit=None),
            'recent_reviews': self.review_repo.find_for_homepage()
        }
