from flask import Blueprint, jsonify, request
from sqlalchemy.orm import selectinload
from ..extensions import db
from ..models.order import Order, OrderItem
from ..models.product import Product
from ..errors import NotFound, OutOfStock
from ..schemas.order import OrderIn, OrderOut

orders_bp = Blueprint("orders", __name__, url_prefix="/api/v1/orders")

@orders_bp.get("")
def list_orders():
    # Sử dụng selectinload để tránh lỗi N+1 Query
    stmt = db.select(Order).options(selectinload(Order.items))
    orders = db.session.execute(stmt).scalars().all()
    return jsonify([OrderOut().dump(o) for o in orders]), 200

@orders_bp.post("")
def create_order():
    data = OrderIn().load(request.json or {})
    order = Order(customer_name=data["customer_name"])
    db.session.add(order)

    for item_data in data["items"]:
        prod = db.session.get(Product, item_data["product_id"])
        if not prod or prod.archived:
            db.session.rollback()
            raise NotFound(message=f"Product id {item_data['product_id']} does not exist")
        if prod.qty_in_stock < item_data["quantity"]:
            db.session.rollback()
            raise OutOfStock(message=f"Product {prod.name} does not have enough stock")

        prod.qty_in_stock -= item_data["quantity"]
        order_item = OrderItem(
            order=order,
            product_id=prod.id,
            quantity=item_data["quantity"],
            unit_price_cents=prod.price_cents
        )
        db.session.add(order_item)

    db.session.commit()
    return jsonify(OrderOut().dump(order)), 201