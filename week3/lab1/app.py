from flask import Flask, jsonify, request

app = Flask(__name__)

USERS = []
POSTS = []
COMMENTS = []
TAGS = []
FOLLOWING = {}

def find(items, id):
    return next((x for x in items if x["id"] == id), None)

def new_id(items):
    return max((x["id"] for x in items), default=0) + 1

@app.get("/api/v1/posts")
def posts():
    return jsonify(POSTS)

@app.post("/api/v1/posts")
def create_post():
    d = request.get_json() or {}
    if not all(k in d for k in ("title", "content", "author_id")):
        return jsonify({"error": "title, content, author_id are required"}), 400
    post = {
        "id": new_id(POSTS),
        "title": d["title"],
        "content": d["content"],
        "author_id": d["author_id"],
        "tag_ids": d.get("tag_ids", [])
    }
    POSTS.append(post)
    return jsonify(post), 201

@app.get("/api/v1/posts/<int:post_id>")
def post(post_id):
    p = find(POSTS, post_id)
    return jsonify(p) if p else (jsonify({"error": "post not found"}), 404)

@app.delete("/api/v1/posts/<int:post_id>")
def delete_post(post_id):
    p = find(POSTS, post_id)
    if not p:
        return jsonify({"error": "post not found"}), 404
    POSTS.remove(p)
    return jsonify({"message": "post deleted"})

@app.get("/api/v1/posts/<int:post_id>/comments")
def comments(post_id):
    if not find(POSTS, post_id):
        return jsonify({"error": "post not found"}), 404
    return jsonify([c for c in COMMENTS if c["post_id"] == post_id])

@app.post("/api/v1/posts/<int:post_id>/comments")
def create_comment(post_id):
    if not find(POSTS, post_id):
        return jsonify({"error": "post not found"}), 404
    d = request.get_json() or {}
    if not d.get("author_id") or not d.get("content"):
        return jsonify({"error": "author_id and content are required"}), 400
    c = {
        "id": new_id(COMMENTS),
        "post_id": post_id,
        "author_id": d["author_id"],
        "content": d["content"]
    }
    COMMENTS.append(c)
    return jsonify(c), 201

@app.get("/api/v1/users")
def users():
    return jsonify(USERS)

@app.get("/api/v1/users/<int:user_id>")
def user(user_id):
    u = find(USERS, user_id)
    return jsonify(u) if u else (jsonify({"error": "user not found"}), 404)

@app.get("/api/v1/users/<int:user_id>/posts")
def user_posts(user_id):
    if not find(USERS, user_id):
        return jsonify({"error": "user not found"}), 404
    return jsonify([p for p in POSTS if p["author_id"] == user_id])

@app.get("/api/v1/users/<int:user_id>/following")
def following(user_id):
    if not find(USERS, user_id):
        return jsonify({"error": "user not found"}), 404
    return jsonify([find(USERS, i) for i in FOLLOWING.get(user_id, [])])

@app.post("/api/v1/users/<int:user_id>/following/<int:target_id>")
def follow(user_id, target_id):
    if not find(USERS, user_id) or not find(USERS, target_id):
        return jsonify({"error": "user not found"}), 404
    if target_id in FOLLOWING.setdefault(user_id, []):
        return jsonify({"error": "already following"}), 409
    FOLLOWING[user_id].append(target_id)
    return jsonify({"message": "followed"}), 201

@app.delete("/api/v1/users/<int:user_id>/following/<int:target_id>")
def unfollow(user_id, target_id):
    if target_id not in FOLLOWING.get(user_id, []):
        return jsonify({"error": "not following"}), 404
    FOLLOWING[user_id].remove(target_id)
    return jsonify({"message": "unfollowed"})

@app.get("/api/v1/tags")
def tags():
    return jsonify(TAGS)

@app.get("/api/v1/tags/<int:tag_id>")
def tag(tag_id):
    t = find(TAGS, tag_id)
    return jsonify(t) if t else (jsonify({"error": "tag not found"}), 404)

@app.get("/api/v1/tags/<int:tag_id>/posts")
def tag_posts(tag_id):
    if not find(TAGS, tag_id):
        return jsonify({"error": "tag not found"}), 404
    return jsonify([p for p in POSTS if tag_id in p["tag_ids"]])

if __name__ == "__main__":
    app.run(debug=True)
