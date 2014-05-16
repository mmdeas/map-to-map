from itertools import count
import pickle
import urllib2
import re
from StringIO import StringIO

from PIL import Image

import lines


def building_to_images(bf):
    request = urllib2.urlopen("http://campus.warwick.ac.uk/?bf={0}".format(bf))
    if request.getcode() != 200:
        raise BuildingError("Received code from server: " + request.getcode())
    html = request.read()
    m = re.findall(r"<option value='(\d+)'", html)
    if not m:
        raise BuildingError("Could not find list of floors.")
    # initiate with current floor
    floor_bfs = [bf]
    # ignore first because it is link back to campus map
    floor_bfs.extend(m[2:])
    pickle.dump(floor_bfs, file(bf + ".bfs", 'w'))
    images = []
    for bf in floor_bfs:
        images.append(get_processed_image(bf))
    return images


def get_processed_image(bf):
    print "get_processed_image({0})".format(bf)
    # list of functions and extensions which should be applied
    funcs = [
        (lines.zhangSuen, '.zs'),
        (lines.threshold, '.th'),
        (lambda a: a, '')
        ]

    # try to find the most advanced cached image
    im = None
    for i, tup in zip(range(len(funcs)), funcs):
        ext = tup[1]
        try:
            fname = ''.join((bf, ext, '.png'))
            im = Image.open(fname)
        except IOError:
            pass
        else:
            print "Found {0}. Applying functions from there.".format(fname)
            # and then apply remaining functions (and cache at each step)
            funcs = funcs[:i]
            while funcs:
                func, ext = funcs.pop()
                print "Applying", func, "...",
                im = func(im)
                print "done."
                im.save(''.join((bf, ext, '.png')))
            break

    # if still not found, download
    if im is None:
        print "No image found for {0}. Downloading...".format(bf),
        im = floor_to_image(bf)
        print "done."
        while funcs:
            func, ext = funcs.pop()
            print "Applying", func, "...",
            im = func(im)
            print "done."
            im.save(''.join((bf, ext, '.png')))

    return im


def floor_to_image(bf):
    request = urllib2.urlopen("http://campus.warwick.ac.uk/?bf={0}".format(bf))
    if request.getcode() != 200:
        raise BuildingError("Received code from server: " + request.getcode())
    html = request.read()
    m = re.search(r"map.prepareViewer\('(.*?)'", html)
    if m is None:
        raise BuildingError("Could not find map preparation.")
    path = m.group(1)
    m = re.search(r"map.setMaxZoom\((\d+)\)", html)
    if m is None:
        raise BuildingError("Could not find zoom level.")
    zoom = int(m.group(1))
    base = "http://campus.warwick.ac.uk/{0}"
    base = base.format(path)
    tile = "tile-{0}-{1}-{2}.png"
    url = '/'.join((base, tile))
    tiles = []
    # first line
    y = 0
    x = 0
    try:
        while True:
            # print "Requesting " + url.format(zoom, x, y)
            request = urllib2.urlopen(url.format(zoom, x, y))
            success = request.getcode() == 200
            if success:
                img = StringIO(request.read())
                img = Image.open(img)
                if x == 0:
                    tiles.append([])
                tiles[-1].append(img)
            else:
                print "Not successful but didn't error."
                print "\t", request
            x += 1
    except urllib2.HTTPError:
        pass
    x_stop = x
    print "Received full first row: {0} items".format(x_stop)

    try:
        for y in count(1):
            for x in range(x_stop):
                # print "Requesting {0}".format((x, y))
                print '.',
                request = urllib2.urlopen(url.format(zoom, x, y))
                if request.getcode() != 200:
                    raise TileError(request)
                img = Image.open(StringIO(request.read()))
                if x == 0:
                    tiles.append([])
                tiles[-1].append(img)
    except urllib2.HTTPError:
        if x != 0:
            raise TileError(request)

    import pickle
    pickle.dump(tiles, file("tiles.pickle", 'wb'))

    canvas = Image.new("RGBA", (256 * x_stop, 256 * y))
    for y in range(len(tiles)):
        for x in range(len(tiles[y])):
            tile = tiles[y][x].convert("RGBA")
            canvas.paste(tile, (256 * x, 256 * y))
    return canvas


class BuildingError(Exception):
    pass


class TileError(Exception):
    pass


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        imgs = building_to_images(arg)
        for im in imgs:
            im.save("bf{0}.png".format(arg))
