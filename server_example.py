import time
import random
import string

from prometheus_client import start_http_server, Summary

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


def random_string():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    Summary('my_summary', 'unused').observe(random_string())

    # Generate some requests.
    while True:
        process_request(random.random())
