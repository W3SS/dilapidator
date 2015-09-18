from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext

import os,numpy,appdirs

core_modules = []
ext_modules = [
    Extension('dilap.geometry.vec3'        ,['dilap/geometry/vec3.pyx',    'dilap/geometry/vec3.pxd']), 
    Extension('dilap.geometry.quat'        ,['dilap/geometry/quat.pyx',    'dilap/geometry/quat.pxd']), 
    Extension('dilap.geometry.pointset'    ,['dilap/geometry/pointset.pyx','dilap/geometry/pointset.pxd']), 

    Extension('dilap.core.vector'        ,['dilap/core/vector.pyx','dilap/core/vector.pxd']), 
    Extension('dilap.core.quaternion'    ,['dilap/core/quaternion.pyx','dilap/core/quaternion.pxd']), 
    Extension('dilap.core.bbox'          ,['dilap/core/bbox.pyx']), 
    Extension('dilap.core.ray'           ,['dilap/core/ray.pyx']), 
    Extension('dilap.core.tools'         ,['dilap/core/tools.pyx','dilap/core/tools.pxd']), 
    Extension('dilap.core.pointset'      ,['dilap/core/pointset.pyx']), 
    Extension('dilap.mesh.triangulate'   ,['dilap/mesh/triangulate.pyx']), 
    Extension('dilap.mesh.tetrahedralize',['dilap/mesh/tetrahedralize.pyx']), 
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
    'dilap.geometry',

    'dilap',
    'dilap.io',
    'dilap.core',
    'dilap.graph',
    'dilap.mesh',
    'dilap.radial_edge',
    'dilap.topology',
    'dilap.primitive',
    'dilap.generate',
    'dilap.degenerate',
    'dilap.infrastructure',
    'dilap.structures',
    'dilap.foliage',
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
    cmdclass = {'build_ext': build_ext},
    include_dirs = [numpy.get_include()], 
    data_files=[(resourcesdir,resourcefils)], 
)




