from flask import Flask, jsonify, request, make_response
import sqlite3

app = Flask(__name__)
DB = "books.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()

@app.get("/books")
def list_books():
    conn = get_db()

    rows = conn.execute(
        "SELECT id, title, author FROM books"
    ).fetchall()

    conn.close()

    books = [dict(row) for row in rows]

    return jsonify({
        "data": books,
        "total": len(books)
    }), 200

@app.get("/books/<int:book_id>")
def get_book(book_id):
    conn = get_db()

    row = conn.execute(
        "SELECT id, title, author FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify(error="book not found"), 404

    return jsonify(dict(row)), 200

@app.post("/books")
def create_book():
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    
    p = request.get_json(silent=True) or {}
    title = (p.get("title") or "").strip()
    author = (p.get("author") or "").strip()

    if not title or not author:
        return jsonify(
            error="title and author required"
        ), 422

    conn = get_db()
    
    cursor = conn.execute(
        """
        INSERT INTO books (title, author)
        VALUES (?, ?)
        """,
        (title, author)
    )

    conn.commit()

    book_id = cursor.lastrowid

    row = conn.execute(
        "SELECT id, title, author FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    conn.close()
    
    book = dict(row)

    response = make_response(jsonify(book), 201)
    response.headers["Location"] = f"/books/{book_id}"
    return response

@app.get("/orders/<int:oid>")
def get_order(oid):
    conn = get_db()

    row = conn.execute(
        "SELECT id, customer, total FROM orders WHERE id = ?",
        (oid,)
    ).fetchone()

    conn.close()

    if row is None:
        return jsonify(error="order not found"), 404

    return jsonify(dict(row)), 200

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000,debug=True)