#! /usr/bin/python

from PIL import Image
import lines
import vmf
import sys
import dl

width = 5
height = 100

for arg in sys.argv[1:]:
    try:
        int(arg)
    except ValueError:
        print "Opening image...",
        im = Image.open(arg)
        print "done."
    else:
        print "Downloading image..."
        im = dl.building_to_image(arg)
        im.save(arg + ".png")
        print "Image downloaded."

    print "Thresholding...",
    im = lines.threshold(im)
    print "done."

    print "Thinning lines...",
    im = lines.zhangSuen(im)
    print "dong."

    print "Calculating lines..."
    straights = lines.straight_lines(im, True, True)
    print "Lines calculated."
    vmff = vmf.VMF(arg, True)
    minx = maxx = miny = maxy = 0
    print "Generating VMF..."
    print "Generating walls...",
    for line in straights:
        start = (line.root.pixel[0], line.root.pixel[1], 0)
        end = (line.pixel[0], line.pixel[1], 0)
        line = (start, end)
        minx = min(minx, start[0], end[0])
        maxx = max(maxx, start[0], end[0])
        miny = min(miny, start[1], end[1])
        maxy = max(maxy, start[1], end[1])
        vmff.add_solid(vmf.wall_from_line(line, width, height))

    print "done."
    print "Generating floors...",
    floor = vmf.floor_from_bounding_box(minx, maxx, miny, maxy, 0, 10)
    ceiling = vmf.floor_from_bounding_box(minx, maxx, miny, maxy, height, 10)
    vmff.add_solid(floor)
    vmff.add_solid(ceiling)
    print "done."

    vmff.write()
    print "VMF generated."
