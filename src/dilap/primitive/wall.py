import dilap.core.base as db
import dilap.core.model as dmo
import dilap.primitive.tools as dpr

import dp_vector as dpv

import pdb

class wall(dmo.model):

    def __init__(self,v1,v2,*args,**kwargs):
        dmo.model.__init__(self,*args,**kwargs)
        self._endpoints(v1,v2)
        self._def('h',5.0,**kwargs)
        self._def('w',0.5,**kwargs)
        self._def('gaps',[],**kwargs)
        self._geo()

    # given v1,v2 set all data dep. on endpoints
    def _endpoints(self,v1,v2):
        self.v1 = v1.copy()
        self.v2 = v2.copy()
        self.l = dpv.distance(v1,v2)
        self.center = dpv.midpoint(v1,v2)
        self.tangent = dpv.v1_v2(v1,v2).normalize()
        self.normal = self.tangent.copy()
        self.normal.rotate_z(db.rad(90)).normalize()

    # given gap tang. coord gx and gap width gw, add gap
    def _gap(self,gx,gw):
        l,w = self.l,self.w
        t = self.tangent.copy().scale_u(gx*l)
        c = self.v1.copy().translate(t)
        tw = self.tangent.copy().scale_u(-0.5*gw)
        p1 = c.copy().translate(tw)
        p2 = c.copy().translate(tw.flip())
        gapped = self._add_gap(p1,p2)
        return gapped

    # given g1,g2 (tang. coords), add gap points to self.gaps
    def _add_gap(self,g1,g2):
        def inside(x1,x2,x3):
            d12 = dpv.distance(x1,x2)
            d13 = dpv.distance(x1,x3)
            d23 = dpv.distance(x2,x3)
            if d13 <= d12 and d23 <= d12:return True
            else:return False
        g1d = min([dpv.distance(g1,self.v1),dpv.distance(g1,self.v2)])
        g2d = min([dpv.distance(g2,self.v1),dpv.distance(g2,self.v2)])
        # skip if gap is too close to edges
        if g1d < 2 or g2d < 2:return None
        # skip if gap overlaps existing gap
        for g in self.gaps:
            og1,og2 = g
            if inside(og1,og2,g1) or inside(og1,og2,g2):
                return None
        self.gaps.append((g1,g2))
        return g1,g2

    # add a wall gap characteristic of a window
    def _window_gap(self,dx,fh):
        wh,winh = self.h,0.5*self.h
        dw,dh,dz = 0.75*winh,winh,max([(wh-winh)/2.0,fh+0.5])
        wpts = self._gap(dx,dw)
        if wpts is None:return
          
        #wkws = {'z':dz,'w':dw,'h':dh,'gap':wpts,'wall':self}
        #self._portals.append(po.window(**wkws))

    # add a wall gap characteristic of a door
    def _door_gap(self,dx,fh):
        wh,ch = self.h,self.fh
        dw,dh,dz = 1.5,mpu.clamp(0.8*(wh-fh-ch),2,3),fh
        dpts = self._gap(dx,dw)
        if dpts is None:return

        #dkws = {'z':dz,'w':dw,'h':dh,'gap':dpts,'wall':self}
        #self._portals.append(po.door(**dkws))

    # build segments of wall skipping regions from self.gaps
    def _geo(self):
        spts = []
        spts.append(self.v1)
        for g in self.gaps:spts.extend(g)
        spts.append(self.v2)
        self._segments(spts)

    # given a set of points, build a segment between every other
    def _segments(self,spts):
        w,h = self.w,self.h
        scnt = len(spts)
        wnorm = self.normal.copy().scale_u(abs(w*0.5))
        for s in range(scnt)[::2]:
            s1,s2 = spts[s],spts[s+1]
            self._segment(s1,s2,h,wnorm.copy())

    # build a wall segment
    def _segment(self,v1,v2,h,wnorm):
        b1 = v1.copy().translate(wnorm.flip())
        b2 = v2.copy().translate(wnorm)
        b3 = v2.copy().translate(wnorm.flip())
        b4 = v1.copy().translate(wnorm)
        t1 = b1.copy().translate_z(h)
        t2 = b2.copy().translate_z(h)
        t3 = b3.copy().translate_z(h)
        t4 = b4.copy().translate_z(h)
        bs = [b1,b4,b3,b2,b1]
        ts = [t1,t4,t3,t2,t1]
        nfs = self._bridge(bs,ts)
        #nfs = self._bridge(bs,ts,m = m)
        #nfs = self._bridge(ts,bs,m = m)
        #self._flip_faces(nfs)
        self._project_uv_flat(nfs)

