#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
import uuid
import re
import sqlite3
from flask import g
from a3d_gui import app
from collections import OrderedDict
from os.path import join


def gunzip(filename):
    gunzipped = ".".join(filename.split(".")[:-1])
    with open(gunzipped, 'w') as f_out:
        with gzip.open(filename, 'rb') as f_in:
            f_out.writelines(f_in)


def unique_id():
    return hex(uuid.uuid4().time)[2:-1]


def regexp(expr, item):
    r = re.compile(expr)
    return r.match(item) is not None


def connect_db():
    """Connects to a specific database."""
    try:
        rv = sqlite3.connect(app.config['DATABASE'])
        rv.create_function('regexp', 2, regexp)
        rv.row_factory = sqlite3.Row
    except sqlite3.Error:
        raise
    return rv


def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def query_db(query, args=(), one=False, insert=False):
    mydb = get_db()
    cur = mydb.cursor()
    cur.execute(query, args)
    if insert:
        mydb.commit()
        cur.close()
        return cur.lastrowid
    else:
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def status_color(status, shorter=True):
    if not status:
        return '<span class="label label-danger">\
                <i class="fa fa-exclamation-circle"></i> error</span>'
    if not shorter:
        if status == 'pending':
            return '<span class="label label-warning">\
                    <i class="fa fa-spin fa-spinner"></i> pending \
                    </span>'
        elif status == 'missing_files':
            return '<span class="label label-info">\
                    <i class="fa fa-sliders"></i> Missing files</span>'
        elif status == 'running':
            return '<span class="label label-primary">\
                    <i class="fa fa-bolt"></i> running</span>'
        elif status == 'error':
            return '<span class="label label-danger">\
                    <i class="fa fa-exclamation-circle"></i> error</span>'
        elif status == 'done':
            return '<span class="label label-success">\
                    <i class="fa fa-check-circle-o"></i> done</span>'
    else:
        if status == 'pending':
            return '<span class="label label-warning">\
                    <i class="fa fa-spin fa-spinner"></i> pending</span>'
        elif status == 'missing_files':
            return '<span class="label label-info">\
                    <i class="fa fa-sliders"></i> Missing files</span>'
        elif status == 'running':
            return '<span class="label label-primary">\
                    <i class="fa fa-bolt"></i> running</span>'
        elif status == 'error':
            return '<span class="label label-danger">\
                    <i class="fa fa-exclamation-circle"></i> error</span>'
        elif status == 'done':
            return '<span class="label label-success">\
                    <i class="fa fa-check-circle-o"></i> done</span>'


def sort_dict(my_dict):
    new_dict = OrderedDict()
    for key, value in sorted(my_dict.iteritems(), key=lambda (k, v): (v, k), reverse=True):
        new_dict[key] = value
    return new_dict


def aminoacids():
    aa_dict = {'A': 'ALA', 'R': 'ARG', 'N': 'ASN', 'D': 'ASP', 'C': 'CYS',
               'E': 'GLU', 'Q': 'GLN', 'G': 'GLY', 'H': 'HIS', 'I': 'ILE',
               'L': 'LEU', 'K': 'LYS', 'M': 'MET', 'F': 'PHE', 'P': 'PRO',
               'S': 'SER', 'T': 'THR', 'W': 'TRP', 'Y': 'TYR', 'V': 'VAL',
               'X': 'UNK'}
    aa_dict_F = {'A': 'alanine', 'R': 'arginine', 'N': 'asparagine',
                 'D': 'aspartic acid', 'C': 'cysteine', 'E': 'glutamic acid',
                 'Q': 'glutamine', 'G': 'glycine', 'H': 'histidine',
                 'I': 'isoleucine', 'L': 'leucine', 'K': 'lysine',
                 'M': 'methionine', 'F': 'phenylalanine', 'P': 'proline',
                 'S': 'serine', 'T': 'threonine', 'W': 'tryptophan',
                 'Y': 'tyrosine', 'V': 'valine', 'X': 'unknown'}
    aa_t = []
    for k in sorted(aa_dict, key=aa_dict.get):
        if k != 'X':
            aa_t.append((aa_dict[k], aa_dict_F[k], k))
    return aa_t


def get_undefined_job_ids(q):
    to_check = []
    for i in q:
        if i['status'] == 'pending' or i['status'] == 'missing_files' or i['status'] == 'running':
            to_check.append(i['jid'])
    return to_check


def parse_out(q):
    out = []
    for row in q:
        if row['datet']:
            dtt = row['datet']
        else:
            dtt = "-"
        l = {'project_name': row['project_name'], 'jid': row['jid'],
             'date': dtt, 'status': status_color(row['status'])}

        out.append(l)
    return out


