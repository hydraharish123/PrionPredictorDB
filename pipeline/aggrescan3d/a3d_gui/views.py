#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import shutil
import sqlite3
from flask import render_template, url_for, request, flash, redirect, jsonify, g, abort, Response

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, HiddenField, RadioField, FloatField
from wtforms.validators import Length, Email, optional, ValidationError

from a3d_gui import app
from utils import query_db, unique_id, gunzip, connect_db, parse_out, aminoacids, get_undefined_job_ids
from job_handling import run_job, check_jobs
from create_config import generate_config, prepare_data
from validators import *

##############################################################################


@app.before_request
def before_request():
    g.sqlite_db = connect_db()


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s\n    " %
                  (getattr(form, field).label.text, error), 'error')


class MyForm(Form):
    name = StringField('Project name',
                       validators=[Length(min=4, max=50), optional()],
                       description="Project name",
                       default="")
    input_pdb_code = StringField('PDB code',
                                 validators=[pdb_input_validator,
                                             pdb_code_validator],
                                 description="1YWO",
                                 default="")
    chain = StringField('Chain',
                        validators=[Length(min=1, max=5),
                                    optional(), single_chain_validator],
                        description="A",
                        default="")
    input_file = FileField('Local PDB file',
                           validators=[pdb_file_validator,
                                       non_empty_file])
    jid = HiddenField(default=unique_id())
    foldx = RadioField("Stability calculations",
                       validators=[foldx_validator],
                       choices=[('1', 'Yes'), ('0', 'No')], default='1')
    mutation = RadioField('Mutate residues',
                          choices=[('1', 'Yes'), ('0', 'No')],
                          validators=[foldx_and_m_validator],
                          default='0')
    auto_mutation = RadioField('Enhance protein solubility',
                               choices=[('1', 'Yes'), ('0', 'No')],
                               validators=[auto_mut_validator],
                               default='0')
    dynamic = RadioField("Dynamic mode",
                         choices=[('1', 'Yes'), ('0', 'No')], default='0')
    distance = RadioField('Distance of aggregation analysis: ',
                          choices=[('5', '5Å'.decode('utf-8')),
                                   ('10', '10Å'.decode('utf-8'))],
                          default='10')
    ph = FloatField('pH',
                    validators=[NumberRange(0.01, 14), optional()],
                    description="Use a pH dependant scale")


def add_init_data_to_db(form):
    jid = unique_id()
    name = form.name.data
    if len(name) < 2:
        name = jid
    chains = form.chain.data.strip()
    dest_directory = os.path.abspath(os.path.join(app.config['USERJOB_DIRECTORY'], jid))
    dest_file = os.path.join(dest_directory, "input.pdb.gz")
    os.makedirs(dest_directory)
    if form.input_pdb_code.data:
        pdb_code = form.input_pdb_code.data.strip()
        stream = urllib2.urlopen('http://www.rcsb.org/pdb/files/' + pdb_code + '.pdb.gz')
        b2 = stream.read()
        string_io_data = StringIO(b2)
        with gzip.GzipFile(fileobj=string_io_data, mode="rb") as f:
            p = PdbParser(f, chains)
            input_seq = p.getSequence()
            p.savePdbFile(dest_file)
            gunzip(dest_file)
        stream.close()
    else:
        p = PdbParser(form.input_file.data.stream, chains)
        input_seq = p.getSequence()
        p.savePdbFile(dest_file)
        gunzip(dest_file)

    chain_numbering = p.getChainIdxResname()
    distance = form.distance.data
    dynamic = form.dynamic.data
    mutate = form.mutation.data
    foldx = form.foldx.data
    ph = form.ph.data
    all_chains = chains or "".join(p.getChains())
    try:    # Add the column for backwards compatibility
        query_db("ALTER TABLE project_details ADD COLUMN ph DOUBLE DEFAULT NULL")
    except:
        pass
    if mutate == "1":
        query_db("INSERT INTO user_queue (jid, project_name, working_dir, status)\
                  VALUES(?,?,?,?)",
                  [jid, name, dest_directory, 'mut_wait'], insert=True)
        query_db("INSERT INTO project_details (jid, chain_numbering, chain_sequence, \
                  dynamic, mutate, distance, chains, foldx, ph) \
                 VALUES(?,?,?,?,?,?,?,?,?)",
                 [jid, chain_numbering, input_seq, dynamic, mutate, distance, all_chains, foldx, ph], insert=True)
    else:
        query_db("INSERT INTO user_queue (jid, project_name, working_dir, status)\
                VALUES(?,?,?,?)",
                 [jid, name, dest_directory, 'running'], insert=True)
        query_db("INSERT INTO project_details (jid, chain_numbering, chain_sequence, \
                 dynamic, mutate, distance, chains, foldx, ph) \
                 VALUES(?,?,?,?,?,?,?,?,?)",
                 [jid, chain_numbering, input_seq, dynamic, mutate, distance, all_chains, foldx, ph], insert=True)
    return jid, dest_directory


