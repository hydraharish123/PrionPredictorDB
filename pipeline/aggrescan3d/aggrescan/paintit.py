#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pymol
from pymol import cmd, stored, util


pymol_mode = sys.argv[1]
pdb_file = sys.argv[2]
output_file = sys.argv[3]

try:
    pdb_code = pdb_file.split('/')[1].split('.')[0]
except IndexError:
    pdb_code = pdb_file.split('.')[0]
    
if pymol_mode == "s":
    pymol.pymol_argv = ['pymol','-qc'] # PyMol quiet launch without GUI
    out_folder = sys.argv[4]

fh = open(output_file, "r")
lines = fh.readlines()

pymol.finish_launching()
cmd.load(pdb_file)
#cmd.remove("HET")
cmd.set_name(pdb_code, pdb_code+'_A3D')
cmd.hide("all")
cmd.show("surface", "all")
cmd.color("white", "all")

#define the reds
cmd.set_color("red1", [1, 0,   0  ])  # most intense red
cmd.set_color("red2", [1, 0.2, 0.2])
cmd.set_color("red3", [1, 0.4, 0.4])
cmd.set_color("red4", [1, 0.6, 0.6])
cmd.set_color("red5", [1, 0.8, 0.8])  # lightest red

#define the blues
cmd.set_color("blue1", [0,   0,   1])  # most intense blue
cmd.set_color("blue2", [0.2, 0.2, 1])
cmd.set_color("blue3", [0.4, 0.4, 1])
cmd.set_color("blue4", [0.6, 0.6, 1])
cmd.set_color("blue5", [0.8, 0.8, 1])  # lightest blue

high_score = 0
high_res = -1500100900
for line in lines[1:]:
    if not (line == "\n" or line.startswith('#')):
        line_params = line.strip().replace('//', '').split(" ")
        score = float(line_params[3])

        chain = line_params[0]
        if chain == '-':
            my_res = "resi " + line_params[1]
        else:
            my_res = "chain " + line_params[0] + " and resi " + line_params[1]

        if score > 0:  # residues with a value above 0 will be colored red
            if score < 0.5:
                cmd.color("red4", my_res)    
            elif score < 1:
                cmd.color("red3", my_res)
            elif score < 1.5:
                cmd.color("red2", my_res)
            else:
                cmd.color("red1", my_res)
            if score > high_score:
                high_score = score
                high_res = my_res
        elif score < -0.5:  # residues with a value below -0.5 will be colored blue
            if score > -1:
                cmd.color("blue5", my_res)
            elif score > -1.5:
                cmd.color("blue4", my_res)
            elif score > -2:
                cmd.color("blue3", my_res)
            elif score > -2.5:
                cmd.color("blue2", my_res)
            else:
                cmd.color("blue1", my_res)

# create an object for the high score hot spot of the protein
if high_res != -1500100900:
    cmd.create("hot_spot", "("+high_res+",byres "+high_res+" around 5 and not HET \
    and not color white and not color blue1 and not color blue2 and not color blue3 \
    and not color blue4 and not color blue5)")

stored.neighbours=[]
cmd.iterate("(hot_spot & n. ca)", "stored.neighbours.append((resi,resn))")
cmd.reset()


# Save PyMol session
if pymol_mode == "s":
    cmd.viewport("640", "480")
    cmd.origin()
    cmd.set("field_of_view",30)
    cmd.set("surface_quality", "1")
    cmd.set("ray_trace_mode", "1")
    cmd.bg_color("white")
    cmd.set("antialias", "2")
    for xx in range(1, 19):
	cmd.rotate("y", 20)
        cmd.ray("640", "480")
	cmd.png("mov%05d.png" % (xx))


    cmd.quit()
