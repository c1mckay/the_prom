def remove_last(s, old):
    li = s.rsplit(old, 1)
    return ''.join(li)


def read_line(url):
    f = open(url)
    contents = f.read().strip()
    f.close()
    return contents
