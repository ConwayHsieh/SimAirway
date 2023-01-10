#!/usr/bin/python3

from solid import *
from solid.utils import *

d = difference()(
  cube(size = 10, center = True),
  sphere(r = 6.5, segments=300)
)
path = scad_render_to_file(d, 'solidpython_example_01.scad')