@app.route('/job/<jid>/')
def job_status(jid):
    try:
        all_info = prepare_data(jid)
    except IOError as e:
        flash("Your job tried to access files that don't exists. Perhaps a job with status done had its files removed? "
              "Or you tried to set done on a job that misses aggrescan files.  "
              "Changed status to error.")
        flash("Your error: %s" % str(e))
        query_db("UPDATE user_queue SET status='error'\
                  WHERE jid=?", [jid], insert=True)
        return job_status(jid)
    aa_t = aminoacids()
    return render_template('job_info.html',
                           jid=jid, aa_dict=aa_t, info=all_info)


@app.route('/mutate/<jid>', methods=['GET', 'POST'])
def mutate(jid):
    q = query_db("SELECT chain_numbering FROM project_details \
                  WHERE jid=?", [jid], one=True)
    chains = json.loads(q['chain_numbering'])
    aa_t = aminoacids()

    return render_template('mutate.html', sequence=chains,
                           jid=jid, aa_dict=aa_t)


@app.route('/auto_mutate/<jid>', methods=['GET', 'POST'])
def auto_mutate(jid):
    q = query_db("SELECT chain_numbering FROM project_details \
                  WHERE jid=?", [jid], one=True)
    chains = json.loads(q['chain_numbering'])
    aa_t = aminoacids()
    return render_template('auto_mutate.html', sequence=chains,
                           jid=jid, aa_dict=aa_t)


@app.route('/_upmut2', methods=['GET', 'POST'])
def up_remutation():
    if request.method == 'POST':
        jid = unique_id()
        old_jid = request.form.get('oldjid', '')
        mut = ", ".join(request.form.getlist('toreplace[]'))
        old_queue = query_db("SELECT project_name, working_dir FROM \
                user_queue WHERE jid=?", [old_jid], one=True)
        new_name = old_queue['project_name']+" [mutate: "+str(mut)+"]"

        d = query_db("SELECT foldx, dynamic, distance, chains FROM project_details WHERE jid=?",
                     [old_jid], one=True)
        dest_directory = os.path.join(app.config['USERJOB_DIRECTORY'], jid)
        old_directory = old_queue['working_dir']
        os.mkdir(dest_directory)
        shutil.copy(os.path.join(old_directory, "output.pdb"),
                    os.path.join(dest_directory, "input.pdb"))
        with open(os.path.join(dest_directory, "input.pdb"), "rb") as rea:
            p = PdbParser(rea)
            sequence = p.getSequence()
            chain_numbering = p.getChainIdxResname()

        query_db("INSERT INTO user_queue(jid, project_name, working_dir, status) VALUES(?,?,?,?)",
                 [jid, new_name, dest_directory, 'running'], insert=True)
        query_db("INSERT INTO project_details(jid, dynamic, mutate, mutation, chains, foldx, distance, "
                 "chain_sequence, chain_numbering) VALUES(?,?,?,?,?,?,?,?,?)",
                 [jid, d['dynamic'], 1, mut, d['chains'], 1, d['distance'],
                  sequence, chain_numbering], insert=True)
        generate_config(jid)
        pid = run_job(dest_directory)
        query_db("UPDATE user_queue SET pid=? WHERE jid=?", [pid, jid], insert=True)
        return redirect(url_for('job_status', jid=jid))


@app.route('/_upmut', methods=['GET', 'POST'])
def up_mutation():
    if request.method == 'POST':
        jid = request.form.get('jid', '')
        mut = ", ".join(request.form.getlist('toreplace[]'))
        details = query_db("SELECT project_name, working_dir FROM user_queue WHERE \
                jid=?", [jid], one=True)
        proname = details['project_name'] + " [mutate: "+mut+"]"
        query_db("UPDATE user_queue SET status='running', \
                project_name=? WHERE jid=?", [proname, jid], insert=True)
        query_db("UPDATE project_details SET mutate=?, mutation=? WHERE jid=?", [1, mut, jid], insert=True)
        generate_config(jid)
        pid = run_job(details['working_dir'])
        query_db("UPDATE user_queue SET pid=? WHERE jid=?", [pid, jid], insert=True)
        return redirect(url_for('job_status', jid=jid))


