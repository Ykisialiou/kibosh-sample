import os
import threading
import time
import traceback
import random
import flask
import prometheus_client
import requests
import json

app = flask.Flask(__name__)

root_request_time = prometheus_client.Summary('root_processing', 'Time spent processing request')
slow_request_time = prometheus_client.Summary('slow_endpoint_processing', 'Time spent processing request')


@app.route("/")
@root_request_time.time()
def index():
    error = flask.request.args.get("error")
    time.sleep(random.randint(1, 50) / 50)
    flask.abort(404)
    return flask.render_template('index.j2.html', error=error)

@app.route("/slow")
@slow_request_time.time()
def index_slow():
    error = flask.request.args.get("error")
    time.sleep(random.randint(1, 10))
    return flask.render_template('index.j2.html', error=error)

@app.route("/metrics")
def metrics():
    resp = flask.Response(prometheus_client.generate_latest())
    resp.headers['Content-Type'] = 'text/plain'

    return resp

def get_uri_from_env():
    vcap_app = json.loads(os.environ.get("VCAP_APPLICATION", "{}"))
    if vcap_app == {}:
        return "localhost:8080"
    return vcap_app['application_uris'][0]


def run():
    time.sleep(4)  # give app time to get healthy
    while True:
        r = requests.get("http://" + get_uri_from_env())
        print(r.status_code)
        time.sleep(random.randint(1,100)/50)

def run_slow():
    time.sleep(4) # give app time to get healthy
    while True:
        r = requests.get("http://" + get_uri_from_env() + "/slow")
        print(r.status_code)


if __name__ == "__main__":
    try:

        port = int(os.getenv('PORT', '8080'))
        thread = threading.Thread(target=run, args=())
        thread.daemon = True
        thread.start()

        thread_slow = threading.Thread(target=run_slow, args=())
        thread_slow.daemon = True
        thread_slow.start()

        app.run(host='0.0.0.0', port=port)
        print("Exited normally")
    except:
        print("* Exited with exception")
        traceback.print_exc()


