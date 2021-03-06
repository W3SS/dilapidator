import dilap.core.base as db
import dilap.core.model as dmo
import dilap.core.tools as dpr
import dilap.core.vector as dpv
import dilap.core.quaternion as dpq
import dilap.primitive.cube as dcu

from mpl_toolkits.mplot3d import Axes3D

import pdb,numpy,random

class lane(db.base):

    def __init__(self,*args,**kwargs):
        self._def('road',None,**kwargs)
        self._def('w',5.0,**kwargs)
        # alignment designates the number of lanes between
        # this lane and center of the road to which it belongs
        self._def('alignment',0,**kwargs)
        # direction can be -1,1 or 0
        self._def('direction',1,**kwargs)

    def _tolane(self,ptx):
        nsoffs = [self.road.lanes[lx].w for lx in self.lnstocenter]
        offdst = self.direction*((self.w/2.0)+sum(nsoffs))
        offset = self.road.normals[ptx].copy().scale_u(offdst)
        pt = self.road.vertices[ptx].copy().translate(offset)
        return pt

    def _fromlane(self,ptx):
        raise NotImplemented
        return pt
        
    def _lanestocenter(self):
        lanestocenter = []
        for lx in range(len(self.road.lanes)):
            l = self.road.lanes[lx]
            if l is self or not l.direction == self.direction:continue
            if l.alignment == self.alignment:
                print('two lanes cannot have equal alignment and direction')
                raise ValueError
            elif l.alignment < self.alignment:lanestocenter.append(lx)
        return lanestocenter

    def _geo_pair(self,x):
        inframe = self._tolane(x)
        norm = self.road.normals[x]
        offset = norm.copy().scale_u(self.w/2.0)
        pt1 = inframe.copy().translate(offset)
        pt2 = inframe.copy().translate(offset.flip())
        return pt1,pt2

    # return a model containing this lane
    def _geo(self):
        self.lnstocenter = self._lanestocenter()
        #m = dtm.meshme(pts,None,None,None,[],tris)
        m = dmo.model()
        
        lpt1,lpt2 = self._geo_pair(0)
        m._consume(dcu.cube().translate(lpt1).translate_z(0.5))
        m._consume(dcu.cube().translate(lpt2).translate_z(0.5))

        lrow = [lpt1]
        rrow = [lpt2]

        for pdx in range(1,len(self.road.vertices)):
            pt1,pt2 = self._geo_pair(pdx)

            m._quad(pt1,pt2,lpt2,lpt1)

            lpt1,lpt2 = pt1,pt2
            lrow.append(lpt1)
            rrow.append(lpt2)

            m._consume(dcu.cube().translate(pt1).translate_z(0.5))
            m._consume(dcu.cube().translate(pt2).translate_z(0.5))
        self.leftrow = lrow
        self.rightrow = rrow
        return m
        
