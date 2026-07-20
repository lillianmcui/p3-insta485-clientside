"""REST API for likes."""
import flask
import insta485
from insta485.api.routes import authenticate_user

@insta485.app.route("/api/v1/likes/", methods=["POST"])
def api_update_likes():
    """Update likes table."""
    logname = authenticate_user()
    if not logname:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    postid = flask.request.args["postid"]
    # check if logname has post liked
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT postid FROM posts WHERE postid = ?",
        (postid, )
    )
    if not cur.fetchone():
        return flask.jsonify({
            "message": "Post not found"
        }), 404
    cur = connection.execute(
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
    connection.execute(
        "INSERT INTO likes (owner, postid) VALUES (?, ?)",
        (logname, postid)
    )
    return flask.jsonify({
        "likeid": cur.lastrowid,
        "url": f"/api/v1/likes/{cur.lastrowid}/"
    }), 201


@insta485.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def api_delete_likes(likeid):
    """Delete from likes table."""
    logname = authenticate_user()
    if not logname:
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403

    # check if like exists
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT likeid FROM likes WHERE likeid = ?",
        (likeid, )
    )
    if not cur.fetchone():
        return flask.jsonify({
            "message": "Like not found"
        }), 404

    # check if logname owns like
    cur = connection.execute(
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
    connection.execute(
        "DELETE FROM likes WHERE likeid = ?",
        (likeid, )
    )
    return "", 204