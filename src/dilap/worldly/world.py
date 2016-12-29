import dilap.core.base as db
import dilap.core.context as cx
import dilap.geometry.tools as gtl
import dilap.modeling.model as dmo
import dilap.modeling.factory as dfa

from dilap.geometry.vec3 import vec3
from dilap.geometry.quat import quat
import dilap.geometry.polymath as pym



import dilap.topology.planargraph as pgr
import dilap.topology.partitiongraph as ptg

import dilap.worldly.terrain as ter
import dilap.worldly.building as blg


#import dilap.worldly.treeskin as ltr

import dilap.worldly.blgsequencing as bseq

#import dilap.worldly.partitiongraph as ptg
import dilap.worldly.roadgraph as rdg

import dilap.worldly.blockletters as dbl



import dilap.core.plotting as dtl
import matplotlib.pyplot as plt

import math,numpy,random,pdb

###############################################################################
### world factory generates full world contexts from a footprint
###############################################################################

class worldfactory(dfa.factory):

    # process of making a world:
    #   generate an xy boundary polygon for the boundary of the world
    #   generate topology in the form of a deterministic function with feedback
    #   partition the interior of the boundary into subsections with type information
    #
    #   place waterways?
    #
    #   create road networks based on region topology
    #       each region has a finite nonzero number of exits
    #           create a network of roads which respects these exits
    #   partition natural and developed regions with 
    #       corridor regions based on road graphs
    #   in developed regions, use the road system to place structures, 
    #       further partitioning the region into developed, buildings, and easements
    #   in natural regions, road graphs are simple and no buildings are present
    #       instead, vegetation and perhaps more extreme topology are added

    def genroadnetwork(self,t):
        # need a graph that spans all landmasses of the continent
        # at boundaries of existing regions, line up the roads nicely
        # within existing regions, add more regions based on road graph
        # develop resulting regions as before

        def trimtofp(p1,p2,r = 5):
            ips = pym.sintbxyp(p1,p2,fp)
            if len(ips) > 0:
                for ip in ips:
                    if ip.isnear(p1):continue
                    p2 = p1.lerp(ip,1-r/p1.d(ip))
            return p2

        rg = pgr.planargraph()
        for lm in t.looptree.below(t.root):
            fp = lm.loop

            #seq = 'S<>G<>L<>'
            #rg = rdg.checkseq(rg,fp,seq,False)
            
            easement = 20

            exp = fp[-1].lerp(fp[0],0.5)
            exn = vec3(0,0,1).crs(fp[-1].tov(fp[0])).nrm()
            ex1 = exp.cp()
            ex2 = ex1.cp().trn(exn.cp().uscl(easement))
            i1 = rg.av(p = ex1,l = 0,w = 0)
            i2,r1 = rg.mev(i1,{'p':ex2,'l':0,'w':0.5},{})
            
            tip = i2
            tv = rg.vs[tip]
            avs = [rg.vs[k] for k in rg.orings[tip]]
            if len(avs) == 1:
                op = tv[1]['p']
                nptn = avs[0][1]['p'].tov(op).nrm().uscl(20)
                np = op.cp().trn(nptn)
                np = trimtofp(op,np,easement)
                nv,nr = rg.mev(tip,{'p':np,'l':0,'w':1},{})

            start = nv
            tip = start
            fp_relax = pym.aggregate(pym.contract(fp,30),30)
            #fp_relax = fp[:]
            for p_relax in fp_relax:
                nv,nr = rg.mev(tip,{'p':p_relax,'l':0,'w':1},{})
                tip = nv
            ne = rg.ae(tip,start,**{})

            ax = rg.plotxy(l = 220)
            plt.show()
            rg.smooth_sticks(1,0.5)
            ax = rg.plotxy(l = 220)
            plt.show()

            ax = dtl.plot_axes_xy(300)
            ax = rg.plotxy(ax)
            ax = dtl.plot_polygon_xy(fp,ax,lw = 2,col = 'b')
            ax = dtl.plot_polygon_xy(fp_relax,ax,lw = 2,col = 'b')
            plt.show()

            #pdb.set_trace()

        #fp = vec3(0,0,0).pring(100,5)
        #rpy = pym.pgtopy(rg,5)

        #ax = dtl.plot_axes_xy(100)
        #ax = dtl.plot_polygon_full_xy(rpy,ax,lw = 2,col = 'b')
        #plt.show()

        return rg

    # generate the topographical data for the world
    def genregions(self,t,r):
        pg = ptg.partitiongraph()
        rpy = pym.pgtopy(r,3)

        #rtl = t.al(rpy[0],t.locloop(rpy[0],1)[0])

        ### create the ocean vertex
        b = t.root.loop
        ov = pg.av(b = [b,[]],p = vec3(0,0,0).com(b),t = ['ocean'])

        ### create landmass vertices
        ls = t.looptree.below(t.root)
        lmvs = []
        for l in ls:
            lv = pg.sv(ov,b,l.loop)
            pg.vs[lv][1]['t'] = ['natural']

            if not rpy is None:
                loops = pym.ebdxy(l.loop,rpy[0])

                '''#
                print('looooopeed',[len(l) for l in loops])
                ax = dtl.plot_axes_xy(100)
                ax = pg.plotxy(ax)
                for j in range(len(loops)):
                    ax = dtl.plot_polygon_xy(loops[j],ax)
                ax = dtl.plot_polygon_full_xy(rpy,ax)
                plt.show()
                '''#

                if len(loops) > 1:
                    for loop in loops[:-1]:
                        rv = pg.sv(lv,l.loop,loop)
                        pg.vs[rv][1]['t'] = ['natural']
                    rv = pg.sv(lv,loops[-1],rpy[0])
                    pg.vs[rv][1]['t'] = ['infrastructure']
                else:
                    rv = pg.sv(lv,loops[0],rpy[0])
                    pg.vs[rv][1]['t'] = ['infrastructure']

                for dpy in rpy[1]:
                    dv = pg.sv(rv,rpy[0],dpy)
                    pg.vs[dv][1]['t'] = ['developed']

                '''#
                ax = dtl.plot_axes_xy(200)
                #ax = r.plotxy(ax)
                ax = pg.plotxy(ax)
                #ax = dtl.plot_polygon_full_xy(rpy,ax)
                plt.show()
                '''#

            lmvs.append(lv)

        ### create the details of each landmass vertex
        for lm in lmvs:self.genregion(t,r,lm,pg)

        ### attach the terrain mesh to the partition vertices...
        for vx in range(pg.vcnt):
            pv = pg.vs[vx]
            if pv is None:continue
            pv[1]['tmesh'] = t

        ### return partition graph
        return pg

    def genregion(self,t,r,v,pg):

        '''#
        coasts = pg.vs[v][1]['b']

        l = [p.cp() for p in coasts[0]]
        r = pym.contract([p.cp() for p in coasts[0]],10,5)

        tl = [p.cp() for p in r]
        par,z = t.locloop(tl)[0],5
        for p in tl:p.ztrn(z)
        tv = t.al(tl,par)

        nv = pg.sv(v,l,r,True,True)
        #pg.vs[nv][1]['t'] = ['developed']

        nv = pg.bv(nv,vec3(0.55,0.65,0),vec3(1,0,0))
        pg.vs[nv[0]][1]['t'] = ['developed']
        '''#

        '''#
        last1 = v
        new = pg.bv(last1,vec3(0.25,0.25,0),vec3(1,0,0))
        pg.vs[last1][1]['t'] = ['developed']
        last2 = new[0]
        new = pg.bv(last2,vec3(0.75,0.75,0),vec3(0,1,0))
        last3 = new[0]
        new = pg.bv(last3,vec3(0.66,0.66,0),vec3(1,0,0))
        last4 = new[0]
        new = pg.bv(last3,vec3(0.33,0.33,0),vec3(0,1,0))
        pg.vs[last3][1]['t'] = ['developed']
        '''#

        ### add infrastructural connectivity for regions
        # create a road network graph...
        #fp = (vec3(0,0,0).pring(100,6),())
        #pv = pg.av(b = fp,p = vec3(0,0,0).com(fp[0]),l = 0)
        #pv = pg.sv(v,pym.ebdxy(pg.vs[v][1]['b'][0],fp[0])[0],fp[0])
        #pg.vs[pv][1]['t'] = ['developed']

        return pg

    # generate the models of the world and add them to the context object
    # NOTE: this should eventually be parallelizable
    def gen(self,w,pg):
        random.seed(0)
        for primarytype in ('ocean','natural','developed','infrastructure'):
            for vx in range(pg.vcnt):
                v = pg.vs[vx]
                if v is None:continue
                if not primarytype in v[1]['t']:continue
                self.vgen(w,v,pg)
        for vx in range(pg.vcnt):
            v = pg.vs[vx]
            if v is None:continue
            if 'ocean' in v[1]['t']:continue
            if not 'infrastructure' in v[1]['t']:
                self.vgen_terrain(w,v,pg)

    ###########################################################################
    ### methods for generating models from descriptive world data
    ###########################################################################

    # vgen takes a context, vertex, and partitiongraph and from that
    #   it generates all models within the space of the vertex
    # this consists of two fundamental steps:
    #   based on the nature of this and adjacent vertices, 
    #       the boundary of this vertex is constrained, 
    #       and meshes which cross it must be forced to appear continuous
    #   based on the nature of this vertex, the interior of the space 
    #       associated with the vertex must be populated with models
    #        - these models must geometrically cover the entire ground surface
    # types:
    #   "natural" - cover with terrain vegetation only edges should only require a terrain seam
    #   "developed" - cover with structures, filling gaps with nature models
    #       edges should only require terrain seams and road seams
    #       where roads may intersect non-colinearly with the boundary only
    #   "corridor" - cover with infrastructure, filling gaps with concrete?
    #       edges should only require terrain seams and road seams
    #       road seems may include colinear intersections with the boundary
    # this supports the idea that all space is either infrastructure, structure, or nature
    def vgen(self,w,v,pg):
        if 't' in v[1]:
            vtypes = v[1]['t']
            #if 'ocean' in vtypes:self.vgen_ocean(w,v,pg)
            if 'ocean' in vtypes:pass
            elif 'natural' in vtypes:self.vgen_natural(w,v,pg)
            elif 'developed' in vtypes:self.vgen_developed(w,v,pg)
            elif 'infrastructure' in vtypes:self.vgen_infrastructure(w,v,pg)
    
    def vgen_ocean(self,w,v,pg,depth = 2,bleed = 5):
        print('ocean vertex',v[0])
        ### create an unrefined flat surface for the bottom of the ocean
        ###  and an unrefined flat surface with contracted holes for the 
        ###  surface of the ocean
        m = dmo.model()
        sgv = w.amodel(None,None,None,m,w.sgraph.root)
        tm = m.agfxmesh()
        gb = v[1]['b']
        #lhs = [pym.contract([p.cp().ztrn(depth) for p in ib],bleed,5) for ib in gb[1]]
        lhs = [pym.contract([p.cp() for p in ib],bleed,5) for ib in gb[1]]
        gb = [[p.cp() for p in gb[0]],lhs]
        wb = [[p.cp().ztrn(depth) for p in gb[0]],
            [[p.cp().ztrn(depth) for p in lh] for lh in lhs]]
        ngvs = m.asurf(gb,tm,fm = 'concrete1',ref = False,hmin = 100,zfunc = None)
        ngvs = m.asurf(wb,tm,fm = 'concrete1',ref = False,hmin = 100,zfunc = None)

    def vgen_natural(self,w,v,pg):
        print('natural vertex',v[0])
        ### create terrain without holes
        #vb = self.vstitch(v,pg)
        #self.vgen_terrain(w,v,pg)

    def vgen_developed(self,w,v,pg):
        print('developed vertex',v[0])
        ### create a child context for a set of buildings within the vertex

        blgs,blgfps = self.vgen_buildings(v,pg)
        for blg in blgs:w.achild(blg.generate(0))

    def vgen_infrastructure(self,w,v,pg):
        print('infrastructure vertex',v[0])
        m = dmo.model()
        sgv = w.amodel(None,None,None,m,w.sgraph.root)
        tm = m.agfxmesh()

        rh = 0.0
        vb = [b.cp().ztrn(rh) for b in v[1]['b'][0]]
        vibs = [[b.cp().ztrn(rh) for b in v[1]['b'][1][x]] 
            for x in range(len(v[1]['b'][1]))]
        vb = self.vstitch(vb,v,pg)
        vibs = [self.vstitch(vib,v,pg) for vib in v[1]['b'][1]]
        v[1]['b'] = vb,vibs

        ngvs = m.asurf((vb,vibs),tm,
            fm = 'concrete1',ref = True,hmin = 100,zfunc = v[1]['tmesh'],
            uvstacked = None,autoconnect = True)
        lockf = lambda p : p.onpxy(v[1]['b']) 
        m.subdiv(tm,False,True,lockf)
        #m.subdiv(tm,False,True,lockf)
        #m.subdiv(tm,False,True,lockf)
        #m.uvs(tm)
        print('generated infrastructure')
        return m

    ###########################################################################

    # create a context representing an entire world
    def new(self,*ags,boundary = None,landmasses = None,**kws):
        ### create the boundary of the world
        if boundary is None:
            #boundary = vec3(0,0,0).pring(5000,8)
            #boundary = vec3(0,0,0).pring(500,8)
            boundary = vec3(0,0,0).pring(250,8)

        ### generate the topographical structure of the world
        t = ter.continent(boundary,landmasses)

        ### generate a graph for infrastructure
        r = self.genroadnetwork(t)
        #r = pgr.planargraph()

        ### generate the region partitions of each landmass
        pg = self.genregions(t,r)

        ### create a world context from the partition graph
        w = self.bclass(*ags,**kws)
        self.gen(w,pg)

        # show the topography
        ax = t.plot(l = 200)
        plt.show()
        # ###################
        return w

    ###########################################################################

    def setseed(self,s = None):
        if s is None:s = self.random.randint(0,1000)
        self.seed = s
        random.seed(self.seed)
        print('set new seed:',self.seed)

    def __str__(self):return 'world factory:'
    def __init__(self,*ags,**kws):
        self._def('seed',0,**kws)
        self._def('bclass',cx.context,**kws)
        dfa.factory.__init__(self,*ags,**kws)
        self.setseed(self.seed)

    ###########################################################################

    # segment the boundary of a vertex based on edges of other vertices
    #def vstitch(self,v,pg,l = 5):
    def vstitch(self,vb,v,pg,l = 10):
        #vb = [b.cp() for b in v[1]['b'][0]]
        if not pym.bccw(vb):vb.reverse()
        fnd = True
        while fnd:
            fnd = False
            for ox in range(pg.vcnt):
                o = pg.vs[ox]
                if o is None or ox == v[0]:continue
                ob = o[1]['b'][0]
                adjs = pym.badjbxy(vb,ob,0.1)
                for adj in adjs:
                    vbx,obx = adj
                    vb1,vb2,ob1,ob2 = vb[vbx-1],vb[vbx],ob[obx-1],ob[obx]
                    ips = pym.sintsxyp(vb1,vb2,ob1,ob2,ieb = 0,skew = 0,ie = 0)
                    if ips is None:continue
                    ip1,ip2 = ips
                    if not ip1 in vb or not ip2 in vb:
                        if ip1.onsxy(vb1,vb2,0):vb.insert(vbx,ip1);fnd = True
                        if ip2.onsxy(vb1,vb2,0):vb.insert(vbx,ip2);fnd = True
                if fnd:break
        vbx = 0
        while vbx < len(vb):
            vb1,vb2 = vb[vbx-1],vb[vbx]
            if vb1.d(vb2) < l:vbx += 1
            else:vb.insert(vbx,vb1.mid(vb2))
        return vb

    def vgen_terrain(self,w,v,pg):
        print('vgen',v[1]['t'])

        tmesh = v[1]['tmesh']
        m = dmo.model()
        sgv = w.amodel(None,None,None,m,w.sgraph.root)
        tm = m.agfxmesh()
        #vstitch isnt being used!!!
        #vstitch isnt being used!!!
        #vstitch isnt being used!!!
        # need to enforce that refinement is no problem for stitching!!!
        # need to enforce that refinement is no problem for stitching!!!
        # need to enforce that refinement is no problem for stitching!!!
        #  need to stitch from holes to interior regions!!!
        #  need to stitch from holes to interior regions!!!
        #  need to stitch from holes to interior regions!!!

        vb = [b.cp() for b in v[1]['b'][0]]
        vibs = [[b.cp() for b in v[1]['b'][1][x]] for x in range(len(v[1]['b'][1]))]
        vb = self.vstitch(vb,v,pg)
        vibs = [self.vstitch(vib,v,pg) for vib in v[1]['b'][1]]
        v[1]['b'] = vb,vibs

        print('generating terrain')
        ngvs = m.asurf((vb,vibs),tm,
            fm = 'grass2',ref = True,hmin = 100,zfunc = v[1]['tmesh'],
            rv = pym.bnrm(vb).z < 0,uvstacked = None,autoconnect = True)
        lockf = lambda p : p.onpxy(v[1]['b']) 
        m.subdiv(tm,False,True,lockf)
        #m.subdiv(tm,False,True,lockf)
        #m.subdiv(tm,False,True,lockf)
        m.uvs(tm)
        print('generated terrain')
        return m

    def vblgsplotch(self,v,pg,easement = 10):
        vb = v[1]['b']
        vbes = [(vb[0][x-1],vb[0][x]) for x in range(len(vb[0]))]
        vbels = [vb[0][x-1].d(vb[0][x]) for x in range(len(vb[0]))]
        vbe_primary = vbels.index(max(vbels))
        vbe_primary_tn = vb[0][vbe_primary-1].tov(vb[0][vbe_primary]).nrm()
        bq = quat(0,0,0,1).uu(vec3(1,0,0),vbe_primary_tn)
        if not bq:bq = quat(1,0,0,0)
        #bq = quat(1,0,0,0)
        vbcon = pym.aggregate(pym.contract(vb[0],easement),5)
        #vbcon = pym.aggregate(pym.contract(vb[0],0),5)

        #ax = dtl.plot_axes_xy(120)
        #ax = dtl.plot_polygon_xy(vbcon,ax,lw = 3,col = 'g')
        #plt.show()

        #if len(fbnd) > 3:fbnd = pinchb(fbnd,epsilon)

        vbxpj = vbe_primary_tn.prjps(vb[0])
        vbypj = vbe_primary_tn.cp().zrot(gtl.PI2).prjps(vb[0])
        vbxl,vbyl = vbxpj[1]-vbxpj[0],vbypj[1]-vbypj[0]

        dx,dy = 20,20
        xn,yn = int(1.5*vbxl/dx),int(1.5*vbyl/dy)
        print('xn,yn',xn,yn)
        #do = vec3(-dx*xn/2.0,-dy*yn/2.0,0)
        o = vec3(0,0,0).com(vbcon)
        vgrid = [o.cp().xtrn(dx*(x-(xn/2.0))).ytrn(dy*(y-(yn/2.0)))
            for x in range(xn) for y in range(yn)]
        boxes = [p.cp().trn(o.flp()).rot(bq).trn(o.flp()).sq(dx,dy) for p in vgrid]
        #boxes = [p.cp().trn(o.flp()).rot(bq).trn(o.flp()).sq(dx,dy) 
        #    for p in vgrid if abs(p.x - o.x) > dx]

        for b in boxes:
            bcom = vec3(0,0,0).com(b).flp()
            bcom.trnos(b)
            bq.rotps(b)
            bcom.flp().trnos(b)
        boxes = [b for b in boxes if pym.binbxy(b,vbcon)]
        for ib in vb[1]:
            boxes = [b for b in boxes if not pym.bintbxy(b,ib) 
                and not b[0].inbxy(ib) and not ib[0].inbxy(b[0])]

        '''#
        ax = dtl.plot_axes_xy(400)
        ax = dtl.plot_point_xy(o,ax)
        ax = dtl.plot_polygon_xy(vb[0],ax,lw = 2,col = 'b')
        ax = dtl.plot_polygon_xy(vbcon,ax,ls = '--',lw = 2,col = 'r')
        #ax = dtl.plot_polygon_xy(box,ax,lw = 2,col = 'r')
        for b in boxes:ax = dtl.plot_polygon_xy(b,ax,lw = 2,col = 'g')
        plt.show()
        '''#

        #blgfps = pym.bsuxy(boxes)
        blgfps = pym.ebuxy_special(boxes,5,4)

        ps = [vec3(0,0,0).com(blgfp) for blgfp in blgfps]
        qs = [bq.cp() for blgfp in blgfps]
        ss = [vec3(1,1,1) for blgfp in blgfps]

        for p,q,s,blgfp in zip(ps,qs,ss,blgfps):
            p.cpxy().flp().trnos(blgfp)
            q.cpf().rotps(blgfp)

        '''#
        ax = dtl.plot_axes_xy(700)
        ax = dtl.plot_point_xy(o,ax)
        ax = dtl.plot_polygon_xy(vb[0],ax,lw = 2,col = 'b')
        #ax = dtl.plot_polygon_xy(box,ax,lw = 2,col = 'r')
        for b in boxes:ax = dtl.plot_polygon_xy(b,ax,lw = 2,col = 'g')
        for b in blgfps:ax = dtl.plot_polygon_xy(b,ax,lw = 2,col = 'r')
        plt.show()
        '''#

        '''#
        bx,by,sx,sy = -30,30,30,30
        r = abs(random.random())*20
        bz = v[1]['tmesh'](bx,by)+r
        blgfps.append(vec3(bx,by,bz).sq(sx,sy))

        bx,by,sx,sy = 30,30,50,30
        r = abs(random.random())*20
        bz = v[1]['tmesh'](bx,by)+r
        blgfps.append(vec3(bx,by,bz).sq(sx,sy))

        bx,by,sx,sy = 30,-30,40,60
        r = abs(random.random())*20
        bz = v[1]['tmesh'](bx,by)+r
        blgfps.append(vec3(bx,by,bz).sq(sx,sy))
        '''#

        #blgfps.append(vec3(bx,by,v[1]['tmesh'](bx,by)).sq(sx,sy))
        #bx,by,sx,sy = 30,30,50,30
        #blgfps.append(vec3(bx,by,v[1]['tmesh'](bx,by)).sq(sx,sy))
        #bx,by,sx,sy = 30,-30,40,60
        #blgfps.append(vec3(bx,by,v[1]['tmesh'](bx,by)).sq(sx,sy))
        #for blgfp in blgfps:
        #    r = v[1]['b'][0][0].z+abs(random.random())*20
        #    for p in blgfp:
        #        p.ztrn(r)
        return zip(ps,qs,ss,blgfps)

    def vgen_buildings(self,v,pg):
        blgfps = self.vblgsplotch(v,pg)
        bfa = blg.blgfactory()
        blgs = []
        for p,q,s,blgfp in blgfps:
            # create a loop denoting the hole in the terrain mesh
            blgth = [p.cp() for p in blgfp]
            q.rotps(blgth)
            p.cpxy().trnos(blgth)
            v[1]['b'][1].append(blgth)
            # create a loop for the terrain mesh
            blgtl = [p.cp() for p in blgfp]
            q.rotps(blgtl)
            p.cpxy().trnos(blgtl)
            blgtv = v[1]['tmesh'].al(blgtl,v[1]['tmesh'].locloop(blgtl,1)[0])
            # create the building given its footprint,p,q,s
            seq = bseq.from_footprint(blgfp,floors = 2*random.randint(1,3))
            nblg = bfa.new(p,q,s,footprint = blgfp,sequence = seq)
            blgs.append(nblg)
        return blgs,blgfps

###############################################################################





