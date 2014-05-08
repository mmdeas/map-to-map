from Queue import Queue
from itertools import product

MIN_LINE_LENGTH = 5

# TODO: deal with 45 degree angles


def straight_lines(im, visual=False):
    # threshold at 90%
    if visual:
        im = im.convert("RGBA")
        im.show()
    im = _threshold(im)
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

    def expand(self):
        children = []
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
        dir_str = 'all' if len(self.directions) == 8 else str(self.directions)
        return ''.join(('<',
                        repr(self.pixel), ', ',
                        repr(self.length), ', ',
                        dir_str, '>'))


def _is_black(colour):
    return colour == 0


def _threshold(image, threshold=0.9):
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
    image.show()
    pa = image.load()
    zhangSuen(pa, image.size[0], image.size[1])
    image.show()
    return image


# neighbours, transitions and zhangSuen modified from
# http://rosettacode.org/wiki/Zhang-Suen_thinning_algorithm
def neighbours(x, y, image):
    '''Return 8-neighbours of point p1 of picture, in order'''
    i = image
    x1, y1, x_1, y_1 = x+1, y-1, x-1, y+1
    return [i[y1, x],  i[y1, x1],   i[y, x1],  i[y_1, x1],  # P2,P3,P4,P5
            i[y_1, x], i[y_1, x_1], i[y, x_1], i[y1, x_1]]  # P6,P7,P8,P9


def transitions(neighbours):
    n = neighbours + neighbours[0:1]    # P2, ... P9, P2
    return sum((n1, n2) == (0, 255) for n1, n2 in zip(n, n[1:]))


def zhangSuen(image, width, height):
    changing1 = changing2 = [(-1, -1)]
    while changing1 or changing2:
        # Step 1
        changing1 = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                P2, P3, P4, P5, P6, P7, P8, P9 = n = neighbours(x, y, image)
                if (image[y, x] == 255 and          # (Condition 0)
                        P4 * P6 * P8 == 0 and       # Condition 4
                        P2 * P4 * P6 == 0 and       # Condition 3
                        transitions(n) == 1 and     # Condition 2
                        2*255 <= sum(n) <= 6*255):  # Condition 1
                    changing1.append((x, y))
        for x, y in changing1:
            image[y, x] = 0
        # Step 2
        changing2 = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                P2, P3, P4, P5, P6, P7, P8, P9 = n = neighbours(x, y, image)
                if (image[y, x] == 255 and          # (Condition 0)
                        P2 * P6 * P8 == 0 and       # Condition 4
                        P2 * P4 * P8 == 0 and       # Condition 3
                        transitions(n) == 1 and     # Condition 2
                        2*255 <= sum(n) <= 6*255):  # Condition 1
                    changing2.append((x, y))
        for x, y in changing2:
            image[y, x] = 0
    return image


if __name__ == '__main__':
    import sys
    from PIL import Image
    for arg in sys.argv[1:]:
        im = Image.open(arg)
        lines = straight_lines(im, True)
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
