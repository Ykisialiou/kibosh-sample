import os
import threading
import time
import traceback
import random
import flask
import prometheus_client
import requests
import json
import metrics

app = flask.Flask(__name__)


@app.route("/")
def index_route():
    sleep_ms(random.random() * 1000)
    return flask.render_template('index.j2.html')


@app.route("/slow")
def slow_route():
    if random.random() < 0.9:
        sleep_ms(random.random() * 1000)
    else:
        sleep_ms(random.random() * 10000)
    return flask.render_template('index.j2.html')


@app.route("/flaky")
def flaky_route():
    sleep_ms(random.random() * 1000)

    r = random.randint(1, 100)
    if r < 70:
        return flask.render_template('index.j2.html')
    elif r < 80:
        flask.abort(500)
    elif r < 90:
        flask.abort(503)
    else:
        flask.abort(504)


@app.route("/metrics")
def metrics_endpoint():
    resp = flask.Response(prometheus_client.generate_latest())
    resp.headers['Content-Type'] = 'text/plain'
    return resp


def sleep_ms(ms):
    return time.sleep(ms / 1000)


def get_uri_from_env():
    vcap_app = json.loads(os.environ.get("VCAP_APPLICATION", "{}"))
    if vcap_app == {}:
        return "localhost:8080"
    else:
        return vcap_app['application_uris'][0]


def fetch(path):
    time.sleep(4)
    while True:
        requests.get("http://" + get_uri_from_env() + path)


if __name__ == "__main__":
    try:
        for p in ["/", "/slow", "/flaky"]:
            threading.Thread(target=fetch, args=(p,), daemon=True).start()

        metrics.setup_metrics(app)
        app.run(host='0.0.0.0', port=(int(os.getenv('PORT', '8080'))))
        print("Exited normally")
    except:
        print("* Exited with exception")
        traceback.print_exc()
