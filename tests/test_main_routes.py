import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from app.web.routes.main import init_main_routes
from app.domain.models import Product, Category, ProductAttribute


class TestMainRoutes:
    @pytest.fixture
    def client(self):
        app = Flask(__name__)
        app.testing = True
        app.config['WTF_CSRF_ENABLED'] = False
        init_main_routes(app)
        return app.test_client()

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
                care="Hand wash",
                description="Desc 1",
                price=100,
                category_id="cat1",
                attributes=sample_product_attributes,
                images=["img1.jpg"],
                stock=10
            )
        ]

    @pytest.fixture
    def sample_categories(self):
        return [
            Category(id="1", name="Category 1", slug="cat1"),
            Category(id="2", name="Category 2", slug="cat2")
        ]

    def test_home_page_route(self, client, sample_products, sample_categories):
        with patch('app.web.routes.main.HomePageService') as mock_service, \
                patch('app.web.routes.main.render_template') as mock_render:
            mock_service.return_value.get_home_page_data.return_value = {
                'featured_products': sample_products,
                'new_arrivals': sample_products,
                'featured_categories': sample_categories,
                'reviews': []
            }

            response = client.get('/')
            assert response.status_code == 200
            mock_service.return_value.get_home_page_data.assert_called_once()
            mock_render.assert_called_once_with(
                'index.html',
                featured_products=sample_products,
                new_arrivals=sample_products,
                categories=sample_categories,
                reviews=[],
                benefits=[
                    {'icon': 'fa-truck', 'title': 'Безкоштовна доставка', 'text': 'Для замовлень від 1000 грн'},
                    {'icon': 'fa-exchange-alt', 'title': 'Легкий обмін', 'text': '14 днів на повернення'},
                    {'icon': 'fa-shield-alt', 'title': 'Гарантія якості', 'text': 'Офіційна гарантія'},
                    {'icon': 'fa-credit-card', 'title': 'Безпечна оплата', 'text': 'Різні способи оплати'}
                ]
            )

    def test_catalog_all_route(self, client, sample_products, sample_categories):
        with patch('app.web.routes.main.CategoryRepository') as mock_cat_repo, \
                patch('app.web.routes.main.ProductRepository') as mock_prod_repo, \
                patch('app.web.routes.main.render_template') as mock_render:
            # Мокуємо репозиторії
            mock_cat_repo.return_value = MagicMock()
            mock_prod_repo.return_value = MagicMock()

            mock_cat_repo.return_value.find_all_with_counts.return_value = sample_categories
            mock_prod_repo.return_value.find_paginated.return_value = {
                'total': 1,
                'items': sample_products
            }

            response = client.get('/catalog')
            assert response.status_code == 200

            mock_cat_repo.return_value.find_all_with_counts.assert_called_once()
            mock_prod_repo.return_value.find_paginated.assert_called_once_with(
                page=1, per_page=12
            )

            mock_render.assert_called_once_with(
                'catalog.html',
                category=None,
                categories=sample_categories,
                products=sample_products,
                pagination={
                    'page': 1,
                    'per_page': 12,
                    'total': 1,
                    'pages': 1,
                    'items': sample_products,
                    'has_prev': False,
                    'has_next': False,
                    'prev_num': 0,
                    'next_num': 2
                }
            )

    def test_category_page_route(self, client, sample_products, sample_categories):
        with patch('app.web.routes.main.CategoryRepository') as mock_cat_repo, \
                patch('app.web.routes.main.ProductRepository') as mock_prod_repo, \
                patch('app.web.routes.main.render_template') as mock_render:
            # Мокуємо репозиторії
            mock_cat_repo.return_value = MagicMock()
            mock_prod_repo.return_value = MagicMock()

            mock_cat_repo.return_value.find_all_with_counts.return_value = sample_categories
            mock_cat_repo.return_value.find_by_slug.return_value = sample_categories[0]
            mock_prod_repo.return_value.find_paginated.return_value = {
                'total': 1,
                'items': sample_products
            }

            response = client.get('/catalog/cat1')
            assert response.status_code == 200

            mock_cat_repo.return_value.find_by_slug.assert_called_once_with('cat1')
            mock_prod_repo.return_value.find_paginated.assert_called_once_with(
                page=1, per_page=12, category_slug='cat1'
            )

            mock_render.assert_called_once_with(
                'catalog.html',
                category=sample_categories[0],
                categories=sample_categories,
                products=sample_products,
                pagination={
                    'page': 1,
                    'per_page': 12,
                    'total': 1,
                    'pages': 1,
                    'items': sample_products,
                    'has_prev': False,
                    'has_next': False,
                    'prev_num': 0,
                    'next_num': 2
                }
            )

    def test_category_page_not_found(self, client):
        with patch('app.web.routes.main.CategoryRepository') as mock_cat_repo:
            mock_cat_repo.return_value.find_by_slug.return_value = None

            response = client.get('/catalog/nonexistent')
            assert response.status_code == 404
            mock_cat_repo.return_value.find_by_slug.assert_called_once_with('nonexistent')

    def test_pagination_logic(self):
        test_cases = [
            (1, 12, 10, 1),  # 10 items, 1 page
            (1, 10, 25, 3),  # 25 items, 3 pages
            (2, 5, 13, 3),  # 13 items, 3 pages
        ]

        for page, per_page, total, expected_pages in test_cases:
            pages = (total + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < pages

            assert pages == expected_pages
            assert has_prev == (page > 1)
            assert has_next == (page < expected_pages)