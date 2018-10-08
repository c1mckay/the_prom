import glob
import subprocess

from prometheus_client import start_http_server, Gauge

LLSTAT = '/usr/bin/llstat'
MD_STATS_URL = '/proc/fs/lustre/mdt/montest1-MDT0000/md_stats'


def llstat(file_location):
    output = subprocess.check_output([LLSTAT, file_location])
    lines = output.split('\n')[1:]
    return {line.split()[0]: line.split()[1] for line in lines if line}


def remove_last(s, old):
    li = s.rsplit(old, 1)
    return ''.join(li)


def resolve_path(url):
    resolved_paths = glob.glob(url)
    ret = {}
    for resolved_path in resolved_paths:
        split = url.split('*')
        tag = resolved_path.replace(split[0], '', 1)
        tag = remove_last(tag, split[1]).replace('-', '_')
        ret[tag] = resolved_path
    return ret


def read_line(url):
    f = open(url)
    contents = f.read().strip()
    f.close()
    return contents


def is_healthy():
    contents = read_line('/sys/fs/lustre/health_check')
    return int(contents == 'healthy')


def get_md_stat_func(key):
    def get_md_stat():
        val = llstat(MD_STATS_URL)[key]
        return float(val)

    return get_md_stat


def add_md_stats():
    llstat_result = llstat(MD_STATS_URL)
    for key in llstat_result.keys():
        g = Gauge('md_stats_' + key, '')
        g.set_function(get_md_stat_func(key))


def add_health_check():
    g = Gauge('health_check', '')
    g.set_function(is_healthy)


def read_int_stat_func(url):
    def read_int_stat():
        return int(read_line(url))

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
        return read_line(url).split()[index]

    return read_lnet_stat


def add_lnet_stats():
    for lnet_type in LNET_TYPES:
        g = Gauge('lnet_stat_' + lnet_type, '')
        g.set_function(read_lnet_stat_func('/proc/sys/lnet/stats', LNET_TYPES.index(lnet_type)))


ODB_FILTER_TYPES = [
    'read_bytes', 'write_bytes', 'destroy', 'create', 'statfs', 'connect', 'reconnect', 'statfs',
    'preprw', 'commitrw', 'ping'
]
ODB_URL = '/proc/fs/lustre/obdfilter/*/stats'


def add_obdfilter_stats():
    for odb_filter_type in ODB_FILTER_TYPES:
        for tag, full_path in resolve_path(ODB_URL).items():
            g = Gauge('odb_filter_' + odb_filter_type + '_' + tag, '')
            g.set_function(read_lnet_stat_func(full_path, ODB_FILTER_TYPES.index(odb_filter_type)))


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
