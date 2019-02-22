import os
import traceback
import json
import prometheus_client

import flask

import db

app = flask.Flask(__name__)

root_request_time = prometheus_client.Summary('root_processing_seconds', 'Time spent processing request')
put_request_time = prometheus_client.Summary('put_processing_seconds', 'Time spent processing request')
delete_request_time = prometheus_client.Summary('delete_processing_seconds', 'Time spent processing request')


@app.route("/")
@root_request_time.time()
def index():
    error = flask.request.args.get("error")
    db_response = app.db.list()

    return flask.render_template('index.j2.html', items=db_response, error=error)


@app.route("/put", methods=['POST'])
@put_request_time.time()
def put():
    key = flask.request.form.get("key", "").strip()
    value = flask.request.form.get("value", "").strip()
    if key == "" or value == "":
        return flask.redirect("/?error=Key and value are required")

    app.db.insert(key, value)
    return flask.redirect("/")


@app.route("/delete", methods=['POST'])
@delete_request_time.time()
def delete():
    key = flask.request.form.get("key", "").strip()
    app.db.delete(key)
    return flask.redirect("/")


@app.route("/metrics")
def metrics():
    resp = flask.Response(prometheus_client.generate_latest())
    resp.headers['Content-Type'] = 'text/plain'

    return resp


def get_credentials_from_env():
    vcap_service = json.loads(os.environ['VCAP_SERVICES'])
    my_sql = vcap_service['mysql-instance'][0]
    secrets = my_sql["credentials"]["secrets"][0]
    services = my_sql["credentials"]["services"][0]

    return {
        'host': services["status"]["loadBalancer"]["ingress"][0]["ip"],
        'database': 'my_db',
        'user': 'root',
        'password': secrets["data"]["mysql-root-password"],
        'port': services["spec"]["ports"][0]["port"]
    }


if __name__ == "__main__":
    try:
        app.db = db.DB(get_credentials_from_env())
        app.db.write_schema()
        app.db.insert("foo", "bar")
        app.db.insert("baz", "qux")

        app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')))
        print("Exited normally")
    except:
        print("* Exited with exception")
        traceback.print_exc()
