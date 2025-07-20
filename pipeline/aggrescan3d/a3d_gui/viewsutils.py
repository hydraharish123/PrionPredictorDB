#!/usr/bin/env python
# -*- coding: utf-8 -*-

from a3d_gui import app
from flask import render_template, g, request, Response, send_from_directory, abort, jsonify, url_for
import os
from utils import query_db
from db_manager import get_filepath
from server_plot import create_plot, create_mut_plot, create_dyn_plot


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.errorhandler(404)
def page_not_found(error):
    app.logger.warning('Page not found (IP: '+request.remote_addr+') '+request.url)
    return render_template('page_not_found.html', code="404"), 404


@app.errorhandler(500)
def page_error(error):
    app.logger.warning('Page not found (IP: '+request.remote_addr+') '+request.url)
    return render_template('page_not_found.html', code="500"), 500


# This function fixes a mismatch between new csv format and interactive js plotting
# Its here becouse I dont want to mess with js
@app.route('/compute_static/<jobid>/a3d.csv')
def compute_static_a3dtable(jobid):
    o = ""
    with open(get_filepath(jobid, "A3D.csv")) as fw:
        for line in fw:
            line = line.replace("chain", "ch")
            line = line.replace("residue_name", "resn")
            line = line.replace("residue", "resi")
            o += line.replace("protein,", "").replace("folded,", "")
        return Response(o, status=200, mimetype='text/csv')


@app.route('/compute_static/<jobid>/<folder>/<filename>')
def ustatic_folder(jobid, folder, filename):
    data_dir = query_db("SELECT working_dir FROM user_queue WHERE \
            jid=?", [jobid], one=True)[0]
    d = os.path.abspath(os.path.join(data_dir, folder))
    s = os.path.join(d, filename)
    if os.path.exists(s):
        return send_from_directory(d, filename)
    else:
        abort(404)

@app.route('/compute_static/<jobid>/<filename>')
def ustatic(jobid, filename):
    data_dir = query_db("SELECT working_dir FROM user_queue WHERE \
            jid=?", [jobid], one=True)[0]
    s = os.path.join(data_dir, filename)
    if os.path.exists(s):
        return send_from_directory(data_dir, filename)
    else:
        abort(404)


@app.route('/save_picture/<jobid>', methods=['POST'])
def save_uri(jobid):
    try:
        picture = request.json['file_content'].split(',')[1]
        filename = request.json['filename']
        pic_type = request.json['type']
        model = request.json['model']
        while os.path.isfile(os.path.join(app.config['PICTURES'], filename)):
            # TODO this will be bad if more dots, fix maybe
            filename = filename.split(".")[0] + "_1" + "." + filename.split(".")[-1]   # Prevent overwriting
        try:
            with open(os.path.join(app.root_path, 'pictures', filename), 'wb') as f:
                f.write(picture.decode('base64'))
        except IOError:
            os.makedirs(os.path.join(app.root_path, 'pictures'))
            with open(os.path.join(app.root_path, 'pictures', filename), 'wb') as f:
                f.write(picture.decode('base64'))
        query_db("INSERT INTO pictures (jid, filename, type, model) \
                 VALUES(?,?,?,?)",
                 [jobid, filename, pic_type, model], insert=True)
        return Response("%s : %s" % (url_for("serve_pic", filename=filename), filename),
                        status=200, mimetype='text/csv')
    except Exception as e:
        return Response("Something went wrong! Python error: %s" % str(e), status=400, mimetype='text/csv')


@app.route('/serve_picture/<filename>', methods=['GET'])
def serve_pic(filename):
    path = os.path.join(app.root_path, 'pictures', filename)
    if os.path.exists(path):
        return send_from_directory(os.path.join(app.root_path, 'pictures'), filename)
    else:
        return Response("Requested file %s does not exist in pictures folder" % filename,
                        status=400, mimetype="text/plain")


@app.route('/delete_picture', methods=['POST'])
def delete_pic():
    filename = request.json['filename']
    path = os.path.join(app.root_path, 'pictures', filename)
    if os.path.exists(path):
        try:
            os.remove(path)
            query_db("DELETE FROM pictures WHERE filename=? ", [filename], insert=True)
            return Response("Success!", status=200, mimetype="text/plain")
        except OSError:
            return Response("Failed to delete the file. Perhaps you don't have necessary permissions?" % filename,
                            status=400, mimetype="text/plain")
    else:
        return Response("Requested file %s does not exist in pictures folder" % filename,
                        status=400, mimetype="text/plain")


@app.route('/get_pictures_links/<jobid>', methods=['GET'])
def get_pics(jobid):
    query = query_db("SELECT * FROM pictures WHERE jid=?", [jobid])
    if query is None:
        return jsonify([])
    results = []
    for row in query:
        results.append({'path': url_for("serve_pic", filename=row['filename']),
                        'model': row['model'], 'type': row['type'], 'filename': row['filename']})
    return jsonify(results)


# @app.route('/get_plot/<jobid>', methods=['POST'])
# def get_plot(jobid):
#     model = request.json['model']
#     data_dir = query_db("SELECT working_dir FROM user_queue WHERE \
#             jid=?", [jobid], one=True)[0]
#     filepath = os.path.join(data_dir, model + ".csv")
#     script, div = create_plot(filepath, model)
#     results = {'script': script, 'div': div}
#     return jsonify(results)



@app.route('/get_mut_plot/<jobid>', methods=['POST'])
def get_mut_plot(jobid):
    data_dir = query_db("SELECT working_dir FROM user_queue WHERE \
            jid=?", [jobid], one=True)[0]
    try:
        script, div = create_mut_plot(data_dir)
        results = {'script': script, 'div': div}
        return jsonify(results)
    except IOError:     # The plot is requested from a project that misses files
        return Response("No plots were generated as the Mutations.csv file is missing",
                        status=400, mimetype="text/plain")


# Returns a bokeh-created div with a single mutant A3D analysis
@app.route('/get_dyn_plot/<jobid>', methods=['POST'])
def get_dyn_plot(jobid):
    data_dir = query_db("SELECT working_dir FROM user_queue WHERE \
            jid=?", [jobid], one=True)[0]
    try:
        script, div = create_dyn_plot(data_dir)
        results = {'script': script, 'div': div}
        return jsonify(results)
    except IOError:     # The plot is requested from a project that misses files
        return Response("No plots were generated as the model(s) csv file(s) are missing",
                        status=400, mimetype="text/plain")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                               'favicon.png', mimetype='image/png')

@app.route('/contact')
def index_contact():
    return render_template('contact.html')


@app.route('/learn_more')
def learn_more():
    return render_template('_learn_more.html')


@app.route('/tutorial_txt')
def tutorial_txt():
    return render_template('tutorial_text.html')


@app.route('/tutorial')
def tutorial():
    return render_template('_tutorial.html')

