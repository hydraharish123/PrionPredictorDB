#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing as mp
from subprocess import Popen, PIPE
from collections import OrderedDict
from os.path import join, isfile
from postProcessing import make_auto_mut_plot
import os
import re
import shutil
import logger

_name = "Auto_mut"

# Define some variables that dictate how some properties of this - maybe they get to be parameters in the future
_score_threshold = -0.2  # How high an A3D score has to be for the residue to be considered for mutation
_energy_threshold = 0.0   # When a mutation is considered "good"
_score_diff_threshold = 5  # When a mutation is considered to increase solubility  +5 should accept all while 0 would
                           # already be qutite restrictive
_target_mutations = ["E", "K", "D", "R"]  # Glutamic acid, lysine,  aspartic acid, arginine

# The slicing in this code can be hard to read so here is a short summary:
# Chain ID and residue names come as one letter shorts while the number can have more than one char
# Final mutation code is <Old residue><New residue><Residue number><Chain ID>
# The auto_mutation to_exclude argument comes as <Residue number><Chain ID>
# The one that comes from A3D file comes as < Old residue><Residue number><Chain ID>


def run_auto_mutation(work_dir, options, foldx_loc, distance, ph):
    n_mutations = options[0]
    n_processes = options[1]
    to_exclude = []     # Not to worry about it even exists
    if len(options) > 2:
        to_exclude = options[2]
    pool = mp.Pool(n_processes)
    mutations, avg_score = _mutation_list(work_dir=work_dir, excluded_list=to_exclude, n_mutations=n_mutations)
    if not mutations:
        with open(join(work_dir, "Mutations_summary.csv"), "w") as f:   # leave an empty file for the server
            pass
        return
    pool.map(_run_job, [(i, foldx_loc, work_dir, str(distance), ph) for i in mutations])

    _analyze_results(work_dir=work_dir, output_file="Mutations_summary.csv", mutation_list=mutations,
                     base_avg_score=avg_score)
    _cleanup(work_dir=work_dir, mutation_list=mutations)
    try:
        _plots(work_dir=work_dir)
    except Exception as e:  # This is hopefully not needed but in case something happens the user will at least see a
                            # message rather than a traceback
        logger.critical(module_name=_name, msg="It seems that all the mutation attempts failed or some other unexpected"
                                               " error arisen while trying to plot the automated mutations.")
        raise


def _mutation_list(work_dir, excluded_list, n_mutations):
    scores = _parse_a3dcsv(os.path.join(work_dir, "A3D.csv"))
    avg_score = sum(scores.values())/len(scores.values())
    mutation_list = []
    counter = 0
    for residue, value in scores.items():
        if value > _score_threshold and residue[1:] not in excluded_list and residue[0] not in _target_mutations \
                and value != 0:
            mutation_list.extend(["%s%s%s" % (residue[0], i, residue[1:]) for i in _target_mutations])
            logger.info(module_name=_name, msg="Residue number %s from chain %s and a score of %.3f (%s) selected "
                                               "for automated muatation" % (residue[1:-1], residue[-1], value,
                                                                            _aa_dict_F[residue[0]]))
            counter += 1
            if counter >= n_mutations:
                break
        elif value > _score_threshold and residue[1:] in excluded_list:
            logger.info(module_name=_name, msg="Residue number %s from chain %s and a score of %.3f omitted "
                                               "from automated muatation (excluded by the user)." % (residue[1:-1], residue[-1], value))
    if not mutation_list:
        logger.critical(module_name=_name, msg="Couldn't find residues suitable for automated mutations (exceeding a "
                                               "threshold of %.2f). No automated mutations performed." % _score_threshold)
    return mutation_list, avg_score


def _parse_a3dcsv(filepath):  #TODO this is done on muttiple occasions so maybe should be unified somwhere
    """
    Return an OrderedDict of label:score type. The dict is sorted by score so highest is on top
    """
    pattern = re.compile(r"^(.*),(.*),(.*),(.*),(.*)$", re.M)
    scores = OrderedDict()
    try:
        with open(filepath, 'r') as f:
            data = pattern.findall(f.read().replace("\r", ""))[1:]  #
    except IOError:
        return False    # The mutation likely failed this should pass the info to analyze_results
    for line in data:
        label = line[3] + line[2] + line[1]  # One letter code + residue ID + chain ID (the mutation syntax)
        aggScore = float(line[4])
        scores[label] = aggScore
    scores = OrderedDict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    return scores


