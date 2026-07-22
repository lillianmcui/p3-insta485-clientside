"""REST API for likes."""
import flask
import insta485
from insta485.api.routes import require_auth


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def api_update_likes():
    """Update likes table."""
    logname, error = require_auth()
    if error:
        return error
    # check if logname has post liked
    db_connection = insta485.model.get_db()
    postid = flask.request.args.get("postid", type=int)
    cur = db_connection.execute(
        "SELECT postid FROM posts WHERE postid = ?",
        (postid, )
    )
    if not cur.fetchone():
        return flask.jsonify({
            "message": "Post not found"
        }), 404
    cur = db_connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid)
    )
    like = cur.fetchone()
    # like already exists
    if like:
        return flask.jsonify(
            {
                "likeid": like['likeid'],
                "url": f"/api/v1/likes/{like['likeid']}/"
            }), 200
    # not liked yet, create like
    cur = db_connection.execute(
        "INSERT INTO likes (owner, postid) VALUES (?, ?)",
        (logname, postid)
    )
    likeid = cur.lastrowid
    return flask.jsonify({
        "likeid": likeid,
        "url": f"/api/v1/likes/{likeid}/"
    }), 201


@insta485.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def api_delete_likes(likeid):
    """Delete from likes table."""
    logname, error = require_auth()
    if error:
        return error

    # check if like exists
    db_connection = insta485.model.get_db()
    cur = db_connection.execute(
        "SELECT likeid FROM likes WHERE likeid = ?",
        (likeid, )
    )
    if not cur.fetchone():
        return flask.jsonify({
            "message": "Like not found"
        }), 404

    # check if logname owns like
    cur = db_connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? AND likeid = ?",
        (logname, likeid)
    )
    liked_by_owner = cur.fetchone()

    # not liked by owner
    if not liked_by_owner:
        return flask.jsonify(
            {
                "message": "Like not owned by user"
            }), 403

    # liked by owner so delete
    db_connection.execute(
        "DELETE FROM likes WHERE likeid = ?",
        (likeid, )
    )
    return "", 204
