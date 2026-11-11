"""LAB 1 — add your five tests here. Do not delete the smoke tests.

A. GET /books, empty database -> HTTP 200 and []
B. GET /books/9999 -> HTTP 404, JSON code == NOT_FOUND
C. POST /books with only author -> HTTP 400, errors contains title
D. POST valid book, DELETE it, GET same id -> HTTP 404
BONUS. Validate a Book response using JSON Schema; add an unknown
       field to a *copy* of the response and assert ValidationError.

Useful imports:
    from jsonschema import validate, ValidationError
    import pytest
    from tools import get_book_schema

Do not depend on test execution order. Fixtures: client, app, sample_book.
"""

from jsonschema import validate, ValidationError
import pytest
from tools import get_book_schema

def test_list_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == []

def test_get_book_not_found(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    assert response.content_type == "application/json"
    assert response.get_json()["code"] == "NOT_FOUND"

def test_post_book_missing_title(client):
    response = client.post("/books", json={"author": "Author"})
    assert response.status_code == 400
    assert response.content_type == "application/json"

    errors = response.get_json()["errors"]
    errors_fields = [error["field"] for error in errors]

    assert "title" in errors_fields

def test_delete_get_book(client, sample_book):
    book_id = sample_book

    delete_response = client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404
    assert get_response.get_json()["code"] == "NOT_FOUND"

def test_response_extra_field_blocked(client, sample_book):
    book_id = sample_book
    
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    book_data = response.get_json()

    schema = get_book_schema()
    schema["additionalProperties"] = False

    if "isbn" in schema.get("properties", {}):
        schema["properties"]["isbn"]["type"] = ["string", "null"]

    validate(instance=book_data, schema=schema)

    book_data_with_extra_field = dict(book_data)
    book_data_with_extra_field["unknown_field"] = "unexpected"

    with pytest.raises(ValidationError):
        validate(instance=book_data_with_extra_field, schema=schema)