import dilap.core.tools as dpr

import dilap.geometry.tools as gtl
from dilap.geometry.vec3 import vec3
from dilap.geometry.quat import quat
from dilap.geometry.pointset import pointset

from dilap.topology.trimesh import trimesh
from dilap.topology.polygonmesh import polygonmesh

import pdb










__doc__ = '''dilapidator\'s implementation of an all purpose model'''
# dilapidators implementation of an all purpose model
# a model contains geometric information and 
#   topological information which references it
# a model generates application content:
#   a set of trimeshes with position,normal,uv coordinates
#   a set of convex disjoint trimeshes composing a collision hull
#   a set of lod trimeshes
# it contains other objects which can operate on its trimeshes
class model:

    def __str__(self):return 'model:'

    def __init__(self,*args,**kwargs):
        self.gfxmeshes = []
        self.colmeshes = []
        self.lodmeshes = []
        self.polymeshes = []
        self.pset = pointset()
        self.nset = pointset()
        self.uset = pointset()

        #self._def('reps',{},**kwargs)
        #self._def('filename','model.mesh',**kwargs)
        self.filename = 'model.mesh'

    # generate a gfx trimesh for a nice cube
    def atricube(self):
        gmesh = self.agfxmesh()
        v1  = gmesh.avert(*self.avert(vec3(-1,-1,-1)))
        v2  = gmesh.avert(*self.avert(vec3( 1,-1,-1)))
        v3  = gmesh.avert(*self.avert(vec3( 1, 1,-1)))
        v4  = gmesh.avert(*self.avert(vec3(-1, 1,-1)))
        v5  = gmesh.avert(*self.avert(vec3(-1,-1, 1)))
        v6  = gmesh.avert(*self.avert(vec3( 1,-1, 1)))
        v7  = gmesh.avert(*self.avert(vec3( 1, 1, 1)))
        v8  = gmesh.avert(*self.avert(vec3(-1, 1, 1)))
        v9  = gmesh.avert(*self.avert(vec3( 0, 0,-1)))
        v10 = gmesh.avert(*self.avert(vec3( 0, 0, 1)))
        v11 = gmesh.avert(*self.avert(vec3(-1, 0, 0)))
        v12 = gmesh.avert(*self.avert(vec3( 1, 0, 0)))
        v13 = gmesh.avert(*self.avert(vec3( 0,-1, 0)))
        v14 = gmesh.avert(*self.avert(vec3( 0, 1, 0)))
        f1  = gmesh.aface(v1,v9, v2) 
        f2  = gmesh.aface(v2,v9, v3) 
        f3  = gmesh.aface(v3,v9, v4) 
        f4  = gmesh.aface(v4,v9, v1) 
        f5  = gmesh.aface(v5,v6,v10) 
        f6  = gmesh.aface(v6,v7,v10) 
        f7  = gmesh.aface(v7,v8,v10) 
        f8  = gmesh.aface(v8,v5,v10) 
        f9  = gmesh.aface(v1,v2,v13) 
        f10 = gmesh.aface(v2,v6,v13) 
        f11 = gmesh.aface(v6,v5,v13) 
        f12 = gmesh.aface(v5,v1,v13) 
        f13 = gmesh.aface(v3,v4,v14)
        f14 = gmesh.aface(v4,v8,v14)
        f15 = gmesh.aface(v8,v7,v14)
        f16 = gmesh.aface(v7,v3,v14)
        f17 = gmesh.aface(v2,v3,v12)
        f18 = gmesh.aface(v3,v7,v12)
        f19 = gmesh.aface(v7,v6,v12)
        f20 = gmesh.aface(v6,v2,v12)
        f21 = gmesh.aface(v4,v1,v11)
        f22 = gmesh.aface(v1,v5,v11)
        f23 = gmesh.aface(v5,v8,v11)
        f24 = gmesh.aface(v8,v4,v11)
        return gmesh

    # generate a gfx trimesh for a nice dome
    def atridome(self):
        gmesh = self.agfxmesh()
        v1  = gmesh.avert(*self.avert(vec3(-1,-1,-1)))
        v2  = gmesh.avert(*self.avert(vec3( 1,-1,-1)))
        v3  = gmesh.avert(*self.avert(vec3( 1, 1,-1)))
        v4  = gmesh.avert(*self.avert(vec3(-1, 1,-1)))
        v5  = gmesh.avert(*self.avert(vec3(-1,-1, 1)))
        v6  = gmesh.avert(*self.avert(vec3( 1,-1, 1)))
        v7  = gmesh.avert(*self.avert(vec3( 1, 1, 1)))
        v8  = gmesh.avert(*self.avert(vec3(-1, 1, 1)))
        #v9  = gmesh.avert(*self.avert(vec3( 0, 0,-1)))
        v10 = gmesh.avert(*self.avert(vec3( 0, 0, 1)))
        v11 = gmesh.avert(*self.avert(vec3(-1, 0, 0)))
        v12 = gmesh.avert(*self.avert(vec3( 1, 0, 0)))
        v13 = gmesh.avert(*self.avert(vec3( 0,-1, 0)))
        v14 = gmesh.avert(*self.avert(vec3( 0, 1, 0)))
        #f1  = gmesh.aface(v1,v9, v2) 
        #f2  = gmesh.aface(v2,v9, v3) 
        #f3  = gmesh.aface(v3,v9, v4) 
        #f4  = gmesh.aface(v4,v9, v1) 
        f5  = gmesh.aface(v5,v6,v10) 
        f6  = gmesh.aface(v6,v7,v10) 
        f7  = gmesh.aface(v7,v8,v10) 
        f8  = gmesh.aface(v8,v5,v10) 
        f9  = gmesh.aface(v1,v2,v13) 
        f10 = gmesh.aface(v2,v6,v13) 
        f11 = gmesh.aface(v6,v5,v13) 
        f12 = gmesh.aface(v5,v1,v13) 
        f13 = gmesh.aface(v3,v4,v14)
        f14 = gmesh.aface(v4,v8,v14)
        f15 = gmesh.aface(v8,v7,v14)
        f16 = gmesh.aface(v7,v3,v14)
        f17 = gmesh.aface(v2,v3,v12)
        f18 = gmesh.aface(v3,v7,v12)
        f19 = gmesh.aface(v7,v6,v12)
        f20 = gmesh.aface(v6,v2,v12)
        f21 = gmesh.aface(v4,v1,v11)
        f22 = gmesh.aface(v1,v5,v11)
        f23 = gmesh.aface(v5,v8,v11)
        f24 = gmesh.aface(v8,v4,v11)
        return gmesh

    # create new gfx trimesh
    def agfxmesh(self):
        ngm = trimesh()
        self.gfxmeshes.append(ngm)
        return ngm

    # create new col trimesh
    def acolmesh(self):
        ncm = trimesh()
        self.colmeshes.append(ncm)
        return ncm

    # create new lod trimesh
    def alodmesh(self):
        nlm = trimesh()
        self.lodmeshes.append(nlm)
        return nlm

    # create new polygonmesh
    def apolymesh(self):
        npm = polygonmesh()
        self.polymeshes.append(npm)
        return npm

    # given a polygonmesh, add a gfx trimesh to the 
    # model representing the polygonmesh
    def gfx(self,pmesh):
        ngm = self.agfxmesh()

        print('GEN TRIMESH FROM POLYGONMESH PLEASE!!!')
        print('GEN TRIMESH FROM POLYGONMESH PLEASE!!!')
        print('GEN TRIMESH FROM POLYGONMESH PLEASE!!!')

        return ngm

    # create new vertex tuple not present in any 
    # current mesh of the model (new p,n, and/or u)
    # NOTE: a polygonmesh might only need points, so 
    #   it should probably not require this function
    def avert(self,p = None,n = None,u = None):
        if p is None:p = vec3(0,0,0)
        if n is None:n = vec3(0,0,1)
        if u is None:u = vec3(0,0,0)
        px = self.pset.ap(p)
        nx = self.nset.ap(n)
        ux = self.uset.ap(u)
        return px,nx,ux

    # given the indices of some vertices, 
    # return their position vectors
    def gvps(self,mesh,vxs):
        pxs = (mesh.verts[vx][0] for vx in vxs)
        ps = self.pset.gps(pxs)
        return ps

    # subdivide the boundary of the mesh
    def subdivbnd(self,mesh):
        # iterate over the edges
        #   if an edge is a boundary, split it into 3 segments
        #     erase the face attached to it and make a tri fan 
        #     over the 3 new segments
        #   if an edge is not a boundar, ignore it

        #oldvs = list(mesh.ve_rings.keys())
        oldes = list(mesh.ef_rings.keys())

        oldvs = []
        for e in oldes:
            if mesh.eonb(e):
                one = mesh.verts[e[0]]
                two = mesh.verts[e[1]]
                oldvs.append(one)
                #oldvs.append(two)
                ep1,ep2 = self.pset.ps[one[0]],self.pset.ps[two[0]]
                np1,np2 = ep1.pline(ep2,2)
                sv1 = mesh.avert(*self.avert(np1))
                sv2 = mesh.avert(*self.avert(np2))
                mesh.sedge(e,(sv1,sv2))

        dels = []
        for v in oldvs:
            p = self.pset.ps[v[0]]
            vns = (v for v in mesh.mask(0,v,None,None) if mesh.vonb(v))
            # need the subset of vns that is on the boundary too!!!
            pns = self.pset.gps((v[0] for v in vns))
            alpha = mesh.alphan(len(pns))
            sdel = p.tov(gtl.com(pns)).uscl(alpha)
            dels.append((p,sdel))
        for sd in dels:sd[0].trn(sd[1])

    #
    # i really want two fundamental concepts abstractly added
    #   splitting operators which add vertices to the mesh
    #       and maintain topological correctness
    #   smoothing operators which converge to limit surfaces
    #
    # perform a sqrt(3) subdivision on a trimesh
    #   topological splitting of the face
    #   also geometric smooothing afterwards
    def subdiv(self,mesh,subdivbnd = True):
        oldvs = list(mesh.ve_rings.keys())
        oldes = list(mesh.ef_rings.keys())
        for f in list(mesh.fs_mats.keys()):
            v,w,x = f
            mp = gtl.com(self.gvps(mesh,f))
            px,nx,ux = self.avert(mp)
            u = mesh.avert(px,nx,ux)
            mesh.sface(u,v,w,x)
        for u,v in oldes:mesh.fedge(u,v)
        dels = []
        for v in oldvs:
            p = self.pset.ps[v[0]]
            vns = mesh.mask(0,v,None,None)
            pns = self.pset.gps((v[0] for v in vns))
            alpha = mesh.alphan(len(pns))
            sdel = p.tov(gtl.com(pns)).uscl(alpha)
            dels.append((p,sdel))
        for sd in dels:sd[0].trn(sd[1])
        if subdivbnd:self.subdivbnd(mesh)

    # translate the position pointset of the model
    def trn(self,v):
        self.pset.trn(v)
        return self

    # rotate the position and normal pointsets of the model
    def rot(self,q):
        self.pset.rot(q)
        self.nset.rot(q)
        return self

    # scale the position pointset of the model
    def scl(self,s):
        self.pset.mul(s)




 



