import pytest
from unittest.mock import patch, MagicMock, Mock
from flask import Flask
from app.domain.models import Product, ProductAttribute
from app.application.services.product_page_service import ProductPageService
from app.infrastructure.persistence.product_repository import ProductRepository
from app.infrastructure.persistence.review_repository import ReviewRepository
from app.web.routes.product import init_product_routes


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'

    with app.app_context():
        init_product_routes(app)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_product():
    attributes = ProductAttribute(
        colors=["red", "blue"],
        sizes=["M", "L"],
        material="cotton"
    )
    return Product(
        name="Test Product",
        care="Test care",
        description="Test description",
        price=100.0,
        category_id="test-category",
        attributes=attributes,
        images=["test.jpg"],
        stock=10,
        product_id="507f1f77bcf86cd799439011"
    )


# ---------- ProductPageService Tests ----------

class TestProductPageService:
    @patch('app.application.services.product_page_service.ProductRepository')
    def test_get_existing_product(self, mock_repo, mock_product):
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.get_product_by_id.return_value = mock_product
        service = ProductPageService()
        result = service.get_product_by_id("valid_id")
        assert result == mock_product
        mock_repo_instance.get_product_by_id.assert_called_once_with("valid_id")

    @patch('app.application.services.product_page_service.ProductRepository')
    def test_get_nonexistent_product(self, mock_repo):
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.get_product_by_id.return_value = None
        service = ProductPageService()
        result = service.get_product_by_id("invalid_id")
        assert result is None
        mock_repo_instance.get_product_by_id.assert_called_once_with("invalid_id")

    @patch('app.application.services.product_page_service.ProductRepository')
    def test_get_related_products(self, mock_repo, mock_product):
        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.get_related_products.return_value = [mock_product]
        service = ProductPageService()
        related = service.get_related_products(mock_product, limit=3)
        assert len(related) == 1
        mock_repo_instance.get_related_products.assert_called_once_with(
            category_slug="test-category",
            exclude_id="507f1f77bcf86cd799439011",
            limit=3
        )


# ---------- Flask Route Tests ----------

class TestProductRoutes:
    @patch('app.web.routes.product.ProductRepository')
    @patch('app.web.routes.product.ReviewRepository')
    @patch('app.web.routes.product.render_template')
    def test_product_page_success(self, mock_render, mock_review_repo, mock_product_repo, client, mock_product):
        mock_product_repo_instance = mock_product_repo.return_value
        mock_product_repo_instance.get_product_by_id.return_value = mock_product
        mock_product_repo_instance.get_related_products.return_value = [mock_product]
        mock_review_repo_instance = mock_review_repo.return_value
        mock_review_repo_instance.get_reviews_by_product_id.return_value = []
        mock_render.return_value = "rendered_template_with_Test_Product"

        response = client.get('/product/507f1f77bcf86cd799439011')
        assert response.status_code == 200
        assert response.data.decode('utf-8') == "rendered_template_with_Test_Product"

    @patch('app.web.routes.product.ProductRepository')
    @patch('app.web.routes.product.ReviewRepository')
    def test_product_page_not_found(self, mock_review_repo, mock_product_repo, client):
        mock_product_repo_instance = mock_product_repo.return_value
        mock_product_repo_instance.get_product_by_id.return_value = None
        mock_review_repo_instance = mock_review_repo.return_value
        mock_review_repo_instance.get_reviews_by_product_id.return_value = []

        response = client.get('/product/invalid_id')
        assert response.status_code == 404

    @patch('app.web.routes.product.ProductRepository')
    @patch('app.web.routes.product.ReviewRepository')
    def test_add_valid_comment(self, mock_review_repo, mock_product_repo, client):
        mock_product_repo_instance = mock_product_repo.return_value
        mock_product_repo_instance.get_product_by_id.return_value = Mock()  # Mock product to avoid None
        mock_review_repo_instance = mock_review_repo.return_value
        mock_review_repo_instance.add_review.return_value = None

        response = client.post(
            '/product/507f1f77bcf86cd799439011/add_comment',
            data={'comment': 'Great!', 'rating': '5'}
        )
        assert response.status_code == 302

    @patch('app.web.routes.product.ProductRepository')
    @patch('app.web.routes.product.ReviewRepository')
    def test_add_invalid_comment(self, mock_review_repo, mock_product_repo, client):
        mock_product_repo_instance = mock_product_repo.return_value
        mock_product_repo_instance.get_product_by_id.return_value = Mock()  # Mock product to avoid None
        mock_review_repo_instance = mock_review_repo.return_value
        mock_review_repo_instance.add_review.return_value = None

        response = client.post(
            '/product/507f1f77bcf86cd799439011/add_comment',
            data={'comment': '', 'rating': '6'}
        )
        assert response.status_code == 400

    @patch('app.web.routes.product.ProductRepository')
    @patch('app.web.routes.product.ReviewRepository')
    @patch('app.web.routes.product.render_template')
    def test_template_context(self, mock_render, mock_review_repo, mock_product_repo, client, mock_product):
        mock_product_repo_instance = mock_product_repo.return_value
        mock_product_repo_instance.get_product_by_id.return_value = mock_product
        mock_product_repo_instance.get_related_products.return_value = [mock_product]
        mock_review_repo_instance = mock_review_repo.return_value
        mock_review_repo_instance.get_reviews_by_product_id.return_value = [MagicMock(rating=4)]
        mock_render.return_value = "rendered_template_with_rating_and_reviews"

        response = client.get('/product/507f1f77bcf86cd799439011')
        html = response.data.decode('utf-8')
        assert response.status_code == 200
        assert "rendered_template_with_rating_and_reviews" in html