def _run_job(args):
    """
    Run a single A3D job with a specific mutation
    args go as follows: mutation code, FoldX location, main job's work dir, a3d distance argument
    """
    mutation, foldx, work_dir, distance, ph = args
    os.chdir(work_dir)
    if ph:
        cmd = ["aggrescan", "-i", "output.pdb", "-v", "4", "-w", mutation, "-m", mutation, "-f", foldx,
               "--subprocess", "--distance", distance]
    else:
        cmd = ["aggrescan", "-i", "output.pdb", "-v", "4", "-w", mutation, "-m", mutation, "-f", foldx,
               "--subprocess", "--distance", distance, "-ph", ph]
    logger.info(module_name=_name, msg="Mutating residue number %s from chain %s (%s) into %s "
                                       " " % (mutation[2:-1], mutation[-1], _aa_dict_F[mutation[0]],
                                              _aa_dict_F[mutation[1]]))  # converting letters into full names
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    proc.communicate()
    if proc.returncode != 0:
        logger.warning(module_name=_name, msg="Mutation %s could have failed (this can be ignored if the main program "
                                              "reports the energy difference). Simulation log for that run should be "
                                               "available at %s" % (mutation,
                                                                    os.path.join(work_dir, mutation, "Aggrescan.error")))


def _analyze_results(work_dir, output_file, mutation_list, base_avg_score):
    """
    Analyze the results and select all of those that are not relevant on keeping top X mutations and return the rest
    to the cleaner that will get rid of them, but keeping their scores in the output_file
    """
    data = OrderedDict()
    unnecessary_results = []
    for mutation in mutation_list:
        scores = _parse_a3dcsv(os.path.join(work_dir, mutation, "A3D.csv"))
        if not scores:
            continue
        with open(os.path.join(work_dir, mutation, "MutantEnergyDiff"), 'r') as f:
            mutation_energy = float(f.read().split()[0])    # This should be guaranteed to work given the check above
        avg_score = sum(scores.values())/len(scores.values())
        data[mutation] = [mutation_energy, avg_score, avg_score - base_avg_score]
        if mutation_energy > _energy_threshold or avg_score - base_avg_score > _score_diff_threshold:
            unnecessary_results.append(mutation)
        logger.info(module_name=_name, msg="Effect of mutation residue number %s from chain %s (%s) into %s: "
                                           "Energy difference: %.4f kcal/mol, Difference in average score from the "
                                           "base case: %.4f"
                                           "" % (mutation[2:-1], mutation[-1], _aa_dict_F[mutation[0]],
                                                 _aa_dict_F[mutation[1]], mutation_energy, avg_score - base_avg_score))
    data = OrderedDict(sorted(data.items(), key=lambda x: x[1][0]))   # sort by mutation energy
    with open(os.path.join(work_dir, output_file), "w") as f:
        f.write("%s,%s,%s,%s\n" % ("Mutation", "EnergyDiff", "AvgScore", "AvgScoreDiff"))
        for mutation, values in data.items():
            f.write("%s,%.4f,%.4f,%.4f\n" % (mutation, values[0], values[1], values[2]))
    return unnecessary_results


def _cleanup(work_dir, mutation_list):
    for mutation in mutation_list:
        if isfile(join(work_dir, mutation, "A3D.csv")) and isfile(join(work_dir, mutation, "output.pdb")):
            shutil.move(join(work_dir, mutation, "A3D.csv"), join(work_dir, "%s%s" % (mutation, ".csv")))
            shutil.move(join(work_dir, mutation, "output.pdb"), join(work_dir, "%s%s" % (mutation, ".pdb")))
            shutil.rmtree(join(work_dir, mutation))
        else:
            if isfile(join(work_dir, mutation, "Aggrescan.error")):
                shutil.move(join(work_dir, mutation, "Aggrescan.error"), join(work_dir, "%s%s" % (mutation, ".error")))
                shutil.rmtree(join(work_dir, mutation))
            else:
                with open(join(work_dir, "%s%s" %(mutation, ".error")), "w") as f:
                    f.write("The mutation has failed and no error log was created during the simulation. "
                            "This is unexpected and if you require further assistance please contact us or leave a bug "
                            "report on our bitbucket at "
                            "https://bitbucket.org/lcbio/aggrescan3d/issues?status=new&status=open")


def _plots(work_dir):
    make_auto_mut_plot(work_dir)


# This is a copy from somewhere else, maybe should put it somewhere for imports
_aa_dict_F = {'A': 'alanine', 'R': 'arginine', 'N': 'asparagine',
              'D': 'aspartic acid', 'C': 'cysteine', 'E': 'glutamic acid',
              'Q': 'glutamine', 'G': 'glycine', 'H': 'histidine',
              'I': 'isoleucine', 'L': 'leucine', 'K': 'lysine',
              'M': 'methionine', 'F': 'phenylalanine', 'P': 'proline',
              'S': 'serine', 'T': 'threonine', 'W': 'tryptophan',
              'Y': 'tyrosine', 'V': 'valine', 'X': 'unknown'}