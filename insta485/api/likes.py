import flask
import insta485


@insta485.app.route("/api/v1/", methods=["POST"])
def update_likes():
    """Update likes table + redirect."""

    if not authenticate_user():
        return flask.jsonify({
            "message": "Forbidden",
            "status_code": 403
        }), 403
        
    logname = flask.session["username"]
    postid = flask.request.form["postid"]
    # check if logname has post liked
    connection = insta485.model.get_db()
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
                "url": "/api/v1/likes/<like['likeid']>/"
            }), 200
    # not liked yet, create like
    connection.execute(
        "INSERT INTO likes (owner, postid) VALUES (?, ?)",
        (logname, postid)
    )
    return flask.jsonify({
        "likeid": cur.lastrowid,
        "url": "/api/v1/likes/<cur.lastrowid>/"
    }), 201


