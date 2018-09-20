import flask
import time
import sys
import prometheus_client

request_count = prometheus_client.Counter(
    'request_count', 'App Request Count',
    ['app_name', 'method', 'endpoint', 'http_status']
)
request_latency = prometheus_client.Histogram(
    'request_latency_seconds', 'Request latency',
    ['app_name', 'endpoint']
)


def start_timer():
    flask.request.start_time = time.time()


def stop_timer(response):
    resp_time = time.time() - flask.request.start_time
    request_latency.labels('metrics_app', flask.request.path).observe(resp_time)
    return response


def record_request_data(response):
    request_count.labels('metrics_app', flask.request.method, flask.request.path, response.status_code).inc()
    return response


def setup_metrics(app):
    app.before_request(start_timer)
    app.after_request(record_request_data)
    app.after_request(stop_timer)
