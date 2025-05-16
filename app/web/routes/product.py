from flask import render_template, abort, request, redirect, url_for
from app.infrastructure.persistence.product_repository import ProductRepository
from app.infrastructure.persistence.review_repository import ReviewRepository


def init_product_routes(app):
    @app.route('/product/<string:product_id>')
    def product_page(product_id: str):
        repo = ProductRepository()
        review_repo = ReviewRepository()

        # Отримання продукту
        product = repo.get_product_by_id(product_id)
        if not product:
            abort(404)

        # Отримання схожих продуктів
        category = product.category_slug if product.category_slug else None
        related = repo.get_related_products(
            category_slug=category,
            exclude_id=product.product_id
        )

        # Отримання коментарів
        comments = review_repo.get_reviews_by_product_id(product_id)

        # Розрахунок середньої оцінки (НОВИЙ КОД)
        if comments:
            total_rating = sum(comment.rating for comment in comments)
            average_rating = total_rating / len(comments)
        else:
            average_rating = None

        return render_template(
            'product.html',
            product=product,
            related_products=related,
            comments=comments,
            average_rating=average_rating  # Передаємо середню оцінку в шаблон
        )

    @app.route('/product/<string:product_id>/add_comment', methods=['POST'])
    def add_comment(product_id: str):
        review_repo = ReviewRepository()
        comment_text = request.form.get('comment', '').strip()
        rating = int(request.form.get('rating', 0))

        # Валідація
        if not comment_text or rating < 1 or rating > 5:
            return "Будь ласка, заповніть всі обов'язкові поля", 400

        review_repo.add_review(
            product_id=product_id,
            text=comment_text,
            author="Гість",
            rating=rating
        )

        return redirect(url_for('product_page', product_id=product_id))