from Queue import Queue, LifoQueue
from itertools import combinations, product
from math import acos, pi

MIN_LINE_LENGTH = 10

# TODO: deal with 45 degree angles


def straight_lines(im, visual=False, log=False):
    """
    Works on a singly-connected binary image.
    Use threshold and zhangSuen to achieve this.
    """
    # threshold at 90%
    if visual:
        im.show()
    pa = im.load()
    expanded = set()
    queue = Queue()
    lines = []
    # iterate over all pixels
    for pixel in product(xrange(im.size[0]),
                         xrange(im.size[1])):
        # add unexpanded white pixels to queue for all directions
        if not _is_black(pa[pixel]):
            if (pixel) not in expanded:
                qo = QueueObject(pixel, None, None, None, 0, pa)
                queue.put(qo)
        while not queue.empty():
            node = queue.get()
            if node.pixel in expanded:
                continue
            expanded.add((node.pixel))
            children = node.expand()
            # if cannot expand
            if len(children) == 0 or all(c in expanded for c in children):
                expanded.remove(node.pixel)
                if node.length > MIN_LINE_LENGTH:
                    lines.append(node)
                    if log:
                        print len(lines), "found."
            elif len(children) == 1:
                queue.put(children[0])
            else:
                expanded.remove(node.pixel)
                if node.length > MIN_LINE_LENGTH:
                    lines.append(node)
                    if log:
                        print len(lines), "found."
                for child in children:
                    if child.pixel not in expanded:
                        child.root = node
                        child.length = 1
                        queue.put(child)

    # lines_by_endpoints = {}
    # for line in lines:
    #     try:
    #         lines_by_endpoints[line.root.pixel].append(line)
    #     except KeyError:
    #         lines_by_endpoints[line.root.pixel] = [line]
    #     try:
    #         lines_by_endpoints[line.pixel].append(line)
    #     except KeyError:
    #         lines_by_endpoints[line.pixel] = [line]
    #
    # for endpoint in lines_by_endpoints:
    #     for pair in combinations(lines_by_endpoints[endpoint], 2):
    #         if _should_combine(*pair):
    #             if pair[0] not in lines or pair[1] not in lines:
    #                 continue
    #             # combine line
    #             ends = [pair[0].root.pixel, pair[0].pixel,
    #                     pair[1].root.pixel, pair[1].pixel]
    #             ends = [e for e in ends if e != endpoint]
    #             newroot = QueueObject(ends[0], None, None, None, 0, None)
    #             new = QueueObject(ends[1], newroot, newroot, None,
    #                               pair[0].length + pair[1].length, None)
    #             lines.remove(pair[0])
    #             lines.remove(pair[1])
    #             lines.append(new)
    #             lines_by_endpoints[endpoint].remove(pair[0])
    #             lines_by_endpoints[endpoint].remove(pair[1])
    #             lines_by_endpoints[new.root.pixel].remove(pair[0])
    #             lines_by_endpoints[new.root.pixel].append(new)
    #             lines_by_endpoints[new.pixel].remove(pair[1])
    #             lines_by_endpoints[new.pixel].append(new)
    return lines


def _should_combine(node1, node2):
    if (node1.pixel == node1.root.pixel
        or node2.pixel == node2.root.pixel):
            return False
    angle = _angle(node1, node2)
    max_angle1 = _vangle([node1.length, 1], [1, 0])
    max_angle2 = _vangle([node2.length, 1], [1, 0])
    max_angle = 2 * (max_angle1 + max_angle2)
    return angle <= max_angle or angle >= pi - max_angle


def _angle(node1, node2):
    print node1, node2, '\t',
    v1 = map(int.__sub__, node1.root.pixel, node1.pixel)
    v2 = map(int.__sub__, node2.root.pixel, node2.pixel)
    return _vangle(v1, v2)


def _vangle(v1, v2):
    print v1, v2, _mag(v1), _mag(v2)
    tmp = sum(map(int.__mul__, v1, v2))/_mag(v1)/_mag(v2)
    if tmp > 1:
        tmp = 1
    if tmp < -1:
        tmp = -1
    return acos(tmp)


def _mag(v):
    return (sum(map(lambda a: a*a, v)))**0.5


