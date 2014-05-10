#! /usr/bin/env python

import numpy as np
from random import randint
from itertools import count
import re
import os

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


class VMFObject(object):

    def __init__(self, name):
        super(VMFObject, self).__init__()
        self.name = name
        self.attributes = {}
        self.children = []

    def __repr__(self):
        out = [self.name, '{']
        for k, v in self.attributes.iteritems():
            out.append('"{0}" "{1}"'.format(k, v))
        for child in self.children:
            out.append(str(child))
        out.append('}')
        return '\r\n'.join(out)


class VMF(VMFObject):
    """Holds a VMF file"""

    def __init__(self, filename, dedot=False):
        super(VMF, self).__init__('')
        if os.path.splitext(filename)[1] != '.vmf':
            filename += '.vmf'
        head, tail = os.path.split(filename)
        if '.' in os.path.splitext(tail)[0]:
            if dedot:
                tail = tail.split('.')[0]
                tail += '.vmf'
                filename = os.path.join(head, tail)
            else:
                raise DotInFilenameError(filename)
        self.filename = filename
        try:
            f = file(filename)
            m = re.search(r'"mapversion" "(\d+)"', f.read())
            self.version = int(m.group(1))
        except:
            self.version = 0
        vinfo = VMFObject("versioninfo")
        vinfo.attributes['mapversion'] = self.version
        self.children.append(vinfo)
        world = VMFObject("world")
        self.world = world
        self.children.append(world)
        world.attributes = {'detailvbsp': 'detail.vbsp', 'skyname': 'sky_cont_overcast01_hdr', 'classname': 'worldspawn', 'mapversion': self.version, 'maxpropscreenwidth': '-1', 'detailmaterial': 'detail/detailsprites', 'id': '0'}

    def add_solid(self, solid):
        self.world.children.append(solid)

    def __repr__(self):
        self.name = ''
        tmp = super(VMF, self).__repr__()
        tmp = tmp[3:-1]
        out = []
        brackets = 0
        for line in tmp.split("\r\n"):
            if line == '}':
                brackets -= 1
            out.append('\t'*brackets + line)
            if line == '{':
                brackets += 1
        return '\r\n'.join(out)

    def write(self):
        f = file(self.filename, 'w')
        f.write(repr(self))
        f.close()


class DotInFilenameError(Exception):
    pass


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
    return '\r\n'.join(out)


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
