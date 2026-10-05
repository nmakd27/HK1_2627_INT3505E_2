from flask import Flask, request, jsonify
import base64
import json

app = Flask(__name__)

ORDERS = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 500},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 300},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 700},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 200},
    {"id": 5, "customer_id": 102, "status": "paid", "total": 900},
    {"id": 6, "customer_id": 101, "status": "paid", "total": 400},
]


def encode_cursor(order_id):
    data = json.dumps({"id": order_id}).encode()
    return base64.urlsafe_b64encode(data).decode()


def decode_cursor(cursor):
    try:
        data = base64.urlsafe_b64decode(cursor).decode()
        return json.loads(data)["id"]
    except Exception:
        return None


@app.get("/orders")
def get_orders():

    try:
        limit = int(request.args.get("limit", 10))
        if limit <= 0:
            return jsonify({"error": "limit must be positive"}), 400
    except ValueError:
        return jsonify({"error": "invalid limit"}), 400

    cursor_string = request.args.get("cursor")

    if cursor_string:
        cursor = decode_cursor(cursor_string)

        if cursor is None:
            return jsonify({"error": "invalid cursor"}), 400
    else:
        cursor = 0

    orders = ORDERS

    status = request.args.get("status")
    if status:
        orders = [o for o in orders if o["status"] == status]

    customer_id = request.args.get("customer_id")
    if customer_id:
        try:
            customer_id = int(customer_id)
        except ValueError:
            return jsonify({"error": "invalid customer_id"}), 400

        orders = [
            o for o in orders
            if o["customer_id"] == customer_id
        ]

    orders = [
        o for o in orders
        if o["id"] > cursor
    ]

    orders.sort(key=lambda o: o["id"])

    page = orders[:limit + 1]

    has_next = len(page) > limit

    page = page[:limit]

    fields = request.args.get("fields")

    if fields:
        fields = fields.split(",")

        page = [
            {
                field: order[field]
                for field in fields
                if field in order
            }
            for order in page
        ]

    next_cursor = None

    if has_next:
        last_order_id = orders[limit - 1]["id"]
        next_cursor = encode_cursor(last_order_id)

    return jsonify({
        "data": page,
        "next_cursor": next_cursor
    })

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )