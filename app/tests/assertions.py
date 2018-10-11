from prometheus_client import REGISTRY


def gauge_exists(gauge_name):
    assert gauge_name in REGISTRY._names_to_collectors


def gauge_not_exists(gauge_name):
    assert gauge_name not in REGISTRY._names_to_collectors
