#cimport dilap.core.tools as dpr

import dilap.geometry.tools as gtl
cimport dilap.geometry.tools as gtl

from dilap.geometry.quat cimport quat

stuff = 'hi'



# dilapidators implementation of a vector in R3
cdef class vec3:

    cdef public float x    
    cdef public float y
    cdef public float z

    cdef vec3 cp_c(self)
    cdef vec3 cpxy_c(self)
    cdef vec3 cpr_c(self)
    cdef vec3 cpf_c(self)
    cdef float d_c(self,vec3 o)
    cdef float dxy_c(self,vec3 o)
    cdef float dexy_c(self,vec3 e1,vec3 e2,bint ie = ?)
    cdef float ang_c(self,vec3 o)
    cdef float sang_c(self,vec3 o,vec3 n)
    cdef float angxy_c(self,vec3 o)
    cdef float dot_c(self,vec3 o)
    cdef vec3 crs_c(self,vec3 o)
    cdef vec3 prj_c(self,vec3 r,vec3 n)
    cdef tuple prjps_c(self,ps)
    cdef tuple baryxy_c(self,vec3 a,vec3 b,vec3 c)
    cdef bint inneighborhood_c(self,vec3 o,float e)
    cdef bint isnear_c(self,vec3 o)
    cdef bint isnearxy_c(self,vec3 o)
    cdef bint inbxy_c(self,ps)
    cdef bint intrixy_c(self,vec3 a,vec3 b,vec3 c)
    cdef bint onsxy_c(self,vec3 s1,vec3 s2,bint ie = ?)
    cdef bint onbxy_c(self,ps)
    cdef bint onpxy_c(self,py)
    cdef float mag2_c(self)
    cdef float mag_c(self)
    cdef vec3 nrm_c(self)
    cdef vec3 trn_c(self,vec3 o)
    cdef vec3 trnos_c(self,os)
    cdef vec3 xtrn_c(self,float d)
    cdef vec3 ytrn_c(self,float d)
    cdef vec3 ztrn_c(self,float d)
    cdef vec3 scl_c(self,vec3 o)
    cdef vec3 uscl_c(self,float s)
    cdef vec3 xscl_c(self,float s)
    cdef vec3 yscl_c(self,float s)
    cdef vec3 zscl_c(self,float s)
    cdef vec3 rot_c(self,quat q)
    cdef vec3 fulc_c(self,quat q,pts)
    cdef list cwoxy_c(self,vec3 fst,ps)
    cdef vec3 xrot_c(self,float a)
    cdef vec3 yrot_c(self,float a)
    cdef vec3 zrot_c(self,float a)
    cdef vec3 flp_c(self)
    cdef vec3 tov_c(self,vec3 o)
    cdef vec3 tovxy_c(self,vec3 o)
    cdef vec3 mid_c(self,vec3 o)
    cdef vec3 lerp_c(self,vec3 o,float ds)
    cdef list pline_c(self,vec3 o,int n)
    cdef list spline_c(self,vec3 o,vec3 st,vec3 ot,int n)
    cdef list ptime_c(self,list ps,list time,float alpha)
    cdef list catmull_rom_c(self,list P,list T,int tcnt)
    cdef float spline__FIXME_c(self,list p,list time,float t)
    cdef list pring_c(self,float r,int n)
    cdef list sq_c(self,float l,float w)
    cdef vec3 com_c(self,os)

    cpdef vec3 cp(self)
    cpdef vec3 cpxy(self)
    cpdef vec3 cpr(self)
    cpdef vec3 cpf(self)
    cpdef float d(self,vec3 o)
    cpdef float dxy(self,vec3 o)
    cpdef float dexy(self,vec3 e1,vec3 e2,bint ie = ?)
    cpdef float ang(self,vec3 o)
    cpdef float sang(self,vec3 o,vec3 n)
    cpdef float angxy(self,vec3 o)
    cpdef float dot(self,vec3 o)
    cpdef vec3 crs(self,vec3 o)
    cpdef vec3 prj(self,vec3 r,vec3 n)
    cpdef tuple prjps(self,ps)
    cpdef tuple baryxy(self,vec3 a,vec3 b,vec3 c)
    cpdef bint inneighborhood(self,vec3 o,float e)
    cpdef bint isnear(self,vec3 o)
    cpdef bint isnearxy(self,vec3 o)
    cpdef bint inbxy(self,ps)
    cpdef bint intrixy(self,vec3 a,vec3 b,vec3 c)
    cpdef bint onsxy(self,vec3 s1,vec3 s2,bint ie = ?)
    cpdef bint onbxy(self,ps)
    cpdef bint onpxy(self,py)
    cpdef float mag2(self)
    cpdef float mag(self)
    cpdef vec3 nrm(self)
    cpdef vec3 trn(self,vec3 o)
    cpdef vec3 trnos(self,os)
    cpdef vec3 xtrn(self,float d)
    cpdef vec3 ytrn(self,float d)
    cpdef vec3 ztrn(self,float d)
    cpdef vec3 scl(self,vec3 o)
    cpdef vec3 uscl(self,float s)
    cpdef vec3 xscl(self,float s)
    cpdef vec3 yscl(self,float s)
    cpdef vec3 zscl(self,float s)
    cpdef vec3 rot(self,quat q)
    cpdef vec3 fulc(self,quat q,pts)
    cpdef list cwoxy(self,vec3 fst,ps)
    cpdef vec3 xrot(self,float a)
    cpdef vec3 yrot(self,float a)
    cpdef vec3 zrot(self,float a)
    cpdef vec3 flp(self)
    cpdef vec3 tov(self,vec3 o)
    cpdef vec3 tovxy(self,vec3 o)
    cpdef vec3 mid(self,vec3 o)
    cpdef vec3 lerp(self,vec3 o,float ds)
    cpdef list pline(self,vec3 o,int n)
    cpdef list spline(self,vec3 o,vec3 st,vec3 ot,int n)
    cpdef list pring(self,float r,int n)
    cpdef list sq(self,float l,float w)
    cpdef vec3 com(self,os)
    cpdef vec3 wrap(self)

# functions to quickly generate R3 basis vectors and their flips
cdef vec3 x_c()
cdef vec3 y_c()
cdef vec3 z_c()
cdef vec3 nx_c()
cdef vec3 ny_c()
cdef vec3 nz_c()

cpdef vec3 x()
cpdef vec3 y()
cpdef vec3 z()
cpdef vec3 nx()
cpdef vec3 ny()
cpdef vec3 nz()








