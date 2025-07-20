#!/usr/bin/env python
from sys import argv
bg_color white
cmd.load(argv[1], "m01", multiplex=1)
cmd.load(argv[2], "m02", multiplex=1)
hide all
print cmd.get_names("all")
cmd.color("red",cmd.get_names("all")[0])
cmd.color("blue",cmd.get_names("all")[1])
show cartoon
orient
set ray_opaque_background, off
set ray_trace_mode,0
set antialias,2
ray 
cmd.png("superimposed.png")