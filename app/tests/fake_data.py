import random
import string

from prometheus_client import REGISTRY


def get_func(x=1):
    def basic_func():
        return x

    return basic_func


def random_string():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(16))


def _get_functions():
    import inspect
    return inspect.getmembers(REGISTRY, predicate=inspect.ismethod)
