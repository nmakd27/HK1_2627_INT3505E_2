from flask import Flask, jsonify, request, make_response
from flask_smorest import Api, Blueprint
from flask.views import MethodView

app = Flask(__name__)

app.config["API_TITLE"] = "Books API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
)

api = Api(app)

blp = Blueprint("books", "books", url_prefix="/books", description="API quản lý sách")

BOOKS = []
_next_id = 1

@blp.route("/")
class BookList(MethodView):

    def get(self):
        return jsonify({
            "data": BOOKS,
            "total": len(BOOKS)
        }), 200
    
    def post(self):
        global _next_id

        if not request.is_json:
            return jsonify(error="expected JSON"), 415

        p = request.get_json()

        t = (p.get("title") or "").strip()
        a = (p.get("author") or "").strip()

        if not t or not a:
            return jsonify(error="title and author required"), 422

        book = {
            "id": _next_id,
            "title": t,
            "author": a
        }

        BOOKS.append(book)
        _next_id += 1

        return jsonify(book), 201

api.register_blueprint(blp)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)