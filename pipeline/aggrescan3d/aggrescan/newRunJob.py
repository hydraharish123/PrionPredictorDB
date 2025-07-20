#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import json
from pkg_resources import resource_filename
from subprocess import Popen, PIPE
from os.path import exists, isdir, join, isfile
import logger
import pdb
from postProcessing import prepare_output
from analysis import aggregation_analysis as analyze
from dynamic_module import run_cabs
from foldx_module import FoldxWrap as fold
from glob import glob
from optparser import save_config_file
from auto_mutation import run_auto_mutation

__all__ = ["Job"]
_name = "runJob"


'''
Note to future self:
The Job atributes are kinda global variables here they  

Pdb files fate during simulation is as follows:
original_input.pdb is kept during all the simulation and then renamed as input.pdb 
input.pdb is the foldx result at each simulation stage, and is the "current" file
folded.pdb is a product of calculations usually soon renamed to input.pdb
output.pdb is the final product of the simulation 
Whole thing is a mess mostly due to how foldx works (which has now improved but this program is still behind on it)
'''


class Job:
    def __init__(self, config):
        for argName, argValue in config.items():
            setattr(self, argName, argValue)
            logger.debug(module_name=_name, msg="Setting %s to %s" % (argName, argValue))
        self.config = config
        if exists(self.work_dir):
            if not isdir(self.work_dir):
                raise logger.AggrescanError('Selected working directory: %s already exists and is not a directory. '
                                            'Quitting.' % self.work_dir,
                                            module_name=_name,
                                            work_dir_error=True)
            if self.overwrite and isfile(join(self.work_dir, "output.pdb")):
                raise logger.AggrescanError("The --overwrite options was seen. "
                                            "\nStopping the program to avoid overwriting files "
                                            "(workdir exists and contains output.pdb).",
                                            module_name=_name,
                                            work_dir_error=True)
            else:
                logger.warning(module_name=_name,
                               msg='Working directory already exists (possibly overwriting previous results -ow '
                                   'to prevent this behavior)')
        else:
            try:
                os.makedirs(self.work_dir)
            except OSError:
                raise logger.AggrescanError("Could not create working directory at %s" % self.work_dir,
                                            module_name=_name,
                                            work_dir_error=True)
        try:
            os.mkdir(self.tmp_dir)
        except OSError:
            pass
        if self.foldx:
            self.foldx_handler = fold(foldx_dir=self.foldx, work_dir=self.work_dir,
                                      skip_minimization=self.subprocess, ph=self.ph)
        save_config_file(config=config, work_dir=self.work_dir)

    def run_job(self):
        logger.info(module_name=_name, msg='Starting aggrescan3d job on: %s with %s chain(s) selected' %
                                           (self.protein, self.chain or "all"))
        logger.info(module_name=_name, msg="Creating pdb object from: %s" % self.protein)
        pdbObj = pdb.Pdb(self.protein, output=join(self.work_dir, 'input.pdb'), chain=self.chain)
        pdbObj.validate()
        pdbObj.savePdbFile(path=join(self.work_dir, "original_input.pdb"))
        pdbObj.savePdbFile(path=join(self.tmp_dir, "input.pdb"))
        if self.mutate:
            if self.foldx:
                mutation = self.find_mutations(pdb_obj=pdbObj)
                self.foldx_handler.build_mutant(working_dir=self.tmp_dir, mutation_list=mutation)
            else:
                raise logger.AggrescanError("FoldX required for mutation analysis. To run aggrescan on a mutant without"
                                            " FoldX provide a mutant pdb file and run Aggrescan3D on it.",
                                            module_name=_name)

        if self.foldx:
            self.foldx_handler.minimize_energy(working_dir=self.tmp_dir)
        else:
            logger.info(module_name=_name,
                        msg="FoldX not utilized. Treating input pdb file as it was already optimized.")
            pdbObj.savePdbFile(path=join(self.tmp_dir, "folded.pdb"))

        if self.dynamic:
            os.chdir(self.work_dir)
            shutil.move(join(self.tmp_dir, "folded.pdb"), "input.pdb")
            run_cabs(config=self.config)
            shutil.move(join(self.work_dir, "folded.pdb"), join(self.tmp_dir, "folded.pdb"))
        analyze(config=self.config, target="folded.pdb", working_dir=self.tmp_dir, agg_work_dir=self.work_dir)
        if self.movie:
            self.create_movie()
        self.post_processing(work_dir=self.tmp_dir, final=True, model_name="folded")
        self.cleanup()
        if self.auto_mutation:
            self.check_auto_mut(pdb_obj=pdbObj)     # This will also modify the auto_mutation excluded part slightly
            run_auto_mutation(work_dir=self.work_dir, options=self.auto_mutation,
                              foldx_loc=self.foldx, distance=self.distance, ph=self.ph)

    def post_processing(self, work_dir="", final=True, model_name="folded"):    # TODO remove this function?
        prepare_output(work_dir=work_dir, final=final, model_name=model_name)

    def find_mutations(self, pdb_obj=None):
        chain_numbering = pdb_obj.getChainIdxResname()
        t = json.loads(chain_numbering)
        to_mutate = []
        for row in self.mutate:
            oi = str(row['idx'])
            on = str(row['oldres'])
            nn = str(row['newres'])
            ch = str(row['chain'])
            found = False
            try:
                for r in t[ch]:
                    if r['resname'] == on and r['chain'] == ch \
                            and r['residx'] == oi:
                        to_mutate.append(on + ch + oi + nn)
                        found = True
                        break
            except KeyError:
                logger.warning(module_name=_name, msg="Mutation %s likely tried to mutate a chain "
                                                      "that doesn't exist." % json.dumps(row))
                logger.info(module_name=_name, msg="Available chains: %s" % t.keys())

            if not found:
                logger.warning(module_name=_name, msg="Could not find the requested mutation: %s" % json.dumps(row))
        if len(to_mutate) == 0:
            raise logger.AggrescanError("Mutations table provided but its parsing failed. "
                                        "Most likely all the provided mutations were incorrect "
                                        "(referring to non existing residues, numbering errors, etc.)",
                                        module_name=_name)
        mutation = ",".join(to_mutate).strip() + ";"
        logger.debug(module_name=_name, msg="Mutation list: %s" % mutation)
        return mutation

    def check_auto_mut(self, pdb_obj=None):
        print self.auto_mutation
        if len(self.auto_mutation) > 2:
            chain_numbering = pdb_obj.getChainIdxResname()
            t = json.loads(chain_numbering)
            counted = 0
            for row in self.auto_mutation[2]:
                oi = str(row['idx'])
                ch = str(row['chain'])
                found = False
                try:
                    for r in t[ch]:
                        if r['chain'] == ch \
                                and r['residx'] == oi:
                            found = True
                            counted += 1
                            break
                except KeyError:
                    logger.warning(module_name="Auto_mut", msg="Attempted to exclude a residue that probably"
                                                               "doesn't exist. (%s)" % json.dumps(row))
                    logger.info(module_name="Auto_mut", msg="Available chains: %s" % t.keys())

                if not found:
                    logger.warning(module_name="Auto_mut", msg="Couldn't find the residue number %s in chain %s to exclude from "
                                                               "auto mutation" % (oi, ch))
            if counted == 0:
                logger.critical(msg="Residues to exclude from automated mutations provided but none "
                                            "could be found in the pdb file.",
                                            module_name="Auto_mut")
            # Parse it into "mutation syntax" for easier comparisons later on
            self.auto_mutation = list(self.auto_mutation)
            self.auto_mutation[2] = [i['idx'] + i["chain"] for i in self.auto_mutation[2]]

    def cleanup(self):
        """Move output from the temporary directory to work directory before the former is deleted"""
        os.chdir(self.tmp_dir)
        shutil.move(join(self.tmp_dir, "A3D.csv"), join(self.work_dir, "A3D.csv"))
        shutil.move(join(self.tmp_dir, "output.pdb"), join(self.work_dir, "output.pdb"))
        shutil.move(join(self.tmp_dir, "folded_stats"), join(self.work_dir, "A3D_summary.json"))
        shutil.move(join(self.work_dir, "original_input.pdb"), join(self.work_dir, "input.pdb"))
        extensions = [".svg", ".png"]
        for ext in extensions:
            for f in glob("*%s" % ext):
                shutil.move(f, join(self.work_dir, f))

    def create_movie(self):
        """
        First uses paintit.py to create movie frame png, then run avconv to create a movie
        This is a legacy function while it should work it's no longer really relevant or updated/tested
        """
        os.chdir(self.tmp_dir)
        pymCmd = "pymol -qc %s -- s input.pdb input_output ." % resource_filename("aggrescan", join("data", "paintit.py"))
        logger.debug(module_name="pyMol", msg="Pymol ran with: %s" % pymCmd)

        try:
            out,err = Popen(pymCmd,stdout=PIPE,stderr=PIPE,shell=True).communicate()
            if err:
                logger.critical(module_name="pyMol",
                                        msg="Pymol encountered an error: %s Movie creation failed." % err.strip("\n"))
                return
        except OSError as e:
            logger.debug(module_name="pyMol", msg="Exception caught: %s" % e)
            logger.critical(module_name="pyMol", msg="OSError while launching pymol. Perhaps it's not installed?")
            return

        self.movie = self.movie.strip()
        if self.movie == "mp4":
            av_cmd = 'avconv  -r 8 -i mov%05d.png  -vcodec libx264 -pix_fmt yuv420p -profile:v baseline ' \
                     '-preset slower -crf 18 -vf "scale=trunc(in_w/2)*2:trunc(in_h/2)*2" clip.mp4'
            logger.info(module_name="Movie",msg="Creting movie with %s format" % self.movie)
        elif self.movie == "webm":
            av_cmd = 'avconv  -r 8 -i mov%05d.png -c:v libvpx -c:a libvorbis -pix_fmt yuv420p ' \
                     '-b:v 2M -crf 5 -vf "scale=trunc(in_w/2)*2:trunc(in_h/2)*2" clip.webm'
            logger.info(module_name="Movie",msg="Creting movie with %s format" % self.movie)
        else:
            logger.warning(module_name="Movie",msg="Wrong movie format specified: %s Using webm instead." % self.movie)
            av_cmd = 'avconv  -r 8 -i mov%05d.png -c:v libvpx -c:a libvorbis -pix_fmt yuv420p ' \
                     '-b:v 2M -crf 5 -vf "scale=trunc(in_w/2)*2:trunc(in_h/2)*2" clip.webm'
            self.movie = "webm"

        try:
            logger.debug(module_name="Avconv", msg="Avconv ran with: %s" % av_cmd)
            out, err = Popen(av_cmd,stdout=PIPE, stderr=PIPE, shell=True).communicate()
            if err:
                logger.debug(module_name="Avconv",
                                    msg="Avconv output: %s" % err.strip("\n"))
            if self.movie == "mp4":
                shutil.move("clip.mp4", join(self.work_dir,"clip.mp4"))
            else:
                shutil.move("clip.webm", join(self.work_dir,"clip.webm"))

        except OSError as e:
            logger.critical(module_name="Avconv", msg="OSError while launching avconv. Perhaps it's not installed?")
            logger.debug(module_name="Avconv", msg="Exception caught: %s" % e)

        except IOError as e2:
            logger.critical(module_name="Avconv", msg="Couldn't move the clip to working directory. "
                                                      "Movie creation likely failed")
            logger.debug(module_name="Avconv", msg="Exception caught: %s" % e2)

        finally:
                file_list = os.listdir(self.tmp_dir)
                for f in file_list:
                    if ".png" in f:
                        os.remove(f)

    def get_tempdir(self):
        return self.tmp_dir
