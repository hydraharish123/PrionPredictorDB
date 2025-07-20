#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os
import sys
import glob
from os.path import join, isfile

_setup_script_path = os.path.dirname(os.path.abspath(__file__))
_data_path = os.path.join(_setup_script_path, "aggrescan", "data")
if not os.path.exists(_data_path):
    print "data folder not available from %s. Qutting." % _data_path
    sys.exit(1)

all_files = glob.glob(join("a3d_gui", "*"))
final_list = []
while all_files:
    item = all_files.pop()
    if isfile(item):
        final_list.append(item)
    else:
        for i in glob.glob(join(item, "*")):
            all_files.append(i)


setup(
    name='Aggrescan3D',
    version='1.1.0',
    packages=['aggrescan', 'a3d_gui'],
    url='https://bitbucket.org/lcbio/aggrescan3d',
    license='free for non-commercial users',
    author='Laboratory of Computational Biology',
    description='Aggrescan3D - protein aggregation analysis standalone application',
    install_requires=['numpy', 'matplotlib>=2.0', 'requests'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'aggrescan = aggrescan.__main__:run_program',
            'a3d_server = a3d_gui.run_server:run_server'
        ]
    },
    package_data={'aggrescan': [os.path.join('data', '*'),
                                os.path.join('data', 'matrices', '*'),
                                os.path.join('data', 'freesasa-2.0.1', 'src', 'freesasa')],
                  'a3d_gui': final_list}
)
