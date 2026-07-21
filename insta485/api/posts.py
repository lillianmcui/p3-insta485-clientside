"""REST API for posts."""
import flask
import insta485
from insta485.api.routes import authenticate_user


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid."""
    # auth user
    logname = authenticate_user()
    if not logname:
        return flask.jsonify({
          "message": "Forbidden",
          "status_code": 403
        }), 403
    connection = insta485.model.get_db()

    # post/owner info
    post_cur = connection.execute(
        """
        SELECT posts.postid, posts.filename, posts.owner,
          posts.created, users.filename AS ownerImgUrl
        FROM posts
        JOIN users ON posts.owner = users.username
        WHERE posts.postid = ?
        """,
        (postid_url_slug,)
    )
    post = post_cur.fetchone()
    if not post:
        return flask.jsonify({
            "message": "Post Not Found",
            "status_code": 404
        }), 404

    # likes
    likes_cur = connection.execute(
      "SELECT COUNT(*) AS count FROM likes WHERE postid = ?",
      (postid_url_slug,)
    )
    likes = likes_cur.fetchone()["count"]

    logname_like_cur = connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid_url_slug)
    )
    like_row = logname_like_cur.fetchone()

    if like_row:
        logname_likes_this = True
    else:
        logname_likes_this = False

    # comments
    comments_cur = connection.execute(
          "SELECT commentid, owner, text FROM comments "
          "WHERE postid = ? ORDER BY commentid ASC",
          (postid_url_slug,)
      )
    comments_rows = comments_cur.fetchall()
    comments = []
    for row in comments_rows:
        comments.append({
            "commentid": row["commentid"],
            "lognameOwnsThis": row["owner"] == logname,
            "owner": row["owner"],
            "ownerShowUrl": f"/users/{row['owner']}/",
            "text": row["text"],
            "url": f"/api/v1/comments/{row['commentid']}/"
        })

    context = {
      "comments": comments,
      "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
      "created": post["created"],
      "imgUrl": f"/uploads/{post['filename']}",
      "likes": {
          "lognameLikesThis": logname_likes_this,
          "numLikes": likes,
          "url": f"/api/v1/likes/{like_row['likeid']}/" if like_row else None
      },
      "owner": post["owner"],
      "ownerImgUrl": f"/uploads/{post['ownerImgUrl']}",
      "ownerShowUrl": f"/users/{post['owner']}/",
      "postShowUrl": f"/posts/{postid_url_slug}/",
      "postid": postid_url_slug,
      "url": f"/api/v1/posts/{postid_url_slug}/"
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/')
def get_newest_posts():
    """Return the 10 newest posts from following or logname."""
    logname = authenticate_user()
    if not logname:
        return flask.jsonify({
          "message": "Forbidden",
          "status_code": 403
        }), 403

    try:
        size = flask.request.args.get('size', 10, type=int)
        page = flask.request.args.get('page', 0, type=int)
    except ValueError:
        flask.abort(400)

    if size <= 0 or page < 0:
        flask.abort(400)
    connection = insta485.model.get_db()

    postid_lte = flask.request.args.get('postid_lte', type=int)
    if postid_lte is None:
        row = connection.execute(
          "SELECT MAX(postid) AS max_postid FROM posts"
        ).fetchone()
        postid_lte = row['max_postid'] if row['max_postid'] is not None else 0

    connection = insta485.model.get_db()
    newest_posts = connection.execute(
        """
        SELECT postid FROM posts
        WHERE postid <= ?
        AND owner = ?
        OR owner IN (SELECT followee FROM following WHERE follower = ?)
        ORDER BY postid DESC
        LIMIT ?
        OFFSET ?
        """,
        (postid_lte, logname, logname, size, size * page)
    ).fetchall()

    results = [
      {"postid": post['postid'], "url": f"/api/v1/posts/{post['postid']}/"}
      for post in newest_posts
    ]

    next_page = ''
    if len(results) >= size:
        next_page = (
          f"/api/v1/posts/?size={size}&page={page + 1}&postid_lte={postid_lte}"
        )
    if flask.request.query_string:
        url = flask.request.full_path
    else:
        url = flask.request.path
    context = {
      "next": next_page,
      "results": results,
      "url": url,
    }
    return flask.jsonify(**context)
