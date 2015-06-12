from distutils.core import setup
from Cython.Build import cythonize

import os,numpy,appdirs

from distutils.extension import Extension
from Cython.Distutils import build_ext

#from setuptools import setup,Extension

core_modules = []
ext_modules = [
    Extension('dp_vector',['cython/dp_vector.c']), 
    Extension('dp_quaternion',['cython/dp_quaternion.c']), 
    Extension('dp_ray',['cython/dp_ray.c']), 
    Extension('dp_bbox',['cython/dp_bbox.c']), 
            ]

resourcesdir = os.path.join(appdirs.user_data_dir(),'dilap_resources')
resourcesrcd = os.path.join(os.getcwd(),'resources')
resourcefils = []

for rpath in os.walk(resourcesrcd):
    rsrcp = rpath[0][len(os.getcwd())+1:]
    for rfile in rpath[2]:
        rfi = '/'.join([rsrcp,rfile])
        resourcefils.append(rfi)

pkgs = [
    'dilap',
    'dilap.io',
    'dilap.core',
    'dilap.core.mesh',
    'dilap.primitive',
    'dilap.generate',
    'dilap.degenerate',
]

setup(
    name="dilapidator",
    version = '1.0',
    description = "dilapidator python pkg",
    author = "ctogle",
    author_email = "cogle@vt.edu",
    license = "MIT License",
    long_description = 'procedural model construction/dilapidation', 
    packages = pkgs, 
    py_modules = core_modules, 
    ext_modules = ext_modules, 
    include_dirs = [numpy.get_include()], 
    data_files=[(resourcesdir,resourcefils)], 
    )




