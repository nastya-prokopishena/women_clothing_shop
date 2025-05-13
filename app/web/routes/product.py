from flask import render_template, abort
from app.infrastructure.persistence.product_repository import ProductRepository

def init_product_routes(app):
    @app.route('/product/<string:product_id>')
    def product_page(product_id: str):
        repo = ProductRepository()

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

        return render_template(
            'product.html',
            product=product,
            related_products=related
        )
