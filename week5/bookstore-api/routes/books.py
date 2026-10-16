from flask import Blueprint, jsonify, request, make_response
from jsonschema import validate, ValidationError
from sqlalchemy import select, func, tuple_
import json
import base64
from models import db, Book, Author, BookAuthor, Category

SCHEMA = json.load(open('schemas/book.json'))
bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

SORT = {
    "id": Book.id,
    "price": Book.price_amount,
    "title": Book.title
}

def parse_book_id(book_id_str):
    if str(book_id_str).startswith("book_"):
        try:
            return int(str(book_id_str).replace("book_", ""))
        except ValueError:
            return None
    try:
        return int(book_id_str)
    except ValueError:
        return None

def parse_sort(raw_sort):
    desc = raw_sort.startswith("-")
    key = raw_sort.lstrip("-")
    if key not in SORT:
        return None, None, False
    
    col = SORT[key]
    cols = [
        col.desc() if desc else col.asc(),
        Book.id.desc() if desc else Book.id.asc()
    ]
    return col, cols, desc

def decode_cursor(cursor_str):
    try:
        pad = "=" * (-len(cursor_str) % 4)
        return json.loads(base64.urlsafe_b64decode(cursor_str + pad))
    except Exception:
        return None

def encode_cursor(sort_str, val, last_id):
    payload = {"s": sort_str, "v": val, "i": last_id}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")

@bp.get("")
def list_books():
    strategy = request.args.get("strategy", "offset").lower()
    genre = request.args.get("genre")
    sort_raw = request.args.get("sort", "-id")
    limit = min(request.args.get("limit", 20, type=int), 100)

    p_col, sort_cols, is_desc = parse_sort(sort_raw)
    if p_col is None:
        return jsonify({"error": "bad_request", "message": f"Thẻ sort '{sort_raw}' không hợp lệ"}), 400

    q = select(Book).order_by(*sort_cols)
    if genre:
        q = q.join(Category).filter(Category.slug == genre.lower())

    # Offset-based
    if strategy == "offset":
        offset = max(request.args.get("offset", 0, type=int), 0)
        
        count_q = select(func.count(Book.id))
        if genre:
            count_q = count_q.join(Category).filter(Category.slug == genre.lower())
        total = db.session.scalar(count_q) or 0

        rows = db.session.scalars(q.offset(offset).limit(limit)).all()
        return jsonify({
            "data": [b.to_dict() for b in rows],
            "pagination": {
                "strategy": "offset",
                "offset": offset,
                "limit": limit,
                "total": total,
                "has_next": (offset + limit) < total
            }
        }), 200

    # Cursor-based
    elif strategy == "cursor":
        raw_cursor = request.args.get("cursor")
        if raw_cursor:
            c = decode_cursor(raw_cursor)
            if not c or c.get("s") != sort_raw:
                return jsonify({"error": "bad_request", "message": "Cursor không hợp lệ hoặc sai cấu hình sort"}), 400
            
            v, i = c["v"], c["i"]
            op = "<" if is_desc else ">"
            q = q.filter(tuple_(p_col, Book.id).op(op)((v, i)))

        rows = db.session.scalars(q.limit(limit + 1)).all()
        has_more = len(rows) > limit
        result_rows = rows[:limit]

        next_cursor = None
        if result_rows and has_more:
            last = result_rows[-1]
            val = getattr(last, p_col.key)
            next_cursor = encode_cursor(sort_raw, val, last.id)

        return jsonify({
            "data": [b.to_dict() for b in result_rows],
            "pagination": {
                "strategy": "cursor",
                "limit": limit,
                "next_cursor": next_cursor,
                "has_more": has_more
            }
        }), 200

    return jsonify({"error": "bad_request", "message": "Strategy phải là 'offset' hoặc 'cursor'"}), 400

@bp.get("/<book_id>")
def get_book(book_id):
    real_id = parse_book_id(book_id)
    if real_id is None:
        return jsonify({"error": "invalid_id", "message": "ID không đúng định dạng"}), 400

    book = db.session.get(Book, real_id)
    if not book:
        return jsonify({"error": "not_found", "message": f"Không tìm thấy sách {book_id}"}), 404

    return jsonify(book.to_dict()), 200

@bp.post("")
def create_book():
    if not request.is_json:
        return jsonify({"error": "unsupported_media_type", "message": "Yêu cầu Content-Type: application/json"}), 415

    payload = request.get_json(silent=True) or {}

    payload_to_validate = dict(payload)
    if "id" not in payload_to_validate:
        payload_to_validate["id"] = "book_0"

    try:
        validate(instance=payload_to_validate, schema=SCHEMA)
    except ValidationError as e:
        return jsonify({
            "error": "validation_failed",
            "field": list(e.path),
            "message": e.message
        }), 400

    price_obj = payload.get("price", {})
    amount = price_obj.get("amount", 0)
    currency = price_obj.get("currency", "VND")

    new_book = Book(
        title=payload["title"],
        isbn=payload.get("isbn"),
        price_amount=amount,
        price_currency=currency
    )
    db.session.add(new_book)
    db.session.flush()

    authors_data = payload.get("authors", [])
    for auth_item in authors_data:
        auth_id = auth_item.get("id")
        author = None
        if auth_id:
            author = db.session.get(Author, auth_id)
        if not author:
            author = Author(name=auth_item.get("name", "Unknown"))
            db.session.add(author)
            db.session.flush()
        
        link = BookAuthor(book_id=new_book.id, author_id=author.id, role=auth_item.get("role", "co"))
        db.session.add(link)

    db.session.commit()

    resp_data = new_book.to_dict()
    resp = make_response(jsonify(resp_data), 201)
    resp.headers["Location"] = f"/api/v1/books/{resp_data['id']}"
    return resp

@bp.delete("/<book_id>")
def delete_book(book_id):
    real_id = parse_book_id(book_id)
    if real_id is None:
        return jsonify({"error": "invalid_id", "message": "ID không hợp lệ"}), 400

    book = db.session.get(Book, real_id)
    if not book:
        return jsonify({"error": "not_found", "message": "Không tìm thấy sách"}), 404

    db.session.delete(book)
    db.session.commit()
    return "", 204