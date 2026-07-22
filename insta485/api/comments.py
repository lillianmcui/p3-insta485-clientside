"""REST API for comments."""
import flask
import insta485
from insta485.api.routes import require_auth


@insta485.app.route("/api/v1/comments/", methods=["POST"])
def post_comment():
    """Add a like to table."""
    logname, error = require_auth()
    if error:
        return error

    postid = flask.request.args["postid"]

    connection = insta485.model.get_db()
    cursor = connection.execute(
        "SELECT postid FROM posts WHERE postid = ?",
        (postid, )
    )
    if not cursor.fetchone():
        return flask.jsonify({
            "message": "Post not found"
        }), 404

    data = flask.request.get_json()
    if data is None or "text" not in data:
        flask.abort(400)
    text = data["text"]

    cur = connection.execute(
        "INSERT INTO comments (owner, text, postid) VALUES (?, ?, ?)",
        (logname, text, postid)
    )
    commentid = cur.lastrowid
    return flask.jsonify({
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": f"/users/{logname}/",
        "text": text,
        "url": f"/api/v1/comments/{commentid}/"
    }), 201


@insta485.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Delete a comment from the table."""
    logname, error = require_auth()
    if error:
        return error

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT commentid FROM comments WHERE commentid= ?",
        (commentid,)
    )
    if not cur.fetchone():
        return flask.jsonify({
            "message": "Comment not found"
        }), 404

    # check if they own the comment
    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ?",
        (commentid,)
    )
    comment_owner = cur.fetchone()
    if comment_owner["owner"] != logname:
        return flask.jsonify({
            "message": "Comment not owned by user"
        }), 403

    cur = connection.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid,)
    )
    return "", 204
