# -*- coding: utf-8 -*-

import os
import errno
import shutil
import logger
from os.path import join, abspath
from subprocess import Popen, PIPE
from glob import glob
from pkg_resources import resource_filename
import json
import tarfile
from postProcessing import prepare_output
from analysis import aggregation_analysis as analyze
from collections import OrderedDict

_name = "CABS"


def run_cabs(config, pdb_input="input.pdb"):
    """Takes an Aggrescan3D Job config dictionary and should never change it"""
    real_work_dir = config["work_dir"]
    os.chdir(real_work_dir)
    real_cabs_dir = os.path.join(real_work_dir, "CABS_sim")
    real_models_dir = os.path.join(real_cabs_dir, "output_pdbs")
    try:
        _makedir(real_cabs_dir)
        _makedir("models")
        _makedir("stats")
        shutil.copyfile(pdb_input, os.path.join(real_cabs_dir,
                                                pdb_input))
    except OSError:
        raise logger.CabsError("Failed to prepare CABS directory at: %s" % real_cabs_dir)

    os.chdir(real_cabs_dir)
    logger.info(module_name=_name,
                msg="Running CABS flex simulation")
    cabs_cmd = _prepare_command(pdb_input=pdb_input, cabs_dir=config["cabs_dir"],
                                cabs_config=config["cabs_config"], n_models=config["n_models"])
    logger.debug(module_name=_name,
                 msg="CABS ran with: %s" % " ".join(cabs_cmd))
    out, err = Popen(cabs_cmd, stdout=PIPE, stderr=PIPE).communicate()
    if err:
        with open(join(real_work_dir, "CABSerror"), 'w') as f:
            f.write(err)
        _cleanup_files(work_dir=real_work_dir, cabs_dir=real_cabs_dir, clean=False)
        raise logger.CabsError("Please see CABSerror file within your work directory for more details",
                               err_file="CABSerror")
    try:
        _check_output(models_dir=real_models_dir, n_models=config["n_models"])
    except logger.CabsError:
        shutil.move(join(real_cabs_dir, "CABS.log"), join(real_work_dir, "CABS.log"))
        _cleanup_files(work_dir=real_work_dir, cabs_dir=real_cabs_dir, clean=False)
        raise logger.CabsError("Please see CABS.log file within your work directory for more details",
                               err_file="CABS.log")

    shutil.copyfile(pdb_input, join("output_pdbs", pdb_input))
    os.chdir("output_pdbs")
    models = glob("model*.pdb")
    top = ""
    max_avg = -100
    averages = {}
    all_models_data = []
    for model in models:
        model_path = abspath(model)
        analyze(config=config, target=model_path, working_dir=real_models_dir, agg_work_dir=real_work_dir)
        data, stats = prepare_output(work_dir=real_models_dir, final=False,
                                     model_name=model.split(".")[0], scores_to_pdb=True, get_data=True)
        all_models_data.append(data["All"])
        current_avg = stats["All"]["avg_value"]
        averages[model] = current_avg
        if current_avg > max_avg:
            max_avg = stats["All"]["avg_value"]
            top = model
        shutil.move("A3D.csv", join(real_work_dir, "stats", model.split(".")[0] + ".csv"))
        shutil.move(model, join(real_work_dir, "models", model))
    analyze(config=config, target=pdb_input, working_dir=real_models_dir, agg_work_dir=real_work_dir)
    stats = prepare_output(work_dir=real_models_dir, final=False,
                           model_name=pdb_input.split(".")[0], scores_to_pdb=True, get_data=False)
    current_avg = stats["All"]["avg_value"]
    averages[pdb_input] = current_avg
    if current_avg > max_avg:
        top = pdb_input

    shutil.copyfile(pdb_input, "CABS_average.pdb")  # Create a "fake" average model from input
    with open("A3D.csv", 'r') as f:
        a3d_file_backup = f.readlines()

    shutil.move("A3D.csv", join(real_work_dir, "stats", pdb_input.split(".")[0] + ".csv"))
    shutil.move(pdb_input, join(real_work_dir, "models", pdb_input))    # Move the actual input out

    _create_avg_A3D(all_models_data, a3d_file_backup, real_models_dir)   # Create a "fake" A3D file that has averages of all CABS models for each residue
    stats = prepare_output(work_dir='', final=False,
                           model_name="CABS_average", scores_to_pdb=True, get_data=False)
    shutil.move("CABS_average.pdb", join(real_work_dir, "models", "CABS_average.pdb"))
    shutil.move("A3D.csv", join(real_work_dir, "stats", "CABS_average" + ".csv"))
    averages["CABS_average.pdb"] = stats["All"]["avg_value"]
    with open('averages', 'w') as avg:
        json.dump(_sort_dict(my_dict=averages), avg)

    os.chdir(real_work_dir)
    _cleanup_files(work_dir=real_work_dir, cabs_dir=real_cabs_dir, input_pdb=pdb_input, top=top, clean=True)
    superimpose(first_model="input.pdb", second_model="folded.pdb")


