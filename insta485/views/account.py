"""
Insta485 Account View.

URLS Include:

/accounts/login/
/accounts/create/
/accounts/logout/
/acounts/?target
"""

import uuid
import hashlib
import pathlib
import flask
import insta485


@insta485.app.route("/accounts/logout/", methods=["POST"])
def logout():
    """Logout from session."""
    flask.session.clear()
    return flask.redirect('/accounts/login/')


def do_login():
    """Login to session."""
    username = flask.request.form["username"]
    password = flask.request.form["password"]
    if not username or not password:
        flask.abort(400)
    # verify password matches
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password FROM users "
        "WHERE username = ? ",
        (username,)
    )
    user = cur.fetchone()
    if not user:
        flask.abort(403)
    password_db_string = user["password"]

    # hash password
    algorithm, salt, stored_hash = password_db_string.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    if password_hash != stored_hash:
        flask.abort(403)

    flask.session['username'] = username
    target = flask.request.args.get("target")
    if not target:
        target = flask.url_for("show_index")
    return flask.redirect(target)


def do_create():
    """Create account."""
    username = flask.request.form["username"]
    password = flask.request.form["password"]
    fullname = flask.request.form["fullname"]
    email = flask.request.form["email"]
    file = flask.request.files["file"]

    # check if any are empty
    if (not username or not password or not fullname):
        flask.abort(400)
    if (not email or not file):
        flask.abort(400)
    # check of username already exists
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT COUNT(*) AS count FROM users "
        "WHERE username = ? ",
        (username,)
    )
    if cur.fetchone()["count"] > 0:
        flask.abort(409)

    # hash password
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    uuid_basename = save_uploaded_image(file)

    # create user
    connection.execute(
        "INSERT INTO users (username, fullname, email, filename, password)"
        "VALUES (?, ?, ?, ?, ?)",
        (username, fullname, email, uuid_basename, password_db_string)
    )
    flask.session['username'] = username
    target = flask.request.args.get("target")
    if not target:
        target = flask.url_for("show_index")
    return flask.redirect(target)


def do_delete():
    """Delete account."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    # save logged in user
    logname = flask.session["username"]
    # delete all post files
    # connect to db
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT filename FROM posts WHERE owner = ?",
        (logname,)
    )
    post_files = cur.fetchall()
    # delete user icon file
    cur = connection.execute(
        "SELECT filename FROM users WHERE username = ?",
        (logname,)
    )
    user_row = cur.fetchone()

    upload_folder = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])

    for post in post_files:
        file_path = upload_folder / post["filename"]
        if file_path.exists():
            file_path.unlink()

    if user_row:
        icon_path = upload_folder / user_row["filename"]
        if icon_path.exists():
            icon_path.unlink()

    # delete related entries in all tables
    connection.execute(
        "DELETE FROM users WHERE username = ?",
        (logname,)
    )

    flask.session.clear()
    return flask.redirect(flask.request.args.get("target")
                          or flask.url_for("show_index"))


def do_edit_acct():
    """Edit account."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))

    logname = flask.session["username"]
    fullname = flask.request.form["fullname"]
    email = flask.request.form["email"]
    if fullname == "" or email == "":
        flask.abort(400)

    connection = insta485.model.get_db()
    upload_folder = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])
    fileobj = flask.request.files["file"]
    filename = fileobj.filename
    if fileobj and filename:
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = ?",
            (logname,)
        )
        old_filename = cur.fetchone()["filename"]
        fileobj = flask.request.files["file"]
        uuid_basename = save_uploaded_image(fileobj)
        old_path = upload_folder / old_filename
        if old_path.exists():
            old_path.unlink()

        connection.execute(
            "UPDATE users SET fullname = ?, email = ?, filename = ? "
            "WHERE username = ?",
            (fullname, email, uuid_basename, logname)
        )
    else:
        connection.execute(
            "UPDATE users SET fullname = ?, email = ? WHERE username = ?",
            (fullname, email, logname)
        )
    target = flask.request.args.get("target")
    if not target:
        target = flask.url_for("show_index")
    return flask.redirect(target)


def do_update_password():
    """Update password."""
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session['username']
    password = flask.request.form["password"]
    new_password1 = flask.request.form["new_password1"]
    new_password2 = flask.request.form["new_password2"]
    if not password or not new_password1 or not new_password2:
        flask.abort(400)
    # verify password matches
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password FROM users "
        "WHERE username = ? ",
        (logname,)
    )
    user = cur.fetchone()
    if not user:
        flask.abort(403)
    password_db_string = user["password"]
    # hash password
    algorithm, salt, stored_hash = password_db_string.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    if password_hash != stored_hash:
        flask.abort(403)
    if new_password1 != new_password2:
        flask.abort(401)
    # edit password
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + new_password1
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    cur = connection.execute(
        "UPDATE users "
        "SET password = ? "
        "WHERE username = ? ",
        (password_db_string, logname,)
    )
    target = flask.request.args.get("target")
    if not target:
        target = flask.url_for("show_index")
    return flask.redirect(target)


@insta485.app.route("/accounts/", methods=["POST"])
def update_account():
    """Login, create, delete, edit, update password + redirect."""
    operation = flask.request.form["operation"]
    target = flask.request.args.get('target', '/')

    if operation == "login":
        return do_login()

    if operation == "create":
        return do_create()

    if operation == "delete":
        return do_delete()

    if operation == "edit_account":
        return do_edit_acct()

    if operation == "update_password":
        return do_update_password()

    return flask.redirect(target)


@insta485.app.route('/accounts/auth/')
def auth():
    """Return 200 if logged in, otherwise abort with a 403."""
    if 'username' not in flask.session:
        flask.abort(403)
    return "", 200


@insta485.app.route('/accounts/password/')
def show_password():
    """Display / change password."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session["username"]

    context = {"logname": logname}

    return flask.render_template("password.html", **context)


@insta485.app.route('/accounts/edit/')
def show_edit():
    """Display / edit."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session["username"]
    connection = insta485.model.get_db()

    # not similar
    cur = connection.execute(
        """
        SELECT username, fullname, email, filename
        FROM users
        WHERE username = ?
        """,
        (logname,)
    )
    user_info = cur.fetchone()
    # these functions are different
    context = {
        "logname": logname,
        "username": user_info["username"],
        "fullname": user_info["fullname"],
        "email": user_info["email"],
        "filename": flask.url_for(
            'download_file', filename=user_info["filename"])
    }

    return flask.render_template("edit.html", **context)


@insta485.app.route('/accounts/delete/')
def show_delete():
    """Display / delete."""
    if "username" not in flask.session:
        return flask.redirect(flask.url_for("show_login"))
    logname = flask.session["username"]

    context = {"logname": logname}

    return flask.render_template("delete.html", **context)


@insta485.app.route('/accounts/login/')
def show_login():
    """Display / login."""
    # change later if already logged in redirect to home

    return flask.render_template("login.html")


@insta485.app.route('/accounts/create/')
def show_create():
    """Display / create."""
    # change later if already logged in redirect to edit

    return flask.render_template("create.html")


def save_uploaded_image(fileobj):
    """Save an uploaded file to disk and return its new secure UUID name."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(fileobj.filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
    fileobj.save(path)
    return uuid_basename
