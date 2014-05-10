from itertools import count
import urllib2
import re

from PIL import Image
from StringIO import StringIO


def building_to_image(bf):
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
            print "Requesting " + url.format(zoom, x, y)
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
                print "Requesting {0}".format((x, y))
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
        im = building_to_image(arg)
        im.save("bf{0}.png".format(arg))
