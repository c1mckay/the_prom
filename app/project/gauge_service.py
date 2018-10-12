from prometheus_client import Gauge


def add_gauge(gauge_name, gauge_func, **kwargs):
    if not kwargs:
        return Gauge(gauge_name, '').set_function(gauge_func)
    tags = [k for k in kwargs.keys()]
    g = Gauge(gauge_name, '', tags)
    g.labels(*[kwargs[tag] for tag in tags]).set_function(gauge_func)
    return g
