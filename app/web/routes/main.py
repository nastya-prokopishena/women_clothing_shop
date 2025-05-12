from flask import render_template
from app.application.services.home_page_service import HomePageService


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
                               reviews=data['recent_reviews'],
                               benefits=benefits)
