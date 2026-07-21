"""Rest API for routes."""
import hashlib
import flask
import insta485


@insta485.app.route('/api/v1/')
def get_urls():
    """Return urls."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)


def authenticate_user():
    """Authenticate user credentials, return username."""
    # check via cookie
    if 'username' in flask.session:
        return flask.session["username"]

    auth = flask.request.authorization
    if auth is None:
        return None
    # check user and password via http authenticate
    username = auth['username']
    password = auth['password']
    connection = insta485.model.get_db()
    cursor = connection.execute(
        "SELECT password FROM users "
        "WHERE username = ? ",
        (username,)
    )
    user = cursor.fetchone()
    if not user:
        return None
    password_db_string = user["password"]
    # hash password
    alg, salt, stored_hash = password_db_string.split("$")
    hash_object = hashlib.new(alg)
    password_salted = salt + password
    hash_object.update(password_salted.encode('utf-8'))
    password_hash = hash_object.hexdigest()
    if password_hash != stored_hash:
        return None
    return username
