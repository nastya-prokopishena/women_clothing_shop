from app.domain.models.product import Product
from decimal import Decimal


class ProductFactory:
    @staticmethod
    def create_product(product_type: str, **kwargs) -> Product:
        """Фабричний метод для створення продуктів"""
        if product_type == "clothing":
            return Product(
                id=kwargs['id'],
                name=kwargs['name'],
                description=kwargs.get('description', ''),
                price=Decimal(kwargs['price']),
                sizes=kwargs.get('sizes', []),
                colors=kwargs.get('colors', []),
                images=kwargs.get('images', []),
                category="Clothing",
                sku=kwargs['sku']
            )
        elif product_type == "accessory":
            return Product(
                id=kwargs['id'],
                name=kwargs['name'],
                description=kwargs.get('description', ''),
                price=Decimal(kwargs['price']),
                sizes=['One Size'],
                colors=kwargs.get('colors', []),
                images=kwargs.get('images', []),
                category="Accessories",
                sku=kwargs['sku']
            )
        else:
            raise ValueError(f"Unknown product type: {product_type}")