import os
import traceback
import json
import prometheus_client

import flask

import db

app = flask.Flask(__name__)

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
def upload():
    description = flask.request.form.get("description", "").strip()
    file = flask.request.files['upload_file']
    print("description", description)
    print("file", file)
    print("file.filename", file.filename)
    print("current folder", os.listdir('.'))

    file.save(os.path.join(".", "static", "images", file.filename))

    memory_db.append(

    )

    return flask.redirect("/")


if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')))
        print("Exited normally")
    except:
        print("* Exited with exception")
        traceback.print_exc()
