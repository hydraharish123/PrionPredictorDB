#!/usr/bin/env python
# -*- coding: utf-8 -*-

from a3d_gui import app
from utils import query_db
from server_plot import create_plot
import os
import tarfile
import psutil
import shutil
import sqlite3
import signal
from os.path import join, isfile, exists
from subprocess import Popen, PIPE
from glob import glob
from flask import Response, flash, url_for


"""
Module intended for job (process, db status) managing for the Aggrescan3D standalone app. 
CAUTION! Some of the functions here perform file deletion as well as process killing                        
Should you chose to modify basic settings or job handling and db managing functions do so with care 
"""

_static_file_list = set(["A3D.csv", "output.pdb"])
_dynamic_file_list = set(["CABSflex_rmsf.png", "CABSflex_rmsf.csv", "averages"])
_auto_mut_file_list = set(["A3D.csv", "output.pdb", "Mutations_summary.csv"])
_other_files = set(["Aggrescan.log", "Aggrescan.error", "input.pdb", "input.pdb.gz", "clip.webm", "models.tar.gz",
                    "stats.tar.gz", "config.ini", "output.pdb", "MutantEnergyDiff"])


def run_job(working_dir):
    curr_dir = os.path.abspath(os.curdir)      # save the working dir of server app, otherwise it loses track of the db
    try:
        os.chdir(working_dir)
        process = Popen(["aggrescan", "-c", "config.ini"],
                        stdout=PIPE,
                        stderr=PIPE,
                        preexec_fn=os.setpgrp)    # hopefully the prevents the job from dying with the server
        return process.pid
    except AttributeError:  # Windows band-aid
        os.chdir(working_dir)
        process = Popen(["aggrescan", "-c", "config.ini"],
                        stdout=PIPE,
                        stderr=PIPE)
        return process.pid
    finally:
        os.chdir(curr_dir)  # It is crucial that python stays within its starting directory


@app.route('/_rerun_job/<jid>', methods=['GET'])
def rerun_job(jid):
    working_dir = query_db("SELECT working_dir FROM user_queue WHERE jid=?", [jid])[0][0]
    job_pid = query_db("SELECT pid FROM user_queue WHERE jid=?", [jid])[0][0]
    if isfile(join(working_dir, "config.ini")):
        if is_running(job_pid):
            return Response("The job appears to still be running. Stop it first. Re-run aborted.",
                            status=400, content_type="plain/text")
        try:
            os.remove(join(working_dir, "Aggrescan.log"))
        except OSError:
            pass
        new_pid = run_job(working_dir)
        query_db("UPDATE user_queue SET status='running', pid=? WHERE jid=?", [new_pid, jid], insert=True)
        return url_for('job_status', jid=jid)
    else:
        return Response("File config.ini not present in working directory for the job. Re-run aborted.",
                        status=400, content_type="plain/text")


@app.route('/_kill_job/<jid>', methods=['GET'])
def kill_job(jid):
    """Kill the aggrescan process and all its children, set status to error"""
    proc_pid = query_db("SELECT pid FROM user_queue WHERE jid=?", [jid])[0][0]
    try:
        process = psutil.Process(proc_pid)
        if process.name() == "aggrescan" and process.is_running():
            kill_proc_tree(proc_pid)
            query_db("UPDATE user_queue SET status='error' WHERE jid=?", [jid], insert=True)
            return Response("Job killed", status="200", content_type="plain/text")
        else:
            return Response("Coulnd't stop the job. The pid assigned to it no "
                            "longer points to an active aggrescan job.",
                            status="400", content_type="plain/text")
    except psutil.NoSuchProcess:
        return Response("Coulnd't stop the job. There is no such process.",
                        status="400", content_type="plain/text")
    except psutil.AccessDenied as e:
        return Response("You dont have permissions to stop the job. %s" % str(e),
                        status="400", content_type="plain/text")
    except psutil.TimeoutExpired as e:
        return Response("Coulnd't stop the job. %s" % str(e),
                        status="400", content_type="plain/text")
    except ValueError as e:
        return Response("Can't kill this job. "
                        "Most likely this job was started manually and can't be stopped by this interface",
                        status="400", content_type="plain/text")


