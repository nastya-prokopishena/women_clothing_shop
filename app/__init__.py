from flask import Flask
from .config import Config
from .extensions import mongo


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ініціалізація розширень
    mongo.init_app(app)

    # Ініціалізація роутів
    from .web.routes import main, auth, user, product, cart, order
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(product.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(order.bp)

    return app
