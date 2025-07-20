#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
flask_loc = os.path.dirname(os.path.abspath(__file__))
try:
    from flask import Flask
    app = Flask(__name__)
    config = dict(PAGINATION=45,

                  STATIC=os.path.join(flask_loc, 'static'),
                  PICTURES=os.path.join(flask_loc, 'pictures'),
                  USERJOB_DIRECTORY=os.path.join(flask_loc, 'computations'),
                  DEBUG=True,
                  SECRET_KEY="This_apps_super_secret_key")

    app.config.update(config)

    import viewsutils
    import views
    import db_manager
    import job_handling


    # Create an empty database for the user only if one doesn't exist.
    if not os.path.isfile(os.path.join(flask_loc, 'a3d_database.db')):
        db_manager.create_new_database(os.path.join(flask_loc, 'a3d_database.db'))
        print "Database for your projects has been created."

    app.config.update(dict(DATABASE=os.path.join(flask_loc, 'a3d_database.db')))


except ImportError:
    with open(os.path.join(flask_loc, "requirements.txt"), 'r') as f:
        print "This program requires a few python packages to run: "
        for line in f:
            print line.strip()
        print "Do you wish to use pip to install/upgrade those?"
    test = raw_input("Type 'y' or 'Y' if yes, else press enter to quit\n")
    if test == 'y' or test == 'Y':
        subprocess.Popen(["pip", "install", "-r", os.path.join(flask_loc, "requirements.txt")]).communicate()
    else:
        print "The program has failed to start. Please contact us if you need further assistance."
        sys.exit(0)
    print ""
    print "The program attempted to install necessary packages. Re-run this script to run the app."
    print "Note, the script will fail if you don't have pip installed. If that is the case please" \
          " visit https://pip.pypa.io/en/stable/installing/ for instructions on how to install it."
    print ""

