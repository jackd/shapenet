def parse_seg(fp):
    return [int(r) for r in fp.readlines()]


def parse_pts(fp):
    return [[float(a) for a in r.split(' ')] for r in fp.readlines()]
