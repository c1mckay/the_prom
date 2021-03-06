import glob
import subprocess

from prometheus_client import start_http_server

from project import gauge_service
import util

HEALTH_CHECK_URL = '/sys/fs/lustre/health_check'
LLSTAT = '/usr/bin/llstat'
MD_STATS_URL = '/proc/fs/lustre/mdt/montest1-MDT0000/md_stats'
LNET_STAT_URL = '/proc/sys/lnet/stats'
OBD_URL = '/proc/fs/lustre/obdfilter/*/stats'


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
        try:
            val = llstat(url)[key]
            return float(val)
        except:  # NOQA
            return 0

    return get_md_stat


def add_md_stats():
    llstat_result = llstat(MD_STATS_URL)
    for key in llstat_result.keys():
        gauge_service.add_gauge('md_stats_' + key, get_md_stat_func(MD_STATS_URL, key))


def add_health_check():
    def is_healthy():
        contents = util.read_line(HEALTH_CHECK_URL)
        return int(contents == 'healthy')

    gauge_service.add_gauge('health_check', is_healthy)


def read_int_stat_func(url):
    def read_int_stat():
        return int(util.read_line(url))

    return read_int_stat


def add_int_stat(url, type_tag):
    for tag, full_path in resolve_path(url).items():
        gauge_service.add_gauge(type_tag + '_' + tag, read_int_stat_func(full_path))


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
        lnet_index = LNET_TYPES.index(lnet_type)
        gauge_service.add_gauge('lnet_stat_' + lnet_type,
                                read_lnet_stat_func(LNET_STAT_URL, lnet_index))


def add_obdfilter_stats():
    for tag, full_path in resolve_path(OBD_URL).items():
        llstat_result = llstat(full_path)
        for key in llstat_result.keys():
            gauge_service.add_gauge('obd_filter_' + key + '_' + tag, get_md_stat_func(
                full_path, key))


def run():
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
