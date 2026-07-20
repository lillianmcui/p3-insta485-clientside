"""
Insta485 likes view.

URLS include:

/likes/
/comments/
/posts/
"""

import pathlib
import flask
import insta485
from insta485.views.account import save_uploaded_image

LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route("/posts/", methods=["POST"])
def update_post():
    """Create or delete posts + redirect."""
    operation = flask.request.form["operation"]
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session["username"]
    target = flask.request.args.get('target', f'/users/{logname}/')
    connection = insta485.model.get_db()
    if operation == "create":
        # Unpack flask object
        fileobj = flask.request.files["file"]
        if not fileobj:
            flask.abort(400)

        fileobj = flask.request.files["file"]
        uuid_basename = save_uploaded_image(fileobj)

        # Insert post info into db
        connection.execute(
            "INSERT INTO posts (filename, owner) VALUES (?, ?)",
            (uuid_basename, logname)
        )

    if operation == "delete":
        postid = flask.request.form["postid"]
        # check if logname owns post
        cur = connection.execute(
            "SELECT filename, owner FROM posts WHERE postid = ?",
            (postid,)
        )
        post = cur.fetchone()
        if post["owner"] != logname:
            flask.abort(403)

        # delete file from filesytem
        path = (pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])
                / post["filename"])
        path.unlink()

        # delete post info
        connection.execute(
            "DELETE FROM posts WHERE postid = ?",
            (postid,)
        )
    return flask.redirect(target)


@insta485.app.route("/likes/", methods=["POST"])
def update_likes():
    """Update likes table + redirect."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session["username"]
    operation = flask.request.form["operation"]
    postid = flask.request.form["postid"]
    # check if logname has post liked
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT COUNT(*) AS count FROM likes "
        "WHERE owner = ? AND postid = ? ",
        (logname, postid)
    )
    already_liked = cur.fetchone()["count"] > 0

    # user trying to like
    if operation == "like":
        if already_liked:
            flask.abort(409)
        connection.execute(
            "INSERT INTO likes (owner, postid) VALUES (?, ?)",
            (logname, postid)
        )
    # user trying to unlike
    elif operation == "unlike":
        if not already_liked:
            flask.abort(409)
        connection.execute(
            "DELETE FROM likes WHERE owner = ? and postid = ?",
            (logname, postid)
        )

    target = flask.request.args.get('target', '/')
    return flask.redirect(target)
    # PITFALL: Do not call render_template()


@insta485.app.route('/comments/', methods=["POST"])
def show_comments():
    """Update comments."""
    operation = flask.request.form["operation"]
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session["username"]
    connection = insta485.model.get_db()

    if operation == "create":
        postid = flask.request.form["postid"]
        text = flask.request.form["text"]
        if text == "":
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)",
            (logname, postid, text)
        )
    elif operation == "delete":
        commentid = flask.request.form["commentid"]
        cur = connection.execute(
            "SELECT owner FROM comments WHERE commentid = ?",
            (commentid,)
        )
        comment = cur.fetchone()
        if comment is None or comment["owner"] != logname:
            flask.abort(403)
        connection.execute(
            "DELETE FROM comments WHERE commentid = ?",
            (commentid,)
        )

    target = flask.request.args.get("target")
    if not target:
        target = flask.url_for("show_index")
    return flask.redirect(target)
