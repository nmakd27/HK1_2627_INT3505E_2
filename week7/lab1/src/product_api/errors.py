from flask import app, jsonify
from werkzeug.exceptions import HTTPException

class ApiError(Exception):
    status_code = 500
    code = "internal_error"
    def __init__(self, code=None, message="", status=None):
        super().__init__(message)
        if code: self.code = code
        if status: self.status_code = status
        self.message = message

class NotFound(ApiError):
    status_code = 404; code = "not_found"

class Conflict(ApiError):
    status_code = 409; code = "conflict"

class OutOfStock(ApiError):
    status_code = 409; code = "out_of_stock"

def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _on_api(err):
        return jsonify({"code": err.code, "message": err.message}), err.status_code
    @app.errorhandler(HTTPException)
    def _on_http(err):
        return jsonify({"code": err.name.lower().replace(" ", "_"), "message": err.description}), err.code
    @app.errorhandler(Exception)
    def _on_err(err):
        app.logger.exception("unhandled")
        return jsonify({"code": "internal_error", "message": "Internal server error"}), 500