@app.route('/_kill_delete_job/<jid>', methods=['GET'])
def kill_delete_job(jid):
    """Terminate the aggrescan process and all its children, and delete all the aggrescan files"""
    try:
        kill_response = kill_job(jid)
        delete_response = delete_files(jid)
        if delete_response and kill_response.status_code == 200:
            _silent_delete_job(jid)
            flash("Files and directory deleted. The job %s has been stopped." % jid)
            return url_for('index_page')
        elif not delete_response and kill_response.status_code == 200:
            _silent_delete_job(jid)
            flash("Files deleted but directory still contains files. The job %s has been stopped." % jid)
            return url_for('index_page')
        elif delete_response and kill_response.status_code != 200:
            _silent_delete_job(jid)
            flash("Something went wrong. The files and directory were deleted but the job couldn't be stopped."
                  "Reason: %s" % kill_response.response)
            return url_for('index_page')
        else:
            return Response("Something went wrong. The directory was not deleted"
                            "and the job couldn't be stopped."
                            "Reason: %s" % kill_response.response,
                            status="400", content_type="plain/text")
    except Exception as e:  # Not nice but there is no outer instance to take that to and I really don't want this crashing the app
        return Response("Something went terribly wrong and your request failed in an unpredictable way ",
                        status="400", content_type="plain/text")


def is_running(proc_pid):
    """Find the aggrescan process based on database-stored pid"""
    try:
        process = psutil.Process(proc_pid)
        if process.name() == "aggrescan" and process.is_running() and process.status() != "zombie":
            return True
        return False
    except psutil.Error:
        return False
    except ValueError:  # for negative pids on added jobs
        return False


def check_jobs(*jobs):
    """
    Attempt to check the job's status. Whether the job is done, missing files, an error occurred, etc
    :param jobs: a list of job_ids
    :return: Bool indicating if the job is done but only if one job id was provided (if more - always None)
    """
    for jid in jobs:
        done = False    # helper to reduce the number of ifs
        working_dir = query_db("SELECT working_dir FROM user_queue WHERE jid=?", [jid])[0][0]
        job_pid = query_db("SELECT pid FROM user_queue WHERE jid=?", [jid])[0][0]
        if isfile(join(working_dir, "Aggrescan.error")):
            query_db("UPDATE user_queue SET status='error' WHERE jid=?", [jid], insert=True)
        elif is_running(job_pid):
            query_db("UPDATE user_queue SET status='running' WHERE jid=?", [jid], insert=True)
        elif not exists(working_dir):
            query_db("UPDATE user_queue SET status='missing_files' WHERE jid=?", [jid], insert=True)
        else:
            details = query_db("SELECT dynamic, mutate, auto_mutation FROM project_details WHERE jid=?", [jid], one=True)
            files_in_dir = set([os.path.basename(i) for i in glob(join(working_dir, "*"))])
            if details['dynamic']:  # attempt to deduct if the job is running or the files are simply not present in the working dir
                missing_files = len(_static_file_list - files_in_dir) + len(_dynamic_file_list - files_in_dir)
                if missing_files == 0:
                    query_db("UPDATE user_queue SET status='done' WHERE jid=?", [jid], insert=True)
                    prepare_files(working_dir)
                    done = True
                else:
                    query_db("UPDATE user_queue SET status='missing_files' WHERE jid=?", [jid], insert=True)

            elif details['auto_mutation']:
                if _auto_mut_file_list - files_in_dir:  # "since the most important files are present we assume the job is done"
                    query_db("UPDATE user_queue SET status='missing_files' WHERE jid=?", [jid], insert=True)
                else:
                    query_db("UPDATE user_queue SET status='done' WHERE jid=?", [jid], insert=True)
                    done = True
            else:
                if _static_file_list - files_in_dir:  # "since two most important files are present we assume the job is done"
                    query_db("UPDATE user_queue SET status='missing_files' WHERE jid=?", [jid], insert=True)
                else:
                    query_db("UPDATE user_queue SET status='done' WHERE jid=?", [jid], insert=True)
                    done = True
            if details['mutate'] and done:
                try:
                    with open(join(working_dir, "MutantEnergyDiff"), 'r') as f:
                        mut_energy_dif = f.read().split()[0].strip()
                    query_db("UPDATE project_details SET mutt_energy_diff=? WHERE jid=?",
                             [mut_energy_dif, jid], insert=True)
                except IOError:
                    query_db("UPDATE user_queue SET status='missing_files' WHERE jid=?", [jid], insert=True)
    if len(jobs) == 1:
        return done


