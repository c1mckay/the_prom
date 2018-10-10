import glob
import subprocess

from prometheus_client import start_http_server, Gauge
import util

LLSTAT = '/usr/bin/llstat'
MD_STATS_URL = '/proc/fs/lustre/mdt/montest1-MDT0000/md_stats'


def llstat(file_location):
    try:
        output = subprocess.check_output([LLSTAT, file_location])
        lines = output.split('\n')[1:]
        return {line.split()[0]: line.split()[1] for line in lines if line}
    except subprocess.CalledProcessError:
        return {}


def resolve_path(url):
    resolved_paths = glob.glob(url)
    ret = {}
    for resolved_path in resolved_paths:
        split = url.split('*')
        tag = resolved_path.replace(split[0], '', 1)
        tag = util.remove_last(tag, split[1]).replace('-', '_')
        ret[tag] = resolved_path
    return ret


def get_md_stat_func(url, key):
    def get_md_stat():
        val = llstat(url)[key]
        return float(val)

    return get_md_stat


def add_md_stats():
    llstat_result = llstat(MD_STATS_URL)
    for key in llstat_result.keys():
        g = Gauge('md_stats_' + key, '')
        g.set_function(get_md_stat_func(MD_STATS_URL, key))


def add_health_check():
    def is_healthy():
        contents = util.read_line('/sys/fs/lustre/health_check')
        return int(contents == 'healthy')

    g = Gauge('health_check', 'WHERE_IS_TEXT')
    g.set_function(is_healthy)
    g = Gauge('health_check', 'WHERE_IS_TEXT')
    g.set_function(is_healthy)
    g = Gauge('health_checky', 'WHERE_IS_TEXT')
    g.set_function(is_healthy)


def read_int_stat_func(url):
    def read_int_stat():
        return int(util.read_line(url))

    return read_int_stat


def add_int_stat(url, type_tag):
    for tag, full_path in resolve_path(url).items():
        g = Gauge(type_tag + '_' + tag, '')
        g.set_function(read_int_stat_func(full_path))


LNET_TYPES = [
    'msgs_alloc', 'msgs_max', 'errors', 'send_count', 'receive_count', 'route_count', 'drop_count',
    'send_bytes', 'receive_bytes', 'route_length', 'drop_length'
]


def read_lnet_stat_func(url, index):
    def read_lnet_stat():
        return util.read_line(url).split()[index]

    return read_lnet_stat


def add_lnet_stats():
    for lnet_type in LNET_TYPES:
        g = Gauge('lnet_stat_' + lnet_type, '')
        g.set_function(read_lnet_stat_func('/proc/sys/lnet/stats', LNET_TYPES.index(lnet_type)))


ODB_URL = '/proc/fs/lustre/obdfilter/*/stats'


def add_obdfilter_stats():
    for tag, full_path in resolve_path(ODB_URL).items():
        llstat_result = llstat(full_path)
        for key in llstat_result.keys():
            print('adding' + 'odb_filter_' + key + '_' + tag)
            res = get_md_stat_func(full_path, key)()
            print('result: ' + str(res))
            g = Gauge('odb_filter_' + key + '_' + tag, '')
            g.set_function(get_md_stat_func(full_path, key))


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    add_health_check()
    add_md_stats()

    add_int_stat('/proc/fs/lustre/osd-zfs/*/kbytesfree', 'kbytes_free')
    add_int_stat('/proc/fs/lustre/osd-zfs/*/filesfree', 'files_free')

    add_lnet_stats()
    add_obdfilter_stats()

    # Generate some requests.
    while True:
        continue
