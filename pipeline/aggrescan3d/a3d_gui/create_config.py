# -*- coding: utf-8 -*-

import os
import json
import re
import sqlite3
import numpy as np
from os.path import join
from glob import glob
from utils import query_db, status_color, sort_dict
from a3d_gui import app
from collections import OrderedDict
from aggrescan.optparser import parse_config_file, get_parser_object, _parse_mut


def generate_config(jid):
    """
    Function that that reads a database and creates a config file
    that then can be easily run by Aggrescan3D on the cluster
    paths to cabs and foldx might need to be changed if changes happen
    :param jid:  job unique id
    :return: None
    """

    # There should be exactly one entry in that table. The location needs to be validated on submit
    foldx_loc = query_db("SELECT foldx_path FROM system_data WHERE id=1", one=True)[0]
    file_header = "# Generated for job: %s" % jid
    try:
        project_settings = query_db("SELECT dynamic, mutate, mutation, chains, \
                   foldx, distance, auto_mutation, ph FROM project_details WHERE jid=?", [jid], one=True)
    except sqlite3.OperationalError:  # Backwards compatibility when the auto_mutation and ph columns didn't exist
        query_db("ALTER TABLE project_details ADD COLUMN auto_mutation TEXT", insert=True)
        query_db("ALTER TABLE project_details ADD COLUMN ph DOUBLE DEFAULT NULL", insert=True)
        project_settings = query_db("SELECT dynamic, mutate, mutation, chains, \
                           foldx, distance, auto_mutation, ph FROM project_details WHERE jid=?", [jid], one=True)

    project_name = query_db("SELECT project_name FROM user_queue WHERE jid=?", [jid], one=True)
    with open(join(app.config['USERJOB_DIRECTORY'], jid, "config.ini"), 'w') as f:
        _write(f, file_header)
        _write(f, "# The job can also be identified by its name: %s" % project_name['project_name'])
        _write(f, "v = 3")
        _write(f, "protein = input.pdb")
        _write(f, "movie = webm")
        _write(f, "distance = %s" % project_settings["distance"])
        _write(f, "remote")
        if project_settings["chains"]:
            if len(project_settings["chains"]) == 1:    # Aggrescan only accepts 1 specific chain
                _write(f, "chain = %s" % project_settings["chains"])
        if project_settings["foldx"]:
            _write(f, "foldx = %s" % foldx_loc)
        if project_settings["dynamic"]:
            _write(f, "dynamic")
        if project_settings['ph']:
            _write(f, "ph = %s" % project_settings["ph"])
        if project_settings["auto_mutation"]:
            _write(f, "auto_mutation = %s" % project_settings["auto_mutation"])
        if project_settings["mutation"]:
            for entry in project_settings["mutation"].split():
                _write(f, "m = %s" % entry)


def reverse_config(filepath):
    argv, mutations = parse_config_file(filepath)
    parser = get_parser_object()
    options = parser.parse_args(argv)
    mutations = _parse_mut(mutations)
    final_options = {
        'dynamic': options.dynamic,
        'distance': options.distance,
        'chain': options.chain,
        "foldx": options.foldx,
        'auto_mutation': options.auto_mutation,
    }
    if final_options['auto_mutation'] == "is_not_used":
        final_options['auto_mutation'] = None
    print final_options, mutations
    return final_options, mutations


def prepare_data(jid):
    """
    Pull all the necessary data from the database and prepare an OrderedDict
    The dict is then used to display the job_info page
    raises an IO error if there is no data in current database for the specified job ID
    :param jid: unique job ID
    :return: dict of option:value pairs
    """
    system_info = query_db("SELECT chain_sequence, distance, mutt_energy_diff, dynamic, \
            mutation, mutate, chains, foldx, auto_mutation FROM  project_details WHERE jid=?", [jid], one=True)
    basic_info = query_db("SELECT started, project_name, status , working_dir FROM  "
                          "user_queue WHERE jid=?", [jid], one=True)
    project_info = OrderedDict()
    if not basic_info or not system_info:
        raise IOError
    project_info['status'] = basic_info['status']
    project_info['status_color'] = status_color(project_info['status'])
    # Example projects will not exist by their abspath on users machine
    if os.path.exists(os.path.join(app.config['USERJOB_DIRECTORY'], basic_info['working_dir'].split("/")[-1])):
        project_info['working_dir'] = os.path.join(app.config['USERJOB_DIRECTORY'], basic_info['working_dir'].split("/")[-1])
    else:
        project_info['working_dir'] = basic_info['working_dir']
    # csv table reading
    mut = {}
    if system_info['mutate'] == 1:
        for mutation in system_info['mutation'].strip().replace(" ", "").split(","):
            k = mutation[-1] + mutation[2:-1]  # the last letter is the chain ID letter, starting from index 2 is the cahin ID number
            mut[k] = mutation
    if system_info['foldx']:  # foldx is app
        project_info['foldx'] = "Yes"
    else:
        project_info['foldx'] = "No"

    avg_scores = ''
    a3d_table = []
    a3dtable = ''
    chains = set()
    models = ["input.pdb", "CABS_average.pdb"]
    models.extend(["model_%s.pdb" % str(i) for i in range(12)])
    project_info['models'] = models
    project_info['error'] = ''
    project_info['table'] = ''
    project_info['avg_scores'] = {'dummy': 'dummy'}     # click highest model would cause template errors otheriwse for static jobs
    project_info['chains'] = system_info['chains'] or ""
    project_info['distance'] = system_info['distance']
    project_info['chain_sequence'] = system_info['chain_sequence']
    project_info['project_name'] = basic_info['project_name']
    project_info['started'] = basic_info['started']
    project_info['mutation'] = mut
    project_info['mutate'] = system_info['mutate']
    project_info['mutt_energy_diff'] = system_info['mutt_energy_diff']
    project_info['auto_mutation'] = False
    project_info['auto_mutation_used'] = system_info['auto_mutation']
    project_info['autom_data'] = {'dummy': 'dummy'}
    if system_info['dynamic'] == 1:
        project_info['dynamic'] = True
        pdb_in_dir = set([os.path.basename(i) for i in glob(join(project_info['working_dir'], "*.pdb"))])
        models = set(models)
        if len(models-pdb_in_dir) > 0:
            project_info['model_files'] = 'missing'
        else:
            project_info['model_files'] = 'ok'
    else:
        project_info['dynamic'] = False
    if project_info['status'] == 'done':
        if system_info['auto_mutation']:
            project_info['autom_data'], project_info['autom_energy'], project_info['autom_score'] = _parse_auto_mut_info(
                join(project_info['working_dir'], 'Mutations_summary.csv'))
            project_info['auto_mutation'] = True
        if project_info['dynamic']:
            with open(os.path.join(project_info['working_dir'], "averages")) as f:
                loaded_data = json.load(f)
            project_info['avg_scores'] = sort_dict(loaded_data)

        with open(os.path.join(project_info['working_dir'],
                  "A3D.csv")) as fw:
            rec = re.compile(r"^(.*),(.*),(.*),(.*),(.*)$", re.M)
            d = rec.findall(fw.read().replace("\r", ""))[1:]
            dat = []
            for row in d:
                if len(row) != 5:
                    continue
                chain = row[1]
                chains.update(chain)
                residx = row[2]
                resname = row[3]
                v = float(row[4])
                dat.append(v)
                a3d_table.append((residx, resname, chain, "%01.4f" % (v)))
            min3d = min(dat)
            max3d = max(dat)
            sum3d = np.sum(dat)
            avg3d = sum3d/len(dat)
            a3dtable = {'min': min3d, 'avg': avg3d, 'max': max3d,
                        'sum': sum3d, 'tab': a3d_table}
            project_info['table'] = a3dtable
    return project_info


