"""
Insta485 User View.

URLS Include:

/users/<username>
/users/followers/
/users/following/
/following/
"""

import flask
import insta485


@insta485.app.route('/users/<username>/following/')
def show_following(username):
    """Display / following."""
    # connect to db
    connection = insta485.model.get_db()
    # check if user logged in
    if "username" not in flask.session:
        # redirect to login
        return flask.redirect(flask.url_for("show_login"))
    # store username
    logname = flask.session["username"]
    # query db
    cursor = connection.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,)
    )

    if not cursor.fetchone():
        flask.abort(404)
    cursor = connection.execute(
        """
        SELECT
            users.username,
            users.filename,
            (SELECT COUNT(*) FROM following WHERE followee = users.username
                AND follower = ?) AS follows_user
        FROM following
        JOIN users ON followee = users.username
        WHERE following.follower = ?
        """,
        (logname, username)
    )
    followers = cursor.fetchall()
    followers_list = []
    for follower in followers:
        followers_list.append({
            "username": follower["username"],
            "user_img_url": flask.url_for('download_file',
                                          filename=follower["filename"]),
            "logname_follows_username": follower["follows_user"] > 0
        })
    context = {
        "logname": logname,
        "username": username,
        "following": followers_list
    }

    return flask.render_template("following.html", **context)


@insta485.app.route('/users/<username>/followers/')
def show_followers(username):
    """Display / followers."""
    db_connection = insta485.model.get_db()
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logged_in_user = flask.session["username"]

    cur = db_connection.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,)
    )

    if not cur.fetchone():
        flask.abort(404)
    cur = db_connection.execute(
        """
        SELECT
            users.username,
            users.filename,
            (SELECT COUNT(*) FROM following WHERE follower = ?
                AND followee = users.username) AS follows_user
        FROM following
        JOIN users ON following.follower = users.username
        WHERE following.followee = ?
        """,
        (logged_in_user, username)
    )
    followers = cur.fetchall()
    followers_list = []
    for follower in followers:
        followers_list.append({
            "username": follower["username"],
            "user_img_url": flask.url_for('download_file',
                                          filename=follower["filename"]),
            "logname_follows_username": follower["follows_user"] > 0
        })
    context = {
        "logname": logged_in_user,
        "username": username,
        "followers": followers_list
    }
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<username>/')
def show_user(username):
    """Display / user."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    conn = insta485.model.get_db()
    logname = flask.session["username"]

    # get user info
    cur = conn.execute(
        """
        SELECT fullname,
               (SELECT COUNT(*) FROM posts WHERE owner = users.username)
                    AS total_posts,
               (SELECT COUNT(*) FROM following WHERE followee = users.username)
                    AS followers,
               (SELECT COUNT(*) FROM following WHERE follower = users.username)
                    AS following,
               (SELECT COUNT(*) FROM following WHERE follower = ?
                    AND followee = users.username) AS follows_user
        FROM users WHERE users.username = ?
        """,
        (logname, username)
    )
    user_data = cur.fetchone()
    if not user_data:
        flask.abort(404)

    # get posts info
    cur = conn.execute(
        """
        SELECT postid, filename FROM posts WHERE owner = ?
            ORDER BY postid DESC
        """,
        (username,)

    )
    posts = [dict(post) for post in cur.fetchall()]
    for post in posts:
        post['img_url'] = flask.url_for('download_file',
                                        filename=post['filename'])

    context = {
        "logname": logname,
        "username": username,
        "fullname": user_data["fullname"],
        "logname_follows_username": user_data["follows_user"] > 0,
        "total_posts": user_data["total_posts"],
        "followers": user_data["followers"],
        "following": user_data["following"],
        "posts": posts
    }
    return flask.render_template("user.html", **context)


@insta485.app.route('/following/', methods=["POST"])
def update_following():
    """Follow or unfollow a user, then redirect."""
    operation = flask.request.form["operation"]
    username = flask.request.form["username"]
    connection = insta485.model.get_db()
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logged_user = flask.session["username"]

    cur = connection.execute(
        "SELECT COUNT(*) AS count FROM following "
        "WHERE follower = ? AND followee = ? ",
        (logged_user, username)
    )
    already_following = cur.fetchone()["count"] > 0

    if operation == "follow":
        if already_following:
            flask.abort(409)
        connection.execute(
            "INSERT INTO following (follower, followee) VALUES (?, ?)",
            (logged_user, username)
        )
    elif operation == "unfollow":
        if not already_following:
            flask.abort(409)
        connection.execute(
            "DELETE FROM following WHERE follower = ? AND followee = ?",
            (logged_user, username)
        )
    target = flask.request.args.get("target")
    if not target:
        target = flask.url_for("show_index")
    return flask.redirect(target)
