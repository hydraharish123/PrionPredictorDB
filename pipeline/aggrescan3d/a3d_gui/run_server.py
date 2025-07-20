#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# Make sure the path to actual files is on the path (the script pretends to be in the parent directory this way)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))


def run_server():
    try:
        from a3d_gui import app
        app.run(host='0.0.0.0', debug=True)
    except ImportError:     # The exception is caught in __init__ but this script raises its own when the import fails
        pass                # Or smth I might not know what exactly happens
