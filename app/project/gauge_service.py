from prometheus_client import Gauge


def add_gauge(gauge_name, gauge_func, src=None):
    # g = Gauge(gauge_name, '', ['src'])
    # g.labels({'src': src}).set_function(gauge_func)
    g = Gauge(gauge_name, '')
    g.set_function(gauge_func)
    return g
