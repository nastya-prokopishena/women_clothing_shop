from flask import Blueprint, request, jsonify, session
from app.application.services.order_service import OrderService

order_bp = Blueprint('order', __name__, url_prefix='/orders')
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

_order_service = None

def get_order_service():
    global _order_service
    if _order_service is None:
        _order_service = OrderService()
    return _order_service


@order_bp.route('/create', methods=['POST'])
def create_order():
    data = request.json

    user_id = data.get('user_id')
    shipping_address = data.get('shipping_address')
    payment_method = data.get('payment_method')
    cart_items = data.get('cart_items')
    subtotal = data.get('subtotal')
    delivery_price = data.get('delivery_price')
    total_order_amount = data.get('total_order_amount')

    success, message, order_id = get_order_service().create_order(
        user_id=user_id,
        shipping_address=shipping_address,
        payment_method=payment_method,
        cart_items=cart_items,
        subtotal=subtotal,
        delivery_price=delivery_price,
        total_order_amount=total_order_amount
    )

    if success:
        return jsonify({'success': True, 'message': message, 'order_id': order_id}), 201
    else:
        return jsonify({'success': False, 'message': message}), 400


@order_bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    order = get_order_service().get_order_details_for_confirmation(order_id)
    if not order:
        return jsonify({'success': False, 'message': 'Замовлення не знайдено'}), 404

    order_data = {
        '_id': str(order._id),
        'user_id': order.user_id,
        'items': [{
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': item.price,
            'size': item.size,
            'color': item.color,
        } for item in order.items],
        'total_amount': order.total_amount,
        'shipping_address': order.shipping_address,
        'payment_method': order.payment_method,
        'payment_status': order.payment_status,
        'delivery_method': order.delivery_method,
        'delivery_cost': order.delivery_cost,
        'status': order.status,
        'tracking_number': order.tracking_number,
        'notes': order.notes,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'updated_at': order.updated_at.isoformat() if order.updated_at else None,
    }

    return jsonify({'success': True, 'order': order_data}), 200


@profile_bp.route('/orders', methods=['GET'])
def get_user_orders():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Користувач не авторизований'}), 401

    orders = get_order_service().get_orders_by_user_id(user_id)
    orders_data = []
    for order in orders:
        orders_data.append({
            'order_id': str(order._id),
            'total_amount': order.total_amount,
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None,
        })

    return jsonify({'success': True, 'orders': orders_data}), 200
