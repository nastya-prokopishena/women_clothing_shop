from flask import Blueprint, render_template, abort
from app.infrastructure.persistence.product_repository import ProductRepository

product_bp = Blueprint('product', __name__, url_prefix='/products')


@product_bp.route('/<string:product_id>')
def product_page(product_id: str):
    repo = ProductRepository()

    # Отримання продукту
    product = repo.get_product_by_id(product_id)
    if not product:
        abort(404)

    # Отримання схожих продуктів
    related = repo.get_related_products(
        category=product.category,
        exclude_id=product_id
    )

    return render_template(
        'product.html',
        product=product,
        related_products=related
    )