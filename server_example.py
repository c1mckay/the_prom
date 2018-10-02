from prometheus_client import start_http_server, Gauge


def is_healthy():
    f = open('/sys/fs/lustre/health_check')
    contents = f.read().strip()
    f.close()
    return int(contents == 'healthy')


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    g = Gauge('my_random_number', '')
    g.set_function(is_healthy)

    # Generate some requests.
    while True:
        continue
