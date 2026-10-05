from flask import Flask, jsonify, request
import hashlib
import json

app = Flask(__name__)

BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert Martin"},
    {"id": 2, "title": "Clean Arch", "author": "Robert Martin"},
    {"id": 3, "title": "Animal Farm", "author": "George Orwell"},
]


def create_etag(book):
    data = json.dumps(book, sort_keys=True)
    return hashlib.md5(data.encode()).hexdigest()


@app.route("/books/<int:id>", methods=["GET"])
def get_book(id):
    book = next((book for book in BOOKS if book["id"] == id), None)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    etag = create_etag(book)

    if_none_match = request.headers.get("If-None-Match")

    if if_none_match == etag:
        return "", 304

    response = jsonify(book)
    response.headers["ETag"] = etag

    return response


if __name__ == "__main__":
    app.run(debug=True)