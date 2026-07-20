"""
Insta485 index (main) view.

URLs include:
/
/explore/
/post/<postid>
"""
import arrow
import flask
import insta485


LOGGER = flask.logging.create_logger(insta485.app)


@insta485.app.route('/posts/<postid>/')
def show_post(postid):
    """Display /posts/<postid> route."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    # Get all posts from logname and everyone logname follows,
    # most recent first (order by postid, not timestamp)
    connection = insta485.model.get_db()
    logname = flask.session["username"]
    cur = connection.execute(
        "SELECT posts.postid, posts.filename AS img_url, posts.owner, "
        "posts.created, users.filename AS owner_img_url "
        "FROM posts "
        "JOIN users ON posts.owner = users.username "
        "WHERE posts.postid = ?",
        (postid,)
    )
    post = cur.fetchone()

    if not post:
        flask.abort(404)

    # fixing links
    post = dict(post)
    post['img_url'] = flask.url_for(
        'download_file', filename=post['img_url']
    )
    post['owner_img_url'] = flask.url_for(
        'download_file', filename=post['owner_img_url']
    )
    # Count
    # likes
    cur = connection.execute(
        "SELECT COUNT(*) AS count FROM likes WHERE postid = ?",
        (postid,)
    )
    post['likes'] = cur.fetchone()['count']

    # Get comments, oldest first
    cur = connection.execute(
        "SELECT commentid, owner, text FROM comments "
        "WHERE postid = ?",
        (postid, )
    )
    post['comments'] = cur.fetchall()

    cur = connection.execute(
        "SELECT 1 FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid)
    )
    row = cur.fetchone()
    post['logname_likes'] = row is not None

    # Humanized timestamp
    post['timestamp'] = arrow.get(post['created']).humanize()

    context = {"logname": logname, "post": post}
    return flask.render_template("post.html", **context)


@insta485.app.route('/')
def show_index():
    """Display / route."""
    connection = insta485.model.get_db()

    if "username" not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session["username"]

    # Get all posts from logname and everyone logname follows,
    # most recent first (order by postid, not timestamp)
    cur = connection.execute(
        "SELECT posts.postid, posts.filename AS img_url, posts.owner, "
        "posts.created, users.filename AS owner_img_url "
        "FROM posts "
        "JOIN users ON posts.owner = users.username "
        "WHERE posts.owner = ? "
        "OR posts.owner IN ("
        "    SELECT followee FROM following WHERE follower = ?"
        ") "
        "ORDER BY posts.postid DESC",
        (logname, logname)
    )
    posts = cur.fetchall()

    # Convert to list of dicts so we can add extra fields
    posts = [dict(post) for post in posts]

    for post in posts:
        # fixing links
        post['img_url'] = flask.url_for(
            'download_file', filename=post['img_url']
        )
        post['owner_img_url'] = flask.url_for(
            'download_file', filename=post['owner_img_url']
        )
        # Count
        # likes
        cur = connection.execute(
            "SELECT COUNT(*) AS count FROM likes WHERE postid = ?",
            (post['postid'],)
        )
        post['likes'] = cur.fetchone()['count']
        # post['logname_likes'] = cur.fetchone()['count'] > 0

        # Get comments, oldest first
        cur = connection.execute(
            "SELECT owner, text FROM comments "
            "WHERE postid = ? ORDER BY commentid ASC",
            (post['postid'],)
        )
        post['comments'] = cur.fetchall()

        cur = connection.execute(
            "SELECT 1 FROM likes WHERE owner = ? AND postid = ?",
            (logname, post['postid'])
        )
        row = cur.fetchone()
        post['logname_likes'] = row is not None

        # Humanized timestamp
        post['timestamp'] = arrow.get(post['created']).humanize()

    context = {"logname": logname, "posts": posts}
    return flask.render_template("index.html", **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    # connect to db
    connection = insta485.model.get_db()
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session["username"]
    # query db
    cur = connection.execute(
        "SELECT username, filename FROM users "
        "WHERE username != ?"
        "AND username NOT IN ("
        "   SELECT followee FROM following WHERE follower = ?"
        ")",
        (logname, logname)
    )
    not_following = [dict(user) for user in cur.fetchall()]

    for user in not_following:
        user['user_img_url'] = flask.url_for(
            'download_file', filename=user['filename']
        )
    context = {
        "logname": logname,
        "not_following": not_following,
    }

    return flask.render_template("explore.html", **context)
