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
        raise ValueError("Arguments must be building identifiers (ints).")

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
            im = Image.open(''.join((arg, ext, '.png')))
        except IOError:
            pass
        else:
            # and then apply remaining functions (and cache at each step)
            funcs = funcs[:i]
            while funcs:
                func, ext = funcs.pop()
                im = func(im)
                im.save('.'.join((arg, ext, '.png')))
            break

    # if still not found, download
    if im is None:
        im = dl.building_to_image(arg)
        while funcs:
            func, ext = funcs.pop()
            im = func(im)
            im.save(''.join((arg, ext, '.png')))

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
