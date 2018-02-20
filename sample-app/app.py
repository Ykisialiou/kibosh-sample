import os
import traceback
import json

import flask

import db

app = flask.Flask(__name__)


@app.route("/")
def index():
    error = flask.request.args.get("error")
    db_response = app.db.list()

    return flask.render_template('index.j2.html', items=db_response, error=error)


@app.route("/put", methods=['POST'])
def put():
    key = flask.request.form.get("key", "").strip()
    value = flask.request.form.get("value", "").strip()
    if key == "" or value == "":
        return flask.redirect("/?error=Key and value are required")

    app.db.insert(key, value)
    return flask.redirect("/")


@app.route("/delete", methods=['POST'])
def delete():
    key = flask.request.form.get("key", "").strip()
    app.db.delete(key)
    return flask.redirect("/")


def get_credentials_from_env():
    # todo: parse VCAP_SERVICES!
    return {
        'host': 'localhost',
        'database': 'kibosh',
        'user': 'root',
        'password': 'password',
    }


if __name__ == "__main__":
    try:
        app.db = db.DB(get_credentials_from_env())
        app.db.write_schema()
        app.db.insert("foo", "bar")
        app.db.insert("baz", "qux")

        app.run(host='0.0.0.0', port=os.getenv('PORT', '8080'))
        print("Exited normally")
    except:
        print("* Exited with exception")
        traceback.print_exc()
