from Queue import Queue
from itertools import product

MIN_LINE_LENGTH = 0


def straight_lines(im):
    # threshold at 90%
    im = im.convert("L")
    im = im.point(_threshold)
    pa = im.load()
    expanded = set()
    queue = Queue()
    lines = []
    # iterate over all pixels
    for pixel in product(xrange(im.size[0]),
                         xrange(im.size[1])):
        # add unexpanded white pixels to queue for each direction
        if not _is_black(pa[pixel]):
            for direction in range(4):
                if (pixel, direction) not in expanded:
                    qo = QueueObject(pixel, None, None, direction, 0, pa)
                    queue.put(qo)
        while not queue.empty():
            node = queue.get()
            expanded.add((node.pixel, direction))
            children = node.expand()
            for child in children:
                if (child.pixel, direction) not in expanded:
                    queue.put(child)
            if len(children) == 0 and node.length > MIN_LINE_LENGTH:
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
    # direction: 0 -> UP, 1 -> RIGHT, 2 -> DOWN, 3 -> LEFT
    def __init__(self, pixel, parent, root, direction, allowed, length, pa):
        super(QueueObject, self).__init__()
        self.pixel = pixel
        self.parent = parent
        if root is None:
            root = self
        self.root = root
        self.direction = direction
        if allowed is None:
            allowed = [1, 1]
        self.length = length
        self.pa = pa

    def expand(self):
        # pixels is iter of poss child pixels
        # UP
        if self.direction == 0:
            pixels = [(x, self.pixel[1] - 1)
                      for x in range(self.pixel[0] - 1, self.pixel[0] + 2)]
            allowed = []
        # RIGHT
        elif self.direction == 1:
            pixels = list(product([self.pixel[0] + 1],
                                  range(self.pixel[1] - 1, self.pixel[1] + 2)))
        # DOWN
        elif self.direction == 2:
            pixels = list(product(range(self.pixel[0] - 1, self.pixel[0] + 2),
                                  [self.pixel[1] + 1]))
        # LEFT
        elif self.direction == 3:
            pixels = list(product([self.pixel[0] - 1],
                                  range(self.pixel[1] - 1, self.pixel[1] + 2)))

        children = []
        for pixel in pixels:
            try:
                if not _is_black(self.pa[pixel]):
                    children.append(QueueObject(pixel, self, self.root,
                                    self.direction, self.length + 1, self.pa))
            except IndexError:
                pass
        return children

    def __repr__(self):
        return ''.join(('<', str(self.pixel), ', ', str(self.direction), '>'))


def _is_black(colour):
    return colour == 0


def _threshold(pixel, percentage=90):
        return (pixel > 255 * percentage / 100) * 255


if __name__ == '__main__':
    import sys
    from PIL import Image
    for arg in sys.argv[1:]:
        im = Image.open(arg)
        im = im.convert('RGBA')
        im.show()
        lines = straight_lines(im)
        print arg, 'lines:', len(lines)
        print arg, lines
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