# a road is a topological structure where lanes (vertices) are connected
# by sharing edges and merging/splitting
class road(dmo.model):

    def translate(self,v):
        dpv.translate_coords(self.vertices,v)
        dpv.translate_coords(self.controls,v)
        dpv.translate_coords(self.tpts,v)
        for h in self.hpts:dpv.translate_coords(h,v)
        self.start.translate(v)
        self.end.translate(v)
        self.tip.translate(v)
        self.tail.translate(v)
        return dmo.model.translate(self,v)

    def calculate_tips(self,controls):
        eleng = 8.0
        start_tip = self.start.copy().translate(
                self.tail.copy().scale_u(eleng))
        end_tip = self.end.copy().translate(
            self.tip.copy().flip().scale_u(eleng))
        self.controls.insert(1,end_tip)
        for cont in controls:self.controls.insert(1,cont)
        self.controls.insert(1,start_tip)

    def calculate_count(self,v1,v2):
        ds = dpv.distance(v1,v2)
        seglen = 3
        self.lastsegcnt = int(ds/seglen)
        return self.lastsegcnt

    def calculate_tangents(self):
        verts = self.vertices
        tangs = []
        for sgdx in range(1,len(verts)):            
            p1,p2 = verts[sgdx-1],verts[sgdx]
            tangs.append(dpv.v1_v2(p1,p2).normalize())
        tangs.append(self.tip.copy())
        self.tangents = tangs

    def calculate_normals(self):
        thats = self.tangents
        rnms = [that.cross(dpv.zhat).normalize() for that in thats]
        self.normals = rnms

    def calculate_vertices(self):
        verts = [self.start.copy()]
        for dx in range(len(self.controls)-3):
            if len(verts) > 1:verts.pop(-1)
            v1 = self.controls[dx]
            v2 = self.controls[dx+1]
            v3 = self.controls[dx+2]
            v4 = self.controls[dx+3]
            scnt = self.calculate_count(v2,v3)
            verts.extend(dpv.vector_spline(v1,v2,v3,v4,scnt))
        verts.append(self.end.copy())
        self.vertices = verts
        self.calculate_tangents()
        self.calculate_normals()

        #self.set_angles(self.tangents)
        #self.set_corners()
        #self.total_length = self.set_arc_length()
        #self.set_safe_vertices()

    def calculate(self,controls = []):
        self.tipnormal = self.tip.copy().flip().xy()
        self.tipnormal.rotate_z(dpr.rad(-90)).normalize()
        self.tailnormal = self.tail.copy().xy()
        self.tailnormal.rotate_z(dpr.rad(90)).normalize()

        self.controls = [self.start.copy(),self.end.copy()]
        self.calculate_tips(controls)
        self.calculate_vertices()

        #self.plot_vertices()
        #self.xy_bbox()                                

    def plot_vertices(self):
        dpr.plot_points(self.vertices)

    def _terrain_points(self):
        rln = self._leftist()
        lln = self._rightist()
        self.tpts = rln.rightrow+lln.rightrow
        return self.tpts

    def _hole_points(self):
        llnrow = self._leftist().rightrow
        rlnrow = self._rightist().leftrow
        self.hpts = []
        for hdx in range(1,len(rlnrow)):
            hole = [
                rlnrow[hdx-1].copy(),rlnrow[hdx].copy(),
                llnrow[hdx].copy(),llnrow[hdx-1].copy()]
            self.hpts.append(hole)
        return self.hpts

    def _lotspace(self,bbs):

        rdtangs = self.tangents
        rdnorms = self.normals
        #rdwidth = self.total_width
        rdvts = self.vertices
        segcnt = len(rdvts) - 1

        rdist = sum([l.w for l in self._rightside()])
        rdist = 0

        which = random.randint(0,segcnt)
        rvt,rnm = rdvts[which],rdnorms[which].copy()
        lotp = rvt.copy().translate(rnm.scale_u(rdist))
        lotzrot = dpv.angle_from_xaxis_xy(rdtangs[which])

        #####
        #lotzrot = 0.0 
        #####

        l,w,p,q = 50,50,lotp,dpq.q_from_av(lotzrot,dpv.zhat)
        return l,w,p,q

    def __init__(self,start,end,tip,tail,**kwargs):
        dmo.model.__init__(self,**kwargs)
        self.start = start
        self.end = end
        self.tip = tip
        self.tail = tail
        self.calculate()
        if not 'largs' in kwargs:
            self.largs = [
                {'direction':-1,'alignment':0},
                {'direction': 1,'alignment':0},
                {'direction': 1,'alignment':1},
                    ]
        else:self.largs = kwargs['largs']
        self._lanes()

    def _leftist(self):
        ls = self._leftside()
        return self._farside(ls)

    def _leftside(self):
        return self._side(-1)

    def _rightist(self):
        ls = self._rightside()
        return self._farside(ls)

    def _rightside(self):
        return self._side(1)

    def _farside(self,ls):
        la = [l.alignment for l in ls]
        return ls[la.index(max(la))]

    def _side(self,side):
        lanes = []
        for l in self.lanes:
            if l.direction == side:
                lanes.append(l)
        return lanes

    # create a collection of lane objects representing how this road
    # should evolve (merges, shoulders, gutters, sidewalks, etc...)
    def _lanes(self):
        for larg in self.largs:larg['road'] = self
        self.lanes = [lane(**larg) for larg in self.largs]

    # use the lane objects to build a model
    def _geo(self):
        m = dmo.model()
        for l in self.lanes:m._consume(l._geo())
        self._consume(m)

# simple road is a true primitive:
# given a set of interpolated points and other parameters
# form a model that properly represents the road segment
class simpleroad(dmo.model):

    def __init__(self,vs,ts,ns,w,**kwargs):
        dmo.model.__init__(self,**kwargs)
        self.vs = vs
        self.ts = ts
        self.ns = ns
        self.w = w

        #self.calculate()
        if not 'largs' in kwargs:
            self.largs = [
                {'direction':-1,'alignment':0},
                {'direction': 1,'alignment':0},
                {'direction': 1,'alignment':1},
                    ]
        else:self.largs = kwargs['largs']
        self._lanes()

    # create a collection of lane objects representing how this road
    # should evolve (merges, shoulders, gutters, sidewalks, etc...)
    def _lanes(self):
        for larg in self.largs:larg['road'] = self
        self.lanes = [lane(**larg) for larg in self.largs]

    # use the lane objects to build a model
    def _geo(self):
        m = dmo.model()
        for l in self.lanes:m._consume(l._geo())
        self._consume(m)

