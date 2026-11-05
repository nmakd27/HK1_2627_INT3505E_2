import pytest
from src.product_api.factory import create_app
from src.product_api.config import TestConfig
from src.product_api.extensions import db

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()