def _write(obj, text):
    obj.write(text)
    obj.write("\n")


def _parse_mut(mut_list):
    """Necessary for now as those come as a list of dicts and the db needs a simple string"""
    return ["%s%s%s%s" % (i['oldres'], i['newres'], i['idx'], i['chain']) for i in mut_list]


def _parse_auto_mut_info(filename):
    """
    Reads the file and returns an ordered dict with the first column as keys, and the next 3 as a list
    Currently will  return top x results - another parameter to decide on
    """
    data = OrderedDict()
    max_results = 12
    counter = 0
    energy_data = OrderedDict()
    score_data = OrderedDict()
    try:
        with open(filename, 'r') as f:
            f.readline()  # Skip first line with labels
            for line in f:
                counter += 1
                parsed = line.split(",")
                data[parsed[0]] = [float(parsed[1]), float(parsed[2]), float(parsed[3]),
                                   _calc_hidden_score(float(parsed[1]), float(parsed[3]))]
    except IOError:
        return {'Data missing': False}, {'Data missing': 'empty'}, {'Data missing': 'empty'}  # The template will recognize this as a sign not to load the tab
    data = _rank_and_prune_mutants(data)
    for key, values in data.items():
        energy_data[key] = _get_energy_eval(values[0])
        score_data[key] = _get_score_eval(values[2])

    if not data:  # File is empty, the likely case is that there were no suitable mutations found
        data = {'No mutants': False}, {'No mutants': 'empty'}, {'No mutants': 'empty'}
    return data, energy_data, score_data


def _rank_and_prune_mutants(data_dict):
    already_in = {x[2:]: 0 for x in data_dict.keys()}
    new_data = sort_dict_list_item(data_dict)
    for key in new_data.keys():
        if already_in[key[2:]] >= 2:
            new_data.pop(key)
        else:
            already_in[key[2:]] += 1
    return new_data


def sort_dict_list_item(my_dict, item_index=3):
    new_dict = OrderedDict()
    for key, value in sorted(my_dict.iteritems(), key=lambda (k, v): (v[item_index], k), reverse=True):
        new_dict[key] = value
    return new_dict


def _calc_hidden_score(energy, a3d_score):
    """ Get the differences in score and energy and calculate something that better ranks them"""
    if a3d_score > 0 and energy > 0:
        return a3d_score * energy * -1
    elif energy > 0 > a3d_score:
        return a3d_score * - (1/(energy*100))
    elif a3d_score > 0 and energy < 0:
        return (1/(a3d_score*100)) * energy
    return a3d_score * energy * 20


def parse_dynamic_data(jid):
    with open(os.path.join(join(app.config['USERJOB_DIRECTORY'], jid), "averages")) as f:
        loaded_data = json.load(f)
    return loaded_data


def _get_energy_eval(energy_diff):
    if energy_diff < -1.0:
        return "good-mutation"
    if energy_diff < -0.5:
        return "medium-mutation"
    if 0.5 > energy_diff > -0.5:
        return "neutral-mutation"
    if energy_diff < 1:
        return "bad-mutation"
    return "terrible-mutation"


def _get_score_eval(avg_score_diff):
    if avg_score_diff < -0.04:
        return "good-mutation"
    if avg_score_diff < -0.02:
        return  "medium-mutation"
    if avg_score_diff > -0.02 and avg_score_diff < 0.02:
        return "neutral-mutation"
    if avg_score_diff < 0.04:
        return "bad-mutation"
    return "terrible-mutation"