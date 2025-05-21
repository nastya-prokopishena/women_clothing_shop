from app import create_app
from app.web.routes.main import init_main_routes
from app.web.routes.product import init_product_routes
from app.web.routes.checkout import init_checkout_routes

app = create_app()

# Ініціалізація маршрутів
init_product_routes(app)
init_checkout_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
