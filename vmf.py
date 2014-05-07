#! /usr/bin/env python

import numpy as np
from random import randint
from itertools import count

solid_id = count(1)
side_id = count(1)


def _normalise(vector):
    return vector / np.linalg.norm(vector)


def _random_joined_lines(n):
    last_end = np.array((0, 0, 0))
    for i in xrange(n):
        new_end = np.array([randint(0, 9999), randint(0, 9999), 0])
        yield (last_end, new_end)
        last_end = new_end


class VMF(object):
    """Holds a VMF file"""
    def __init__(self, filename):
        super(VMF, self).__init__()
        self.filename = filename


def header():
    return """versioninfo
{
    "mapversion" "0"
}
"""


def wall_from_line(*args):
    return _solid_from_sides(_wall_sides_from_line(*args))


def _solid_from_sides(sides):
    out = ['solid', '{', '"id" "{0}"'.format(solid_id.next())]
    for side in sides:
        side_out = ['side', '{']
        side_out.append('"id" "{0}"'.format(side_id.next()))
        side_out.append('"plane" "({0}) ({1}) ({2})"'
                        .format(*[' '.join([repr(point) for point in points])
                                for points in side]))
        u = _normalise(side[1] - side[0])
        v = _normalise(side[2] - side[1])
        side_out.append('"material" "BARRICADE/BOARD_DIFFUSE_01"')
        side_out.append('"uaxis" "[{0} 0] 0.25"'
                        .format(' '.join([repr(p) for p in u])))
        side_out.append('"vaxis" "[{0} 0] 0.25"'
                        .format(' '.join([repr(p) for p in v])))
        side_out.append('"rotation" "0"')
        side_out.append('"lightmapscale" "16"')
        side_out.append('"smoothing_groups" "0"')
        side_out.append('}')
        out.extend(side_out)
    out.append('}')
    return '\n'.join(out)


def _wall_sides_from_line(line, w, h):
    sides = []
    s, e = line
    s = np.array(s)
    e = np.array(e)
    v = e - s
    u = np.array([0, 0, 1])
    tmp = np.cross(v, u)
    tmp = _normalise(tmp)
    p1 = s + tmp * w/2 + np.array([0, 0, h])
    p2 = s - tmp * w/2 + np.array([0, 0, h])
    p3 = p2 + v
    p4 = p1 + v
    top = (p1, p2, p3, p4)
    top = [np.array([round(x) for x in p], int) for p in top]
    sides.append(top[:3])

    u = np.array([0, 0, -1])
    tmp = np.cross(v, u)
    tmp = _normalise(tmp)
    p1 = s + tmp * w/2
    p2 = s - tmp * w/2
    p3 = p2 + v
    p4 = p1 + v
    bottom = (p1, p2, p3, p4)
    bottom = [np.array([round(x) for x in p], int) for p in bottom]
    sides.append(bottom[:3])

    sides.append((bottom[1], top[0], top[3]))
    sides.append((bottom[0], top[1], top[0]))
    sides.append((bottom[3], top[2], top[1]))
    sides.append((bottom[2], top[3], top[2]))
    return sides
