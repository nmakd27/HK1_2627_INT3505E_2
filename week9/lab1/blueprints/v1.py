from flask import Blueprint, jsonify, make_response
from .users_data import get_user

bp = Blueprint("v1", __name__, url_prefix="/users")
 
@bp.route("/<int:uid>")
def get(uid):
    u = get_user(uid)
    if not u: return {"error": "nf"}, 404

    resp = make_response(jsonify({
        "id": uid,
        "full_name": f"{u['first_name']} {u['last_name']}",
        "email": u["email"]
    }), 200)
    
    resp.headers["Sunset"] = "Thu, 31 Dec 2026 23:59:59 GMT"
    resp.headers["Deprecation"] = "true"
    resp.headers["Link"] = '</api/v2/users>; rel="successor-version"'
    return resp