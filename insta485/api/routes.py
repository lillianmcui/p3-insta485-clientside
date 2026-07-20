""" Rest API for routes."""
import flask
import insta485
import hashlib

@insta485.app.route('/api/v1/')
def get_urls():
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context)

def authenticate_user():
    """
    Authenticate user credentials.
    """
    # check via cookie
    if 'username' in flask.session:
        return True

    # check user and password via http authenticate
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password FROM users "
        "WHERE username = ? ",
        (username,)
    )
    user = cur.fetchone()
    if not user:
        return False
    password_db_string = user["password"]
    # hash password
    algorithm, salt, stored_hash = password_db_string.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    if password_hash != stored_hash:
        return False
    return True
    
    

    


