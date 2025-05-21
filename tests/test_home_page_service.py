import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.application.services.home_page_service import HomePageService
from app.domain.models import Product, ProductAttribute, Review


class TestHomePageService:
    @pytest.fixture
    def mock_repositories(self):
        with patch('app.application.services.home_page_service.ProductRepository') as mock_product_repo, \
                patch('app.application.services.home_page_service.CategoryRepository') as mock_category_repo, \
                patch('app.application.services.home_page_service.ReviewRepository') as mock_review_repo:
            yield {
                'product_repo': mock_product_repo.return_value,
                'category_repo': mock_category_repo.return_value,
                'review_repo': mock_review_repo.return_value
            }

    @pytest.fixture
    def sample_product_attributes(self):
        return ProductAttribute(
            colors=["red", "blue"],
            sizes=["S", "M", "L"],
            material="cotton"
        )

    @pytest.fixture
    def sample_products(self, sample_product_attributes):
        return [
            Product(
                product_id="1",
                name="Product 1",
                care="Hand wash only",
                description="Test product 1",
                price=100.0,
                category_id="category-1",
                attributes=sample_product_attributes,
                images=["image1.jpg", "image2.jpg"],
                stock=10
            ),
            Product(
                product_id="2",
                name="Product 2",
                care="Machine wash",
                description="Test product 2",
                price=200.0,
                category_id="category-2",
                attributes=sample_product_attributes,
                images=["image3.jpg"],
                stock=5
            )
        ]

    @pytest.fixture
    def sample_reviews(self):
        return [
            Review(
                id="1",
                product_id="1",
                user_name="User 1",
                text="Great product",
                created_at=datetime.now(),
                rating=5
            ),
            Review(
                id="2",
                product_id="1",
                user_name="User 2",
                text="Good product",
                created_at=datetime.now(),
                rating=4
            ),
            Review(
                id="3",
                product_id="2",
                user_name="User 3",
                text="Average product",
                created_at=datetime.now(),
                rating=3
            )
        ]

    def test_get_home_page_data_success(self, mock_repositories, sample_products, sample_reviews):
        # Arrange
        mock_repositories['product_repo'].find_all.return_value = sample_products
        mock_repositories['product_repo'].find_new_arrivals.return_value = sample_products[:1]
        mock_repositories['category_repo'].find_featured.return_value = ["Category1", "Category2"]
        mock_repositories['review_repo'].get_random_reviews.return_value = sample_reviews[:2]

        def mock_get_reviews(product_id):
            return [r for r in sample_reviews if r.product_id == product_id]

        mock_repositories['review_repo'].get_reviews_by_product_id.side_effect = mock_get_reviews

        service = HomePageService()

        # Act
        result = service.get_home_page_data()

        # Assert
        mock_repositories['product_repo'].find_all.assert_called_once()
        mock_repositories['product_repo'].find_new_arrivals.assert_called_once()
        mock_repositories['category_repo'].find_featured.assert_called_once_with(limit=None)
        mock_repositories['review_repo'].get_random_reviews.assert_called_once_with(limit=10)

        assert mock_repositories['review_repo'].get_reviews_by_product_id.call_count == len(sample_products)

        assert 'featured_products' in result
        assert 'new_arrivals' in result
        assert 'featured_categories' in result
        assert 'reviews' in result

        assert len(result['featured_products']) == 2
        assert result['featured_products'][0].average_rating == 4.5  # (5+4)/2
        assert result['featured_products'][0].reviews_count == 2
        assert result['featured_products'][1].average_rating == 3.0
        assert result['featured_products'][1].reviews_count == 1
        assert result['featured_products'][0].average_rating >= result['featured_products'][1].average_rating

    def test_get_home_page_data_no_reviews(self, mock_repositories, sample_products):
        # Arrange
        mock_repositories['product_repo'].find_all.return_value = sample_products[:1]
        mock_repositories['product_repo'].find_new_arrivals.return_value = []
        mock_repositories['category_repo'].find_featured.return_value = []
        mock_repositories['review_repo'].get_random_reviews.return_value = []
        mock_repositories['review_repo'].get_reviews_by_product_id.return_value = []

        service = HomePageService()

        # Act
        result = service.get_home_page_data()

        # Assert
        assert result['featured_products'][0].average_rating == 0
        assert result['featured_products'][0].reviews_count == 0
        assert len(result['new_arrivals']) == 0
        assert len(result['featured_categories']) == 0
        assert len(result['reviews']) == 0

    def test_get_home_page_data_empty_products(self, mock_repositories):
        # Arrange
        mock_repositories['product_repo'].find_all.return_value = []
        mock_repositories['product_repo'].find_new_arrivals.return_value = []
        mock_repositories['category_repo'].find_featured.return_value = []
        mock_repositories['review_repo'].get_random_reviews.return_value = []

        service = HomePageService()

        # Act
        result = service.get_home_page_data()

        # Assert
        assert len(result['featured_products']) == 0
        assert len(result['new_arrivals']) == 0
        assert len(result['featured_categories']) == 0
        assert len(result['reviews']) == 0

    def test_get_home_page_data_division_by_zero_handling(self, mock_repositories, sample_products):
        # Arrange
        mock_repositories['product_repo'].find_all.return_value = sample_products[:1]
        mock_repositories['review_repo'].get_reviews_by_product_id.return_value = []  # немає відгуків

        service = HomePageService()

        # Act
        result = service.get_home_page_data()

        # Assert
        assert result['featured_products'][0].average_rating == 0
        assert result['featured_products'][0].reviews_count == 0