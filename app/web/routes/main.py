from flask import render_template, abort, request
from app.application.services.home_page_service import HomePageService
from app.infrastructure.persistence.category_repository import CategoryRepository
from app.infrastructure.persistence.product_repository import ProductRepository


def init_main_routes(app):
    @app.route('/', endpoint='home')
    def home_page():
        service = HomePageService()
        data = service.get_home_page_data()

        benefits = [
            {'icon': 'fa-truck', 'title': 'Безкоштовна доставка', 'text': 'Для замовлень від 1000 грн'},
            {'icon': 'fa-exchange-alt', 'title': 'Легкий обмін', 'text': '14 днів на повернення'},
            {'icon': 'fa-shield-alt', 'title': 'Гарантія якості', 'text': 'Офіційна гарантія'},
            {'icon': 'fa-credit-card', 'title': 'Безпечна оплата', 'text': 'Різні способи оплати'}
        ]

        return render_template('index.html',
                               featured_products=data['featured_products'],
                               new_arrivals=data['new_arrivals'],
                               categories=data['featured_categories'],
                               reviews=data['reviews'],
                               benefits=benefits,
                               )

    @app.route('/catalog', endpoint='catalog_all')
    def catalog_all():
        category_repo = CategoryRepository()
        product_repo = ProductRepository()
        all_categories = category_repo.find_all_with_counts()

        # Пагінація
        page = request.args.get('page', 1, type=int)
        per_page = 12

        products_data = product_repo.find_paginated(page=page, per_page=per_page)

        # Створюємо об'єкт пагінації
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': products_data['total'],
            'pages': (products_data['total'] + per_page - 1) // per_page,
            'items': products_data['items'],
            'has_prev': page > 1,
            'has_next': page < (products_data['total'] + per_page - 1) // per_page,
            'prev_num': page - 1,
            'next_num': page + 1
        }

        return render_template('catalog.html',
                               category=None,
                               categories=all_categories,
                               products=products_data['items'],
                               pagination=pagination)

    @app.route('/catalog/<slug>', endpoint='category')
    def category_page(slug):
        category_repo = CategoryRepository()
        product_repo = ProductRepository()
        all_categories = category_repo.find_all_with_counts()

        category = category_repo.find_by_slug(slug)
        if not category:
            abort(404)

        # Пагінація
        page = request.args.get('page', 1, type=int)
        per_page = 12

        products_data = product_repo.find_paginated(
            page=page,
            per_page=per_page,
            category_slug=slug
        )

        # Створюємо об'єкт пагінації
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': products_data['total'],
            'pages': (products_data['total'] + per_page - 1) // per_page,
            'items': products_data['items'],
            'has_prev': page > 1,
            'has_next': page < (products_data['total'] + per_page - 1) // per_page,
            'prev_num': page - 1,
            'next_num': page + 1
        }

        return render_template('catalog.html',
                               category=category,
                               categories=all_categories,
                               products=products_data['items'],
                               pagination=pagination)