def _create_avg_A3D(data, a3d_content, work_dir):
    """Assuming the order is the same in data and a3d_content this should be the case as data is read from an A3D file"""
    new_data = [0 for i in range(len(data[0]))]
    for model in data:
        for res_index in range(len(model)):
            new_data[res_index] += model[res_index][1]
    new_data = [i/len(data) for i in new_data]
    with open(join(work_dir, "A3D.csv"), "w") as f:
        counter = 0
        first = True
        suma = 0
        for line in a3d_content:
            if first is True:
                f.write(line)
                first = False
            else:
                parsed = line.split(",")
                parsed[-1] = "%.4f\r\n" % new_data[counter]
                newline = ",".join(parsed)
                suma += new_data[counter]
                f.write(newline)
                counter += 1


def superimpose(first_model, second_model):
    try:
        pymol_cmd = ["pymol", "-cq", resource_filename("aggrescan", join("data", "superimpose.pml")), "--", first_model, second_model]
        out, err = Popen(pymol_cmd, stdout=PIPE, stderr=PIPE).communicate()
        if err:
            logger.warning(module_name="Pymol",
                           msg="Pymol reports an error: %s" % err)
        shutil.move("superimposed.png", "CABSflex_supe.png")
    except OSError:
        logger.warning(module_name=_name,
                       msg="Pymol failed to launch (most likely not present on the system)."
                           "Couldn't create a superimposed picture of CABS input and output ")
    except (shutil.Error, IOError):
        logger.critical(module_name="Pymol",
                        msg="Pymol failed to create a superimposed image for input and "
                            "most aggregation prone CABS model")


def _prepare_command(pdb_input="input.pdb", cabs_dir=".", cabs_config='', n_models=12):
    """Prepare CABS settings according to user input"""
    cabs_cmd = []
    if cabs_dir:
        cabs_cmd.extend(["python", cabs_dir, "flex"])
    else:
        cabs_cmd.append("CABSflex")
    if cabs_config:
        cabs_cmd.extend(["-c", cabs_config])
    else:
        cabs_cmd.extend(["--image-file-format", "png", "-v", "4"])
    cabs_cmd.extend(["--input", pdb_input, "--clustering-medoids", str(n_models), "--aa-rebuild", "--log"])
    return cabs_cmd


def _cleanup_files(work_dir="", cabs_dir="", input_pdb="", top="", clean=True):
    """If clean some files will be saved, else only remove all created files"""
    if clean:
        shutil.move(join(cabs_dir, "plots", "RMSF_seq.png"), join(work_dir, "CABSflex_rmsf.png"))
        shutil.move(join(cabs_dir, "plots", "RMSF.csv"), join(work_dir, "CABSflex_rmsf.csv"))
        shutil.copyfile(join(work_dir, "models", top.strip()), join(work_dir, "folded.pdb"))
        shutil.copyfile(join(cabs_dir, "output_pdbs", "averages"), "averages")

    if logger.get_log_level() >= 2 and clean:
        logger.log_file(module_name="CABS",
                        msg="Saving top CABS models as %s" % "models.tar.gz")
        with tarfile.open(join(work_dir, "models.tar.gz"), "w:gz") as tar:
            tar.add(join(work_dir, "models"), arcname=os.path.sep)
        logger.log_file(module_name="CABS",
                        msg="Saving Aggrescan3D statistics for all CABS models as %s" % "stats.tar.gz")
        with tarfile.open(join(work_dir, "stats.tar.gz"), "w:gz") as tar:
            tar.add(join(work_dir, "stats"), arcname=os.path.sep)

    shutil.rmtree(join(work_dir, "stats"), ignore_errors=True)
    shutil.rmtree(join(work_dir, "models"), ignore_errors=True)
    _del_cabs_dir(cabs_dir=cabs_dir)


def _del_cabs_dir(cabs_dir="CABS_sim"):
    shutil.rmtree(cabs_dir, ignore_errors=True)


def _check_output(models_dir, n_models):
    """Check if all the required files were created"""
    _file_list = ["CABS.log"]
    _file_list.extend([join(models_dir, "model_%s.pdb" % str(i)) for i in range(n_models)])
    _file_list.append(join("plots", "RMSF_seq*"))
    _file_list.append(join("plots", "RMSF*"))
    for filename in _file_list:
        if not glob(filename):
            logger.critical(module_name="CABS",
                            msg="File %s which CABS should have generated was not found." % filename)
            raise logger.CabsError


def _sort_dict(my_dict):
    """Return a reverse-sorted by value, OrderedDict of a regular dictionary with number values"""
    new_dict = OrderedDict()
    for key, value in sorted(my_dict.iteritems(), key=lambda (k, v): (v, k), reverse=True):
        new_dict[key] = value
    return new_dict


def _makedir(path):
    """Ignore error if path exists"""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
