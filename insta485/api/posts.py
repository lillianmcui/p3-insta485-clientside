"""REST API for posts."""
import flask
import insta485
from insta485.api.routes import authenticate_user


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
def get_post(postid_url_slug):
    """Return post on postid.

    Example:
    {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postShowUrl": "/posts/1/",
      "postid": 1,
      "url": "/api/v1/posts/1/"
    }
    """
    if not authenticate_user():
      return flask.jsonify({
          "message": "Forbidden",
          "status_code": 403
      }), 403

    context = {
        "created": "2017-09-28 04:33:28",
        "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": flask.request.path,
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/')
def get_newest_posts():
  """ Return the 10 newest posts from following or logname."""
  if not authenticate_user():
    return flask.jsonify({
        "message": "Forbidden",
        "status_code": 403
    }), 403
  logname = flask.session['username']

  try:
    size = flask.request.args.get('size', 10, type=int)
    page = flask.request.args.get('page', 0, type=int)
  except ValueError:
    flask.abort(400)

  if size <= 0 or page < 0:
    flask.abort(400)

  postid_leq = flask.request.args.get('postid_leq', type=int)
  if postid_leq is None:
    row = connection.execute(
      "SELECT MAX(postid) AS max_postid FROM posts"
    ).fetchone()
    postid_leq = row['max_postid'] if row['max_postid'] is not None else 0

  connection = insta485.model.get_db()
  newest_posts = connection.execute(
    """
    SELECT postid FROM posts
    WHERE post id <= ?
    AND owner = ?
    OR owner IN (SELECT followee FROM following WHERE follower = ?)
    ORDER BY postid DESC
    LIMIT ?
    OFFFSET ?
    (postid_leq, logname, logname, size, size * page)
    """,
    (postid)
  ).fetchall()

  results = [
    {"postid": post['postid'], "url": f"/api/v1/posts/{post['postid']}/"}
    for post in newest_posts
  ]

  next = ''
  if len(results) >= size:
    next = (
      f"/api/v1/posts/?size={size}&page={page + 1}&postid_leq={postid_leq}"
    )
  context = {
    "next": next_url,
    "results": results,
    "url": flask.request.path,
  }
  return flask.jsonify(**context)
