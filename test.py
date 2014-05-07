#! /usr/bin/python

from PIL import Image
import lines
import vmf
import sys

width = 20
height = 100

for arg in sys.argv[1:]:
    im = Image.open(arg)
    lines = lines.straight_lines(im)
    fout = file(arg + '.vmf', 'w')
    fout.write(vmf.header())
    for line in lines:
        start = (line[0].pixel[0], line[0].pixel[1], 0)
        end = (line[1].pixel[0], line[1].pixel[1], 0)
        line = (start, end)
        fout.write(vmf.wall_from_line(line, width, height))
    fout.close()
