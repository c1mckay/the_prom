from prometheus_client import Gauge


def add_gauge(gauge_name, gauge_func, **kwargs):
    if not kwargs:
        return Gauge(gauge_name, '').set_function(gauge_func)
    g = Gauge(gauge_name, '', [k for k in kwargs.keys()])
    g.labels(*(kwargs.values())).set_function(gauge_func)
    return g
