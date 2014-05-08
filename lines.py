from Queue import Queue
from itertools import product

MIN_LINE_LENGTH = 5

# TODO: deal with 45 degree angles


def straight_lines(im, visual=False):
    # threshold at 90%
    im = im.convert("RGBA")
    if visual:
        im.show()
    im = im.convert("L")
    if visual:
        im.show()
    im = im.point(_threshold)
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
            exps = 0
            for child in children:
                if (child.pixel) not in expanded:
                    queue.put(child)
                else:
                    exps += 1
            if len(children) == exps and node.length > MIN_LINE_LENGTH:
                lines.append((node.root, node))
    lines_by_se = {}
    for line in lines:
        try:
            lines_by_se[(line[0].pixel, line[1].pixel)].append(line)
        except KeyError:
            lines_by_se[(line[0].pixel, line[1].pixel)] = [line]
    for se in lines_by_se:
        for line in lines_by_se[se][1:]:
            lines.remove(line)
    return lines


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
        if root.pixel == (33, 57):
          print self, parent

    def expand(self):
        children = []
        for direction in self.directions:
            new = tuple(map(lambda x, y: x+y, self.pixel, direction))
            try:
                if not _is_black(self.pa[new]):
                    new_dirs = self.directions.intersection(self.dir_enable[direction])
                    children.append(QueueObject(new, self, self.root,
                                    new_dirs, self.length + 1, self.pa))
            except IndexError:
                pass
        return children

    def __repr__(self):
        dir_str = 'all' if len(self.directions) == 8 else str(self.directions)
        return ''.join(('<', repr(self.pixel), ', ', repr(self.length), ', ', dir_str, '>'))


def _is_black(colour):
    return colour == 0


def _threshold(image, percentage=90):
    return (pixel > 255 * percentage / 100) * 255


if __name__ == '__main__':
    import sys
    from PIL import Image
    for arg in sys.argv[1:]:
        im = Image.open(arg)
        lines = straight_lines(im)
        print arg, 'lines:', len(lines)
        im = Image.new("RGB", im.size)
        pa = im.load()
        for line in lines:
            node = line[1]
            i = 0
            while node is not None:
                tmp = (line[1].length - i) * 255 / line[1].length
                pa[node.pixel] = (tmp, 255-tmp, 0)
                node = node.parent
                i += 1
        im.show()
