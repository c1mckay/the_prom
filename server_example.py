import subprocess

from prometheus_client import start_http_server, Gauge

LLSTAT = '/usr/bin/llstat'
MD_STATS_URL = '/proc/fs/lustre/mdt/montest1-MDT0000/md_stats'


def llstat(file_location):
    output = subprocess.check_output([LLSTAT, file_location])
    lines = output.split('\n')[1:]
    return {line.split()[0]: line.split()[1] for line in lines if line}


def is_healthy():
    f = open('/sys/fs/lustre/health_check')
    contents = f.read().strip()
    f.close()
    return int(contents == 'healthy')


def get_md_stat_func(key):
    def get_md_stat():
        val = llstat(MD_STATS_URL)[key]
        return float(val)

    return get_md_stat


def add_md_stats():
    llstat_result = llstat(MD_STATS_URL)
    for key in llstat_result.keys():
        g = Gauge('md_stat_' + key, '')
        g.set_function(get_md_stat_func(key))


def add_health_check():
    g = Gauge('health_check', '')
    g.set_function(is_healthy)


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    add_health_check()
    add_md_stats()

    # Generate some requests.
    while True:
        continue
