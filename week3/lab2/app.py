from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
import logging

app = Flask(__name__)

class ProblemError(Exception):
    def __init__(self, status, title, detail):
        self.status = status
        self.title = title
        self.detail = detail

@app.errorhandler(ProblemError)
def handle_problem(e):
    return jsonify({
        "type": "about:blank",
        "title": e.title,
        "detail": e.detail,
        "status": e.status,
        "instance": request.path
    }), e.status, {"Content-Type": "application/problem+json"}

@app.errorhandler(HTTPException)
def handle_http(e):
    return jsonify({
        "type": "about:blank",
        "title": e.name,
        "detail": e.description,
        "status": e.code,
        "instance": request.path
    }), e.code, {"Content-Type": "application/problem+json"}

@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Unhandled exception")
    return jsonify({
        "type": "about:blank",
        "title": "Internal Server Error",
        "detail": "An unexpected error occurred.",
        "status": 500,
        "instance": request.path
    }), 500, {"Content-Type": "application/problem+json"}

@app.route("/resources/<int:id>")
def get_resource(id):
    if id != 1:
        raise ProblemError(404, "Not Found", "Resource not found")
    return {"id": 1, "name": "Example"}

if __name__ == "__main__":
    app.run(debug=False)