class QueueObject(object):
    """Class to keep information about the line search."""
    dir_enable = {
        (-1, -1): set([(0, -1), (-1, -1), (-1, 0)]),
        (-1, 0): set([(-1, -1), (-1, 0), (-1, 1)]),
        (-1, 1): set([(-1, 0), (-1, 1), (0, 1)]),
        (0, 1): set([(-1, 1), (0, 1), (1, 1)]),
        (1, 1): set([(0, 1), (1, 1), (1, 0)]),
        (1, 0): set([(1, 1), (1, 0), (1, -1)]),
        (1, -1): set([(1, 0), (1, -1), (0, -1)]),
        (0, -1): set([(1, -1), (0, -1), (-1, -1)])
    }

    def __init__(self, pixel, parent, root, directions, length, pa):
        super(QueueObject, self).__init__()
        self.pixel = pixel
        self.parent = parent
        if root is None:
            root = self
        self.root = root
        if directions is None:
            directions = set([d for d in product([-1, 0, 1], [-1, 0, 1])
                             if d != (0, 0)])
        self.directions = directions
        self.length = length
        self.pa = pa

    def expand(self):
        children = []
        dirs = [d for d in self.directions if d[0] * d[1] == 0]
        dirs.extend([d for d in self.directions if d not in dirs])
        for direction in self.directions:
            new = tuple(map(lambda x, y: x+y, self.pixel, direction))
            try:
                if not _is_black(self.pa[new]):
                    new_dirs = self.directions.intersection(
                        self.dir_enable[direction])
                    children.append(QueueObject(new, self, self.root,
                                    new_dirs, self.length + 1, self.pa))
            except IndexError:
                pass
        self.children = children
        return children

    def __repr__(self):
        # dir_str = 'all' if len(self.directions) == 8 else str(self.directions)
        # return ''.join(('<',
        #                 repr(self.pixel), ', ',
        #                 repr(self.length), ', ',
        #                 dir_str, '>'))
        return '<' + ' '.join((str(self.root.pixel), '->', str(self.pixel))) + '>'


def _is_black(colour):
    return colour == 0


def threshold(image, threshold=0.9):
    # remove transparency
    image = image.convert("RGBA")
    pa = image.load()
    for p in product(xrange(image.size[0]), xrange(image.size[1])):
        colour = pa[p]
        if colour[-1] < 255 or sum(colour[:-1]) < 255 * 3 * threshold:
            pa[p] = (0, 0, 0, 255)
        else:
            pa[p] = (255, 255, 255, 255)
    image = image.convert("1")
    return image


# _neighbours, _transitions and _zhangSuen adapted from
# http://rosettacode.org/wiki/Zhang-Suen_thinning_algorithm
def _neighbours(x, y, image):
    '''Return 8-neighbours of point p1 of picture, in order'''
    i = image
    x1, y1, x_1, y_1 = x+1, y-1, x-1, y+1
    return [i[y1, x],  i[y1, x1],   i[y, x1],  i[y_1, x1],  # P2,P3,P4,P5
            i[y_1, x], i[y_1, x_1], i[y, x_1], i[y1, x_1]]  # P6,P7,P8,P9


def _transitions(neighbours):
    n = neighbours + neighbours[0:1]    # P2, ... P9, P2
    return sum((n1, n2) == (0, 255) for n1, n2 in zip(n, n[1:]))


def zhangSuen(image):
    _zhangSuen(image.load(), image.size[0], image.size[1])
    return image


def _zhangSuen(image, width, height):
    changing1 = changing2 = [(-1, -1)]
    while changing1 or changing2:
        # Step 1
        changing1 = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                P2, P3, P4, P5, P6, P7, P8, P9 = n = _neighbours(x, y, image)
                if (image[y, x] == 255 and          # (Condition 0)
                        P4 * P6 * P8 == 0 and       # Condition 4
                        P2 * P4 * P6 == 0 and       # Condition 3
                        _transitions(n) == 1 and     # Condition 2
                        2*255 <= sum(n) <= 6*255):  # Condition 1
                    changing1.append((x, y))
        for x, y in changing1:
            image[y, x] = 0
        # Step 2
        changing2 = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                P2, P3, P4, P5, P6, P7, P8, P9 = n = _neighbours(x, y, image)
                if (image[y, x] == 255 and          # (Condition 0)
                        P2 * P6 * P8 == 0 and       # Condition 4
                        P2 * P4 * P8 == 0 and       # Condition 3
                        _transitions(n) == 1 and     # Condition 2
                        2*255 <= sum(n) <= 6*255):  # Condition 1
                    changing2.append((x, y))
        for x, y in changing2:
            image[y, x] = 0
    return image


if __name__ == '__main__':
    import sys
    from PIL import Image
    from matplotlib import pyplot as plt
    for arg in sys.argv[1:]:
        im = Image.open(arg)
        print arg,
        lines = straight_lines(im)
        print 'lines:', len(lines)
        # print arg, [(node.root.pixel, node.pixel) for node in lines]

        im = Image.new("RGB", im.size)
        pa = im.load()
        for line in lines:
            plt.plot([line.root.pixel[0], line.pixel[0]],
                     [-line.root.pixel[1], -line.pixel[1]])
            node = line
            i = 0
            while node is not None:
                tmp = (line.length - i) * 255 / line.length
                pa[node.pixel] = (tmp, 255-tmp, 0)
                node = node.parent
                i += 1
        im.show()
        plt.show()
