"""
Insta485 uploads view.

URLS include:
/uploads/filename/
"""

import flask
import insta485


@insta485.app.route('/uploads/<filename>')
def download_file(filename):
    """Download file to disk."""

    if "username" not in flask.session:
       flask.abort(403)
    return flask.send_from_directory(
        insta485.app.config["UPLOAD_FOLDER"], filename
    )