class intersection(dmo.model):

    def translate(self,v):
        self.p.translate(v)
        dpv.translate_coords(self.tpts,v)
        for h in self.hpts:dpv.translate_coords(h,v)
        return dmo.model.translate(self,v)

    def calculate(self,roads):
        for r in roads:
            pstd = dpv.distance(self.p,r.start)
            pend = dpv.distance(self.p,r.end)
            if pend < pstd:r.end.translate(r.tip.copy().flip().scale_u(10))
            else:r.start.translate(r.tail.copy().scale_u(10))
            r.calculate()

    def _terrain_points(self):
        self.tpts = []
        self.tpts.extend(dpr.corners(20,20,self.p))
        return self.tpts

    def _hole_points(self):
        self.hpts = []
        self.hpts.append(dpr.corners(20,20,self.p))
        return self.hpts

    def __init__(self,p,*roads,**kwargs):
        dmo.model.__init__(self,**kwargs)
        self.p = p
        self.calculate(roads)

    # use the lane objects to build a model
    def _geo(self):
        m = dcu.cube().translate_z(0.5).scale_x(20).scale_y(20).translate(self.p)
        self._consume(m)

# use/modify *args/**kwargs to make a highway like road model
def highway(*args,**kwargs):
    largs = [
        {'direction':-1,'alignment':1},
        {'direction':-1,'alignment':0},
        {'direction': 1,'alignment':0},
        {'direction': 1,'alignment':1},
            ]
    kwargs['largs'] = largs
    hway = road(*args,**kwargs)
    return hway

def circle(rtype,*args,**kwargs):
    ring = dpr.point_ring(100,12)
    ring.append(ring[0])
    tips = [
        dpv.yhat.copy(),dpv.nxhat.copy(),
        dpv.nyhat.copy(),dpv.xhat.copy()]
    tips.append(tips[0])
    roads,isects = [],[]
    for x in range(4):
        kwargs['controls'] = [ring[3*x+1],ring[3*x+2]]
        st,en = ring[(3*x)].copy(),ring[3*(x+1)].copy()
        rd = rtype(st,en,tips[x+1].copy(),tips[x].copy(),**kwargs)
        roads.append(rd)
    for x in range(4):
        r1,r2 = roads[x-1],roads[x]
        isect = intersection(ring[3*x],r1,r2)
        isects.append(isect)
    for r in roads:
        r._geo()
        r._terrain_points()
        r._hole_points()
    for i in isects:
        i._geo()
        i._terrain_points()
        i._hole_points()
    return roads,isects

# given an infragraph, create roads and intersections representing it
def graph_roads(igraph,*args,**kwargs):

    tips = [
        dpv.yhat.copy(),dpv.nxhat.copy(),
        dpv.nyhat.copy(),dpv.xhat.copy()]
    tips.append(tips[0])
    roads,isects = [],[]

    for eg in igraph.edges:
        if eg is None:roads.append(None)
        else:
            '''#
            tip  = eg.one.spikes[eg.two.index].copy().normalize().flip()
            tail = eg.two.spikes[eg.one.index].copy().normalize()
            st = eg.two.p.copy()
            en = eg.one.p.copy()
            rd = highway(st,en,tip,tail,**kwargs)
            '''#
            rd = simpleroad(eg.rpts,eg.rtangents,eg.rnormals,eg.width)
            roads.append(rd)

    for nd in igraph.nodes:
        rds = []
        for rx in range(len(roads)):
            if roads[rx] is None:continue
            eg = igraph.edges[rx]
            if nd is eg.one or nd is eg.two:
                rds.append(roads[rx])
        if len(rds) == 2:continue
        isect = intersection(nd.p,*rds)
        isects.append(isect)

    for r in roads:
        r._geo()
        #r._terrain_points()
        #r._hole_points()
    for i in isects:
        i._geo()
        i._terrain_points()
        i._hole_points()
    return roads,isects

#start = dpv.vector(-100,-300, 20)
#end   = dpv.vector( 100, 300, 40)
#tip  = dpv.vector(0,1,0)
#tail = dpv.vector(1,1,0)
#cs = [dpv.vector(-100,-100, 30),dpv.vector( 100, 100, 40)]
#rd = dr.highway(start,end,tip,tail,controls = cs)
#self.roads = [rd]





