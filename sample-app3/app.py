import os
import traceback
import json
import prometheus_client

import flask
from flask_httpauth import HTTPBasicAuth

import db

app = flask.Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "admin": "springone",
}

next_id = 3

memory_db = [
    {
        "id": 1,
        "description": "Dog in cow's clothing",
        "image_path": "dog_with_cows.jpg",
        "votes_up": 2,
        "votes_down": 1,
    },
    {
        "id": 2,
        "description": "A rabbit mouse? A rabbit? Hybrid?",
        "image_path": "rabbit.jpg",
        "votes_up": 3,
        "votes_down": 0,
    },
]

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route("/")
def index():
    error = flask.request.args.get("error")
    entries = memory_db
    for entry in entries:
        entry["votes_net"] = entry["votes_up"] - entry["votes_down"]
    entries.sort(key=lambda x: x["votes_net"], reverse=True)

    return flask.render_template('index.j2.html', entries=entries, error=error)


@app.route("/vote_up/<int:id>", methods=['GET'])
def vote_up(id):
    # todo: push this into db
    for entry in memory_db:
        if entry["id"] == id:
            entry["votes_up"] += 1
    return flask.redirect("/")


@app.route("/vote_down/<int:id>", methods=['GET'])
def vote_down(id):
    # todo: push this into db
    for entry in memory_db:
        if entry["id"] == id:
            entry["votes_down"] += 1
    return flask.redirect("/")


@app.route("/upload", methods=['POST'])
@auth.login_required
def upload():
    global next_id
    description = flask.request.form.get("description", "").strip()
    file = flask.request.files['upload_file']

    file.save(os.path.join(".", "static", "images", file.filename))

    memory_db.append(
        {
            "id": next_id,
            "description": description,
            "image_path": file.filename,
            "votes_up": 0,
            "votes_down": 0,
        }
    )

    next_id += 1

    return flask.redirect("/")


if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')))
        print("Exited normally")
    except:
        print("* Exited with exception")
        traceback.print_exc()
