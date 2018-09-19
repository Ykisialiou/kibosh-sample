import os
import traceback
import json
import prometheus_client
import mimetypes
from flask import send_file
from flask import make_response

import flask
from flask_httpauth import HTTPBasicAuth

import db
import image

app = flask.Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "admin": "springone",
}


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


@app.route("/")
def index():
    error = flask.request.args.get("error")
    entries = app.db.list()
    for entry in entries:
        entry["votes_net"] = entry["votes_up"] - entry["votes_down"]
    entries.sort(key=lambda x: x["votes_net"], reverse=True)

    return flask.render_template('index.j2.html', entries=entries, dbtype=app.db.in_memory, disktype=app.image.on_disk, error=error)

@app.route("/get-image/<string:path>")
def get_image(path):
    binary_image = app.image.get_image(path)
    response = make_response(binary_image)
    response.headers['Content-Type'] = mimetypes.guess_type(path, strict=True)
    response.headers['Content-Disposition'] = 'inline; filename=%s' % path
    return response

@app.route("/vote_up/<int:id>", methods=['GET'])
def vote_up(id):
    app.db.vote_up(id)
    return flask.redirect("/")


@app.route("/vote_down/<int:id>", methods=['GET'])
def vote_down(id):
    app.db.vote_down(id)
    return flask.redirect("/")


@app.route("/upload", methods=['POST'])
@auth.login_required
def upload():
    global next_id
    description = flask.request.form.get("description", "").strip()
    file = flask.request.files['upload_file']

    app.image.save_image(file)
#    file.save(os.path.join(".", "static", "images", file.filename))

    entry = {
        "description": description,
        "image_path": file.filename,
        "votes_up": 0,
        "votes_down": 0,
    }
    app.db.insert(entry)

    return flask.redirect("/")


if __name__ == "__main__":
    try:
        app.db = db.newDB()
        app.image = image.new_image()
        app.db.bootstrap()

        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')))
        print("Exited normally")
    except:
        print("* Exited with exception")
        traceback.print_exc()