def prepare_files(working_dir):
    """Move some files around to make it easier for the pseudo server"""
    curr_dir = os.path.abspath(os.curdir)      # save the working dir of server app, otherwise it loses track of the db
    try:    # make absolutely sure it gets back to the curr_dir
        os.chdir(working_dir)
        with tarfile.open("models.tar.gz", 'r:gz') as tar:
            tar.extractall()
        os.remove("models.tar.gz")  # remove the archive since the files are already outside anyway
    except IOError:
        pass  # models are not present in the folder, this can happen shouldn't be an issue
    try:
        os.chdir(working_dir)
        with tarfile.open("stats.tar.gz", 'r:gz') as tar:
            tar.extractall()
        os.remove("stats.tar.gz")  # remove the archive since the files are already outside anyway
    except IOError:
        pass  # stats are not present in the folder, this can happen shouldn't be an issue
    finally:
        os.chdir(curr_dir)


def delete_files(job_id):
    """
    Delete all aggrescan files in the working directory. If the directory is then empty it is also removed
    Warning! This will delete any files and subfolders in "tmp" folder in your working directory.
    Returns True if the entire dir is deleted, False otherwise
    """
    n_models = 12  # TODO customizable number of models for the gui
    working_dir = query_db("SELECT working_dir FROM user_queue WHERE jid=?", [job_id])[0][0]
    chains = query_db("SELECT chains FROM project_details WHERE jid=?", [job_id])[0][0]
    pictures = query_db("SELECT * FROM pictures WHERE jid=?", [job_id])
    if pictures is not None:
        for pic in pictures:
            try:
                os.remove(join(app.config['PICTURES'], pic['filename']))
            except OSError:
                pass  # the picture was likely deleted from the folder manually
    files = ["%s.png" % i for i in chains]
    files.extend(["%s.svg" % i for i in chains])
    files.extend(["model_%d.pdb" % i for i in range(n_models)])
    files.extend(["model_%d.pdb" % i for i in range(n_models)])
    files_in_dir = [i for i in glob(working_dir+"/*") if isfile(i)]
    shutil.rmtree(join(working_dir, "tmp"), ignore_errors=True)
    for to_del in files_in_dir:
        try:
            os.remove(to_del)
        except OSError:
            flash("Couldn't delete a file, which was supposed to be here: %s" % to_del)
    try:
        if os.listdir(working_dir):
            return False
        else:
            try:
                os.rmdir(working_dir)
                return True
            except OSError:
                return False  # Something went in the way, shouldn't happen but if it does lets not make a mess about it
    except OSError:
        flash("Attempted to delete %s but it already doesn't exist." % working_dir)
        return True


def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=3):
    """
    Kill a process tree. SIGTERM is sent first, then SIGKILL.
    If a process survives that a psutil.TimeoutExpired is raised
    If everything goes well None is the return value
    """
    if pid == os.getpid():
        raise RuntimeError("I refuse to kill myself")
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:    # Parent likely dies on child death so just ignore that
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout)
    if alive:
        for p in alive:
            p.send_signal(signal.SIGKILL)
    gone, alive = psutil.wait_procs(children, timeout=timeout)
    if alive:
        raise psutil.TimeoutExpired("Failed to stop or kill a process")


def _silent_delete_job(jid):
    """Delete a job from current database, returns only success or failure"""
    try:
        query_db("DELETE FROM user_queue WHERE jid=?", [jid], insert=True)
        query_db("DELETE FROM project_details WHERE jid=?", [jid], insert=True)
    except sqlite3.Error:
        flash("For some reason couldn't delete %s from database. "
              "Perhaps it already doesn't exist?" % jid, 'alert')

