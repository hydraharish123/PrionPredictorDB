# -*- coding: utf-8 -*-

import os
from os.path import join, abspath
from subprocess import PIPE, Popen
from pkg_resources import resource_filename
from aggrescan_3d import run as run_aggrescan_3d
import logger
import platform

_name = "Analysis"
if platform.system() == "Windows":
    _bin_name = "freesasa.exe"
elif platform.system() == "Darwin":
    _bin_name = "freesasa_Darwin"
else:
    _bin_name = "freesasa"


def aggregation_analysis(config, target="input.pdb", working_dir=".", agg_work_dir=""):
    """Takes Aggrescaan3D Job class config as an argument and should never change it"""
    os.chdir(working_dir)  # Just in case one of the programs handles abspaths poorly
    if config["naccess"]:
        _run_naccess(target=target, agg=agg_work_dir, naccess_dir=config["naccess"])
    else:
        _run_free_sasa(target=target, agg=agg_work_dir)
    _run_aggrescan(target=target, working_dir=working_dir, config=config)


def _run_aggrescan(target, working_dir, config):
    """
    Takes target pdb file, working directory for analysis
    and aggrescan config dict as arguments so need the two in sync
    """
    logger.info(module_name=_name, msg="Starting Aggrescan3D on %s" % target.split("/")[-1])
    logger.debug(module_name=_name, msg="Running Aggrescan3D program on %s" % abspath(target))
    matrix_dir = resource_filename('aggrescan', join("data", "matrices", "aggrescan.mat"))
    out = run_aggrescan_3d(target, matrix_dir, config["distance"], working_dir, naccess=config["naccess"],
                           ph=config['ph'])
    logger.to_file(filename=join(config["tmp_dir"], "input_output"), content=out, allow_err=False)


def _run_free_sasa(target="folded.pdb", agg=""):
    sasa_dir = resource_filename('aggrescan', join("data", "freesasa-2.0.1", "src", _bin_name))
    sasa_cmd = [sasa_dir, "--resolution", "100", target, "--radii", "naccess", "--format", "pdb", "--format", "rsa"]
    logger.debug(module_name="freeSasa", msg="Starting freeSasa with %s" % " ".join(sasa_cmd))
    _fname = join(agg, "ASA.error")
    out, err = Popen(sasa_cmd, stdout=PIPE, stderr=PIPE).communicate()
    if err:
        logger.to_file(_fname, content=err)
        for line in err.split("\n"):
            if "warning" in line:
                logger.critical(module_name="freeSasa", msg="Warning detected: %s" % line)
                logger.critical(module_name="freeSasa", msg="Attempting to continue.")
            else:
                raise logger.ASAError(program_name="freeSasa", filename=_fname)
    logger.to_file(filename="sasa.out", content=out, allow_err=False)


def _run_naccess(target="folded.pdb", agg="", naccess_dir=""):
    naccess_cmd = [naccess_dir, target, "-p", "1.4", "-z", "0.05"]
    logger.debug(module_name=_name, msg="running naccess program with %s" % " ".join(naccess_cmd))
    _fname = join(agg, "ASA.error")
    try:
        out, err = Popen(naccess_cmd, stdout=PIPE, stderr=PIPE).communicate()
    except OSError:
        raise logger.AggrescanError("Couldn't start the naccess program. Naccess requires csh shell to be present on the system."
                                    " If it is present please run the program in debug mode and see if the path printed in "
                                    "Naccess command actually contains the file.", module_name="Naccess")
    if err:
        logger.to_file(filename=_fname, content=err)
        raise logger.ASAError(program_name="Naccess", filename=_fname)
    try:
        for msg in out.split("\n"):
            if msg:
                logger.debug(module_name="Naccess", msg=msg)
    except AttributeError:
        pass