@app.route('/_upautomut', methods=['GET', 'POST'])
def up_automutation():
    if request.method == 'POST':
        jid = request.form.get('jid', '')
        n_mutated = request.form.get('n_mutated', '')
        n_cores = request.form.get('n_cores', '')

        automut = "%s %s " % (n_mutated, n_cores) + " ".join(request.form.getlist('toreplace[]'))
        details = query_db("SELECT project_name, working_dir FROM user_queue WHERE \
                jid=?", [jid], one=True)
        proname = details['project_name'] + " (automated mutations)"
        query_db("UPDATE user_queue SET status='running', \
                project_name=? WHERE jid=?", [proname, jid], insert=True)
        try:
            query_db("UPDATE project_details SET auto_mutation=? WHERE jid=?", [automut, jid], insert=True)
        except sqlite3.OperationalError: # Backwards compatibility when the column didn't exist
            query_db("ALTER TABLE project_details ADD COLUMN auto_mutation TEXT", insert=True)
            query_db("UPDATE project_details SET auto_mutation=? WHERE jid=?", [automut, jid], insert=True)
        generate_config(jid)
        pid = run_job(details['working_dir'])
        query_db("UPDATE user_queue SET pid=? WHERE jid=?", [pid, jid], insert=True)
        return redirect(url_for('job_status', jid=jid))


@app.route('/_check_status/<jid>', methods=['GET'])
def get_job_status(jid):
    response = {}
    details = query_db("SELECT working_dir,status,jid FROM user_queue WHERE \
            jid=?", [jid], one=True)
    try:
        with open(os.path.join(details['working_dir'], "Aggrescan.log"), 'r') as f:
            response['log'] = f.read()
        if (details['status'] != 'done' and details['status'] != 'error') and check_jobs(details['jid']):
            response['reload'] = True
    except IOError:
        response['log'] = "Couldn't open the log for simulation at %s" % os.path.join(details['working_dir'], "Aggrescan.log")
    return jsonify(**response)


@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index_page():
    form = MyForm()
    foldx_path = query_db("SELECT foldx_path FROM system_data WHERE id=1", one=True)[0]
    if request.method == 'POST':
        if form.validate_on_submit():
            jid, work_dir = add_init_data_to_db(form)
            if form.mutation.data == '1':
                return redirect(url_for('mutate', jid=jid))
            elif form.auto_mutation.data == '1':
                return redirect(url_for("auto_mutate", jid=jid))
            else:
                generate_config(jid)
                pid = run_job(work_dir)
                query_db("UPDATE user_queue SET pid=? WHERE jid=?", [pid, jid], insert=True)
                return redirect(url_for('job_status', jid=jid))
        flash_errors(form)
    return render_template('index.html', form=form, foldx_path=foldx_path)


########################################################################################################################
@app.route('/queue', methods=['POST', 'GET'], defaults={'page': 1})
@app.route('/queue/page/<int:page>/', methods=['POST', 'GET'])
def queue_page(page=1):
    before = (page - 1) * app.config['PAGINATION']
    if request.method == 'GET':
        search = request.args.get('q', '')
        if search != '':
            flash("Searching results for %s ..." % (search), 'warning')
            q = query_db("SELECT project_name, jid, status, \
                    started datet FROM user_queue \
                    WHERE status!='mut_wait' AND (project_name LIKE ? OR \
                    jid=?) ORDER BY started DESC LIMIT ?,?",
                         ["%"+search+"%", search, before,
                          app.config['PAGINATION']])
            q_all = query_db("SELECT status FROM user_queue WHERE \
                    status!='mut_wait' AND (project_name LIKE ? OR jid=?) \
                    ORDER BY started DESC", ["%"+search+"%", search])
            out = parse_out(q)
            if len(out) == 0:
                flash("Nothing found", "error")
            elif len(out) == 1:
                flash("Project found!", "info")
                jid = out[0]['jid']
                return redirect(url_for('job_status', jid=jid))

            return render_template('queue.html', queue=out, page=page,
                                   total_rows=len(q_all))
    # Get the jobs from database
    qall = query_db("SELECT status FROM user_queue WHERE \
            status!='mut_wait' ORDER BY started DESC", [])
    q = query_db("SELECT jid, project_name, status, started datet \
                  FROM user_queue WHERE status != 'mut_wait' \
                  ORDER BY started DESC LIMIT ?,?", [before, app.config['PAGINATION']])
    # Check if status has changed
    check_jobs(*get_undefined_job_ids(q))
    # Get updated que
    q = query_db("SELECT jid, project_name, status, started datet \
                      FROM user_queue WHERE status != 'mut_wait' \
                      ORDER BY started DESC LIMIT ?,?", [before, app.config['PAGINATION']])
    out = parse_out(q)
    return render_template('queue.html', queue=out, total_rows=len(qall),
                           page=page)





