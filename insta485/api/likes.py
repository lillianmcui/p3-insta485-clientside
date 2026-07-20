import flask
import insta485


from insta485.api.routes import authenticate_user


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def api_update_likes():
    """Update likes table + redirect."""

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


