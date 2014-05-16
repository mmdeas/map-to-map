#! /usr/bin/python

import pickle

from PIL import Image, ImageDraw

import lines
import vmf
import sys
import dl

width = 5
height = 150


for arg in sys.argv[1:]:
    try:
        int(arg)
    except ValueError:
        raise ValueError("Arguments must be building identifiers (ints).")

    try:
        print "Trying to get .bfs file."
        bfs = pickle.load(file(arg + ".bfs"))
    except IOError:
        print "No .bfs file. Downloading building instead."
        images = dl.building_to_images(arg)
    else:
        print "Found bfs:", bfs
        images = []
        for bf in bfs:
            images.append(dl.get_processed_image(bf))

    z = 0
    print "Generating VMF..."
    vmff = vmf.VMF(arg, True)
    minx = miny = 1e6
    maxx = maxy = -1e6
    for im in images:
        print "Calculating lines..."
        straights = lines.straight_lines(im)
        print "Lines calculated."
        print "Generating walls...",
        out = Image.new("RGB", im.size)
        draw = ImageDraw.Draw(out)
        count = {}
        pickle.dump([(line.root.pixel, line.pixel) for line in straights],
                    file(arg + ".lines", 'w'))
        for line in straights:
            start = (line.root.pixel[0], line.root.pixel[1], z)
            end = (line.pixel[0], line.pixel[1], z)
            try:
                count[start] += 1
            except KeyError:
                count[start] = 1
            try:
                count[end] += 1
            except KeyError:
                count[end] = 1
            line = (start, end)
            minx = min(minx, start[0], end[0])
            maxx = max(maxx, start[0], end[0])
            miny = min(miny, start[1], end[1])
            maxy = max(maxy, start[1], end[1])
            vmff.add_solid(vmf.wall_from_line(line, width, height))
            draw.line((start[0], start[1], end[0], end[1]), (255, 0, 0))
            draw.point(start[:2], (0, 0, 255))
            draw.point(end[:2], (0, 0, 255))
        for pixel in [p for p in count if count[p] > 1]:
            draw.point(pixel[:2], (0, 255, 0))
        out.show()

        print "done."
        print "Generating floors...",
        floor = vmf.floor_from_bounding_box(minx, maxx, miny, maxy, z, 10)
        ceiling = vmf.floor_from_bounding_box(minx, maxx, miny, maxy,
                                              z + height, 10)
        vmff.add_solid(floor)
        vmff.add_solid(ceiling)
        print "done."
        z += height

    vmff.write()
    print "VMF generated."
