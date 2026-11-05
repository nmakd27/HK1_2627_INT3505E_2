from sqlalchemy import event
from src.product_api.models.product import Product
from src.product_api.models.order import Order, OrderItem
from src.product_api.extensions import db

def test_create_product(client):
    payload = {
        "sku": "IPHONE-15",
        "name": "iPhone 15 Pro",
        "price_cents": 99900,
        "qty_in_stock": 10
    }
    res = client.post("/api/v1/products", json=payload)
    assert res.status_code == 201
    assert res.json["sku"] == "IPHONE-15"

    res_conflict = client.post("/api/v1/products", json=payload)
    assert res_conflict.status_code == 409
    assert res_conflict.json["code"] == "conflict"

def test_get_orders_eager_loading_avoids_n_plus_one(client, app):
    with app.app_context():
        p1 = Product(sku="PROD-1", name="Product 1", price_cents=1000, qty_in_stock=100)
        p2 = Product(sku="PROD-2", name="Product 2", price_cents=2000, qty_in_stock=100)
        db.session.add_all([p1, p2])
        db.session.commit()

        o1 = Order(customer_name="Alice")
        o2 = Order(customer_name="Bob")
        db.session.add_all([o1, o2])
        db.session.flush()

        db.session.add_all([
            OrderItem(order_id=o1.id, product_id=p1.id, quantity=1, unit_price_cents=1000),
            OrderItem(order_id=o1.id, product_id=p2.id, quantity=2, unit_price_cents=2000),
            OrderItem(order_id=o2.id, product_id=p1.id, quantity=3, unit_price_cents=1000),
        ])
        db.session.commit()

    queries = []
    def count_queries(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", count_queries)
        res = client.get("/api/v1/orders")
        event.remove(db.engine, "before_cursor_execute", count_queries)

    assert res.status_code == 200
    assert len(res.json) == 2
    assert len(queries) <= 2