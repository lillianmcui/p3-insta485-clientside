"""REST API for comments."""
import flask
import insta485
from insta485.api.routes import authenticate_user

@insta485.app.route("/api/v1/comments/", methods=["POST"])
def post_comment():
    """Add a like to table."""
    logname = authenticate_user()
    if not logname:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    postid = flask.request.args["postid"]

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT postid FROM posts WHERE postid = ?",
        (postid, )
    )
    if not cur.fetchone():
        return flask.jsonify({
            "message": "Post not found"
        }), 404
    
    data = flask.request.get_json()
    if data is None or "text" not in data:
        flask.abort(400)
    text = data["text"]

    connection.execute(
        """ 
        INSERT INTO comments (owner, text, postid) VALUES (?, ?, ?)
        """,
        (logname, text, postid)
    )
    commentid = connection.execute("SELECT last_insert_rowid()").fetchone()
    return flask.jsonify({
        "commentid": commentid,
        "url": f"/api/v1/comments/{commentid}/"
    }), 201

