import dilap.core.vector as dpv
import dilap.core.uinfo as di
import dilap.core.sgraph as dsg
import dilap.core.model as dm
import dilap.core.context as dgc
import dilap.io.io as dio
import dilap.primitive.cube as dcu
import dilap.primitive.cone as dco
import dilap.primitive.cylinder as dcyl
import dilap.primitive.wall as dw
import dilap.primitive.floor as df
import dilap.primitive.pipe as dp
import dilap.primitive.road as dr
import dilap.generate.landscape as dls
#import dilap.generate.lot as dlot
#import dilap.generate.street as dstr
#import dilap.generate.continent as dct

from dilap.geometry.vec3 import vec3
import dilap.modeling.model as dmo

import dilap.mesh.piecewisecomplex as pwc
import dilap.mesh.tools as dtl

import dilap.topology.tools.triangulate as dtg

import matplotlib.pyplot as plt

import pdb

iotypes = dio.iotypes

###############################################################################
### functions to realize models,nodes,contexts
###############################################################################

# given either one or many models or nodes
# build all models in world space using iotype io
def build(mods,consume = False,io = None):
    if io is None:io = di.fetch_info()['exporter']
    elif type(io) is type(''):io = iotypes[io]
    if not type(mods) is type([]):mods = [mods]
    for mdx in range(len(mods)):
        m = mods[mdx]
        if issubclass(m.__class__,dm.model): 
            mods[mdx] = dsg.node(models = [m])
    if consume:
        consumenode = dsg.node(children = mods,consumption = True)
        mods = [consumenode]
    sgr = dsg.sgraph(nodes = mods)
    #sgr.graph(iotypes[io])
    sgr.graph(io)

def realize(context,years = 0):
    context.generate(worn = years)
    context.passtime(years)
    context.graph()

###############################################################################

###############################################################################
### simple functions which return simple models
###############################################################################

# return a cube model with sidelength l
def cube(l = 1.0):
    cu = dcu.cube()
    cu.scale_u(l)
    return cu

# return a cylinder model of radius r, height h, with n sides
def cylinder(r = 1.0,h = 1.0,n = 8):
    cu = dcyl.cylinder(n = n)
    cu.scale_u(r).scale_z(h/float(r))
    return cu

# return a cylinder model of radius r, height h, with n sides
def cone(r = 1.0,h = 1.0,n = 8):
    cu = dco.cone(n = n)
    cu.scale_u(r).scale_z(h/float(r))
    return cu

def wall(v1,v2,h = 1.0,w = 0.5,gs = []):
    wa = dw.wall(v1,v2,h = h,w = w,gaps = gs)
    return wa

def perimeter(vs,h = 1.0,w = 0.5):
    v1,v2 = vs[0],vs[1]
    pwa = wall(v1,v2,h = h,w = w)
    for vdx in range(2,len(vs)):
        v1,v2 = vs[vdx-1],vs[vdx]
        wa = wall(v1,v2,h = h,w = w)
        pwa._consume(wa)
    return pwa

def floor(l = 10.0,w = 10.0,h = 0.5,gap = None,m = 'generic'):
    fl = df.floor(l,w,h = h,gap = gap,m = m)
    return fl

def pipe(curve = None,loop = None,m = 'generic'):
    pi = dp.pipe(curve = curve,loop = loop,m = m)
    return pi

def road(start = None,end = None,tip = None,tail = None):
    if start is None:start = dpv.zero()
    if end is None:end = dpv.vector(100,100,-10)
    if tip is None:tip = dpv.vector(0,1,0)
    if tail is None:tail = dpv.vector(0,1,0)
    rd = dr.road(start,end,tip,tail)
    return rd

###############################################################################

def context(io = 'obj',dilaps = []):
    cx = dgc.context(iotype = io,dilapidors = dilaps)
    return cx

def landscape(io = 'obj',dilaps = []):
    cx = dls.landscape(iotype = io,dilapidors = dilaps)
    return cx

def lot(l = 20,w = 40,io = 'obj',dilaps = []):
    cx = dlot.lot(l,w,iotype = io,dilapidors = dilaps)
    return cx

#def street(io = 'obj',dilaps = []):
#    cx = dstr.street(iotype = io,dilapidors = dilaps)
#    return cx

def continent(io = 'obj',dilaps = []):
    cx = dct.continent(iotype = io,dilapidors = dilaps)
    return cx

###############################################################################

###############################################################################
### convenient collections of functions
###############################################################################

# generator is a dict of funcs which return model objects
generator = {
    'cube':cube,
    'cylinder':cylinder,
    'cone':cone,
    'wall':wall,
    'perimeter':perimeter,
    'floor':floor,
    'pipe':pipe,
    'road':road,
    #'context':context,
    #'lot':lot,
}

# contextualizer is a dict of funcs which return context objects
contextualizer = {
    'context':context,
    'landscape':landscape,
    'lot':lot,
    #'street':street,
    'continent':continent,
}

###############################################################################

'''#
def lastteststage(**kwargs):
    plc1 = dtl.box(5,5,5)
    plc2 = dtl.box(5,5,5).translate(dpv.vector(2.5,2.5,2.5))
    #plc3 = pwc.union(plc1,plc2)
    plc3 = dtl.box(5,5,5)

    print('teststage plot')
    ax = dtl.plot_axes()
    ax = plc3.plot(ax)
    plt.show()

    print('build cube now')
    build(cube(10),**kwargs)
'''#

def tridome(mod):
    gmesh = mod.atridome()
    mod.subdiv(gmesh,True)
    mod.subdiv(gmesh,True)
    mod.subdiv(gmesh,True)
    mod.subdiv(gmesh,True)
    #mod.subdiv(gmesh,True)
    #mod.subdiv(gmesh,False)
    #mod.subdiv(gmesh,True)
    return mod

def house(mod):
    gm = mod.agfxmesh()

    eb = (vec3(-2,-2,0),vec3(2,-2,0),vec3(2,2,0),vec3(-2,2,0))
    ibs = ()
    hmin,ref,smo = 1,False,False

    gm.tripoly(eb,ibs,hmin,ref,smo)

    #v1  = gm.avert(*mod.avert(vec3(-1,-1,-1)))
    #v2  = gm.avert(*mod.avert(vec3( 1,-1,-1)))
    #v3  = gm.avert(*mod.avert(vec3( 1, 1,-1)))
    #v4  = gm.avert(*mod.avert(vec3(-1, 1,-1)))
    #f1  = gm.aface(v1,v2,v3) 
    #f2  = gm.aface(v1,v3,v4) 
    return mod

def teststage(**kwargs):
    mod = dmo.model()

    #mod = tridome(mod)
    mod = house(mod)

    ax = dtl.plot_axes()
    for gmesh in mod.gfxmeshes:
        for f in gmesh.faces:
            ps = mod.gvps(gmesh,f)
            ax = dtl.plot_polygon(ps,ax)
    plt.show()

    print('build2 cube now')
    build2(mod,**kwargs)

###############################################################################

# given a model, output its representation in world space
def build2(mod,io = None):
    if io is None:io = di.fetch_info()['exporter']
    elif type(io) is type(''):io = iotypes[io]
    io.build_model2(mod)

def realize(context,years = 0):
    context.generate(worn = years)
    context.passtime(years)
    context.graph()

###############################################################################








                                                                                  

