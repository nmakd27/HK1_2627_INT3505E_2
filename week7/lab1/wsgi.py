# wsgi.py — entry point
from src.product_api.factory import create_app
from src.product_api.extensions import db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)