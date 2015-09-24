# cython: profile=True
#cimport cython

cimport dilap.core.tools as dpr

from dilap.geometry.vec3 cimport vec3

from libc.math cimport sqrt
from libc.math cimport sqrt
from libc.math cimport cos
from libc.math cimport sin
from libc.math cimport tan
from libc.math cimport acos
from libc.math cimport asin
from libc.math cimport hypot
import numpy as np

stuff = 'hi'










__doc__ = '''dilapidator\'s implementation of a quaternion in R3'''
# dilapidators implementation of a quaternion in R3
cdef class quat:

    ###########################################################################
    ### python object overrides ###############################################
    ###########################################################################

    def __str__(self):return 'quat:'+str(tuple(self))
    def __iter__(self):yield self.w;yield self.x;yield self.y;yield self.z
    def __mul__(self,o):return self.mul(o)
    def __add__(self,o):return self.add(o)
    def __sub__(self,o):return self.sub(o)
    def __is_equal(self,o):return self.isnear(o)
    def __richcmp__(x,y,op):
        if op == 2:return x.__is_equal(y)
        else:assert False

    ###########################################################################

    ###########################################################################
    ### c methods #############################################################
    ###########################################################################

    def __cinit__(self,float w,float x,float y,float z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    # given an angle a and axis v, modify to represent 
    # a rotation by a around v and return self
    # NOTE: negative a still maps to positive self.w
    cdef quat av_c(self,float a,vec3 v):
        cdef float a2 = a/2.0
        cdef float sa = sin(a2)
        cdef float vm = v.mag_c()
        self.w = cos(a2)
        self.x = v.x*sa/vm
        self.y = v.y*sa/vm
        self.z = v.z*sa/vm
        return self

    # modify to represent a rotation 
    # between two vectors and return self
    cdef quat uu_c(self,vec3 x,vec3 y):
        cdef float a = x.ang_c(y)
        cdef vec3 v = x.crs_c(y)
        return self.av_c(a,v)

    # return an independent copy of this quaternion
    cdef quat cp_c(self):
        cdef quat n = quat(self.w,self.x,self.y,self.z)
        return n

    # is quat o within a very small neighborhood of self
    cdef bint isnear_c(self,quat o):
        cdef float dw = (self.w-o.w)
        if dw*dw > dpr.epsilonsq_c:return 0
        cdef float dx = (self.x-o.x)
        if dx*dx > dpr.epsilonsq_c:return 0
        cdef float dy = (self.y-o.y)
        if dy*dy > dpr.epsilonsq_c:return 0
        cdef float dz = (self.z-o.z)
        if dz*dz > dpr.epsilonsq_c:return 0
        return 1

    # return the squared magintude of self
    cdef float mag2_c(self):
        cdef float w2 = self.w*self.w
        cdef float x2 = self.x*self.x
        cdef float y2 = self.y*self.y
        cdef float z2 = self.z*self.z
        cdef float m2 = w2 + x2 + y2 + z2
        return m2

    # return the magintude of self
    cdef float mag_c(self):
        return sqrt(self.mag2_c())

    # normalize and return self
    cdef quat nrm_c(self):
        cdef float m = self.mag_c()
        if m == 0.0:return self
        else:return self.uscl_c(1.0/m)

    # flip the direction of and return self
    cdef quat flp_c(self):
        self.w *= -1.0
        return self

    # multiply each component by a scalar of and return self
    cdef quat uscl_c(self,float s):
        self.w *= s
        self.x *= s
        self.y *= s
        self.z *= s
        return self

    # conjugate and return self
    cdef quat cnj_c(self):
        self.x *= -1.0
        self.y *= -1.0
        self.z *= -1.0
        return self

    # compute the inverse of self and return 
    cdef quat inv_c(self):
        cdef m = self.mag2_c()
        cdef quat n = self.cp_().cnj_c().uscl_c(1/m)
        return n

    # given quat o, return self + o
    cdef quat add_c(self,quat o):
        cdef quat n = quat(self.w+o.w,self.x+o.x,self.y+o.y,self.z+o.z)
        return n

    # given quat o, return self - o
    cdef quat sub_c(self,quat o):
        cdef quat n = quat(self.w-o.w,self.x-o.x,self.y-o.y,self.z-o.z)
        return n

    # given quat o, rotate self so that self represents
    # a rotation by self and then q (q * self)
    cdef quat mul_c(self,quat o):
        cdef float nw,nx,ny,nz
        if dpr.isnear_c(self.w,0):nw,nx,ny,nz = o.__iter__()
        elif dpr.isnear_c(o.w,0):nw,nx,ny,nz = self.__iter__()
        else:
            nw = o.w*self.w - o.x*self.x - o.y*self.y - o.z*self.z
            nx = o.w*self.x + o.x*self.w + o.y*self.z - o.z*self.y
            ny = o.w*self.y - o.x*self.z + o.y*self.w + o.z*self.x
            nz = o.w*self.z + o.x*self.y - o.y*self.x + o.z*self.w
        cdef quat n = quat(nw,nx,ny,nz)
        return n

    # given quat o, rotate self so that self represents
    # a rotation by self and then q (q * self)
    cdef quat rot_c(self,quat o):
        cdef quat qres = self.mul_c(o)
        self.w,self.x,self.y,self.z = qres.__iter__()
        return self

    # return the dot product of self and quat o
    cdef float dot_c(self,quat o):
        return self.w*o.w + self.x*o.x + self.y*o.y + self.z*o.z

    # spherically linearly interpolate between 
    # self and quat o proportionally to ds
    cdef quat slerp_c(self,quat o,float ds):
        cdef float hcosth = self.dot_c(o)
        # will need to flip result direction if hcosth < 0????
        if dpr.isnear_c(abs(hcosth),1.0):return self.cp_c()
        cdef float hth    = acos(hcosth)
        cdef float hsinth = sqrt(1.0 - hcosth*hcosth)
        cdef float nw,nx,ny,nz,a,b
        if dpr.isnear_c(hsinth,0): 
            nw = (self.w*0.5 + o.w*0.5)
            nx = (self.x*0.5 + o.x*0.5)
            ny = (self.y*0.5 + o.y*0.5)
            nz = (self.z*0.5 + o.z*0.5)
        else:
            a = sin((1-ds)*hth)/hsinth
            b = sin((  ds)*hth)/hsinth
            nw = (self.w*a + o.w*b)
            nx = (self.x*a + o.x*b)
            ny = (self.y*a + o.y*b)
            nz = (self.z*a + o.z*b)
        cdef quat n = quat(nw,nx,ny,nz)
        return n

    ###########################################################################

    ###########################################################################
    ### python wrappers for c methods #########################################
    ###########################################################################

    # given an angle a and axis v, modify to represent 
    # a rotation by a around v and return self
    cpdef quat av(self,float a,vec3 v):
        '''modify to represent a rotation about a vector by an angle'''
        return self.av_c(a,v)

    # modify to represent a rotation 
    # between two vectors and return self
    cpdef quat uu(self,vec3 x,vec3 y):
        '''modify to represent a rotation from one vector to another'''
        return self.uu_c(x,y)

    # return an independent copy of this quaternion
    cpdef quat cp(self):
        '''create an independent copy of this quaternion'''
        return self.cp_c()

    # is quat o within a very small neighborhood of self
    cpdef bint isnear(self,quat o):
        '''determine if a point is numerically close to another'''
        return self.isnear_c(o)
    
    # return the squared magintude of self
    cpdef float mag2(self):
        '''compute the squared magnitude of this quaternion'''
        return self.mag2_c()

    # return the magintude of self
    cpdef float mag(self):
        '''compute the magnitude of this quaternion'''
        return self.mag_c()

    # normalize and return self
    cpdef quat nrm(self):
        '''normalize this quaternion'''
        return self.nrm_c()

    # flip the direction of and return self
    cpdef quat flp(self):
        '''flip the direction of rotation represented by this quaternion'''
        return self.flp_c()

    # multiply each component by a scalar of and return self
    cpdef quat uscl(self,float s):
        '''multiply components of this point by a scalar'''
        return self.uscl_c(s)

    # conjugate and return self
    cpdef quat cnj(self):
        '''conjugate this quaternion'''
        return self.cnj_c()

    # compute the inverse of self and return 
    cpdef quat inv(self):
        '''compute the inverse of this quaternion'''
        return self.inv_c()

    # given quat o, return self + o
    cpdef quat add(self,quat o):
        '''compute the addition of this quaternion and another'''
        return self.add_c(o)

    # given quat o, return self - o
    cpdef quat sub(self,quat o):
        '''compute the subtraction of this quaternion and another'''
        return self.sub_c(o)

    # given quat o, rotate self so that self represents
    # a rotation by self and then q (q * self)
    cpdef quat mul(self,quat o):
        '''rotate this quaternion by another quaternion'''
        return self.mul_c(o)

    # given quat o, rotate self so that self represents
    # a rotation by self and then q (q * self)
    cpdef quat rot(self,quat o):
        '''rotate this quaternion by another quaternion'''
        return self.rot_c(o)

    # return the dot product of self and quat o
    cpdef float dot(self,quat o):
        '''compute the dot product of this quaternion and another'''
        return self.dot_c(o)

    # spherically linearly interpolate between 
    # self and quat o proportionally to ds
    cpdef quat slerp(self,quat o,float ds):
        '''create a new quat interpolated between this quat and another'''
        return self.slerp_c(o,ds)

    ###########################################################################










