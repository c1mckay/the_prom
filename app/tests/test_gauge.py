from project import gauge_service
from tests.fake_data import get_func, random_string
from tests import assertions as test


def test_gauge_exists():
    gauge_name = random_string()

    gauge_service.add_gauge(gauge_name, get_func())

    test.gauge_exists(gauge_name)
    test.gauge_not_exists(gauge_name + '2')


def test_src_label():
    gauge_name = random_string()
    gauge_val = 4

    def gauge_func():
        return gauge_val

    gauge_service.add_gauge(gauge_name, gauge_func)
    gauge_func()

    test.gauge_exists(gauge_name)
