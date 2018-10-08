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


def read_stat(url):
    f = open(url)
    contents = f.read().strip()
    f.close()
    return contents


def is_healthy():
    contents = read_stat('/sys/fs/lustre/health_check')
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
        return int(read_stat(url))

    return read_int_stat


def add_int_stat(url, type_tag):
    for tag, full_path in resolve_path(url).items():
        g = Gauge(type_tag + tag, '')
        g.set_function(read_int_stat_func(full_path))


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    add_health_check()
    add_md_stats()
    add_int_stat('/proc/fs/lustre/osd-zfs/*/kbytesfree', 'kbytes_free')
    add_int_stat('/proc/fs/lustre/osd-zfs/*/filesfree', 'files_free')

    # Generate some requests.
    while True:
        continue
