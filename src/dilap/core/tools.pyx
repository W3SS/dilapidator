#imports
# cython: profile=True
#cimport cython

#import dilap.core.base as db
cimport dilap.core.vector as dpv
cimport dilap.core.quaternion as dpq
#cimport dilap.core.ray as dr
#import dilap.core.ray as dr

import math,numpy
import matplotlib.pyplot as plt

PI = numpy.pi
PI2 = PI/2.0
twoPI = PI*2.0

__doc__ = '''General purpose tool functions...'''

###############################################################################
### c space
###############################################################################

# if a is within c of b, return True
# else return False
cdef bint isnear_c(float a,float b,float c = 0.001):
    if abs(a-b) < c:return 1
    else:return 0

# if a is within c of b, return b
# else return a
cdef float near_c(float a,float b,float c = 0.001):
    if abs(a-b) < c:return b
    else:return a

# is a on the interior of (a,b) given an error of d
cdef bint inrange_c(float a,float b,float c,float d = 0.001):
    cdef float r = near_c(near_c(a,b,d),c,d)
    #cdef bint inr = r >= b and r <= c
    cdef bint inr = r > b and r < c
    return inr

# return the index of the smallest value in values
cdef int locate_smallest_c(list values):
    cdef int vcnt = len(values)
    cdef int vx
    cdef float v
    cdef float sv = values[0]
    cdef int si = 0
    for vx in range(1,vcnt):
        v = values[vx]
        if v < sv:
            si = vx
            sv = v
    return si

# return the ordered indices for a list of values (ascending)
cdef list order_ascending_c(list values):
    cdef list xrng = [x for x in range(len(values))]
    cdef list od = list(list(zip(*sorted(zip(values,xrng))))[1])
    #od.reverse()
    return od

# return the shortest angular distance between two angles
cdef float adist_c(float a1,float a2):
    cdef float da = clamp_periodic(a1-a2,0.0,twoPI)
    return da if da < PI else twoPI - da

# is seq1 a cyclic permutation of seq2?
cdef bint cyclic_permutation_c(seq1,seq2):
    cdef int s1cnt = len(seq1)
    cdef int s2cnt = len(seq2)
    cdef int pmdx
    if not s1cnt == s2cnt:return 0
    for pmdx in range(s1cnt):
        perm = seq1[pmdx:] + seq1[:pmdx]
        if perm == seq2:return 1
    return 0

# convert an angle from degrees to radians
cdef float rad_c(float deg):return PI*deg/180.0

# convert an angle from radians to degrees
cdef float deg_c(float rad):return 180.0*rad/PI

# keep the value val bounded by f and c by flooring
cdef float clamp_c(float v,float f,float c):
    if v < f:return f
    elif v > c:return c
    else:return v

# keep the value val bounded by f and c by wrapping around
cdef float clamp_periodic_c(float v,float f,float c):
    period = c - f
    while v < f:v += period
    while v > c:v -= period
    else:return v

# perp distance should get a function??
#cdef float ed = abs(pt.dot(etn)-e1.dot(etn))

# compute the distance from pt to the edge segment e1,e2 along nm
cdef float distance_to_edge_c(dpv.vector pt,dpv.vector e1,dpv.vector e2,dpv.vector nm):
    cdef float eproj11 = dpv.dot_c(e1,nm)
    cdef float eproj12 = dpv.dot_c(e2,nm)
    cdef float pproj   = dpv.dot_c(pt,nm)
    cdef dpv.vector2d eproj = dpv.vector2d(min(eproj11,eproj12),max(eproj11,eproj12))
    return abs(eproj.x - pproj)

# revolve pt around the edge segment e1,e2 by ang
cdef dpv.vector revolve_about_edge_c(dpv.vector pt,dpv.vector e1,dpv.vector e2,float ang):
    cdef dpv.vector etn = e2-e1
    cdef dpq.quaternion q = dpq.q_from_av_c(ang,etn)
    cdef dpv.vector new = (pt-e1).rotate(q).translate(e1)
    return new

# rotate a list of vectors by a quaternion q
cdef list rotate_coords_c(list ps,dpq.quaternion q):
    cdef int pcnt = len(ps)
    cdef int px
    cdef dpv.vector p
    for px in range(pcnt):
        p = <dpv.vector>ps[px]
        p.rotate(q)
    return ps

#######
#######
#######
cdef float angle_between_xy_c(dpv.vector v1,dpv.vector v2):
    cdef float alpha1 = angle_from_xaxis_xy_c(v1)
    cdef float alpha2 = angle_from_xaxis_xy_c(v2)
    return alpha2 - alpha1

cpdef float angle_between_xy(dpv.vector v1,dpv.vector v2):
    return angle_between_xy_c(v1,v2)

cdef float angle_between_c(dpv.vector v1,dpv.vector v2):
    cdef dpv.vector n1 = v1.copy().normalize()
    cdef dpv.vector n2 = v2.copy().normalize()

    #cdef float n12dot = dpv.dot_c(n1,n2)
    cdef float n12dot = n1.x*n2.x + n1.y*n2.y + n1.z*n2.z
    cdef float ang = 0.0
    if   abs(n12dot - 1.0) < 0.000001:return ang
    elif abs(n12dot + 1.0) < 0.000001:return PI
    else:ang = numpy.arccos(n12dot)
    return ang                    

    #cdef float ang = numpy.arccos(dpv.dot_c(n1,n2))
    #return ang

cpdef float angle_between(dpv.vector v1,dpv.vector v2):
    return angle_between_c(v1,v2)

cdef float signed_angle_between_xy_c(dpv.vector v1,dpv.vector v2):
    cdef dpv.vector n1 = v1.xy().normalize()
    cdef dpv.vector n2 = v2.xy().normalize()
    cdef dpv.vector vn
    #cdef float n12dot = dpv.dot_c(n1,n2)
    cdef float n12dot = n1.x*n2.x + n1.y*n2.y + n1.z*n2.z
    cdef float ang = 0.0
    #print('signed_angle_between_xy_c')
    if   abs(n12dot - 1.0) < 0.000001:return ang
    elif abs(n12dot + 1.0) < 0.000001:return PI
    else:ang = numpy.arccos(n12dot)
    vn = n1.cross(n2)
    #if vn.dot(dpv.zhat) < 0.0:ang *= -1.0
    if vn.z < 0.0:ang *= -1.0
    return ang                    

cpdef float signed_angle_between_xy(dpv.vector v1,dpv.vector v2):
    return signed_angle_between_xy_c(v1,v2)

cdef float signed_angle_between_c(dpv.vector v1,dpv.vector v2,dpv.vector n):
    cdef dpv.vector n1 = v1.copy().normalize()
    cdef dpv.vector n2 = v2.copy().normalize()
    cdef float n12dot = n1.x*n2.x + n1.y*n2.y + n1.z*n2.z
    cdef float ang = 0.0
    if   abs(n12dot - 1.0) < 0.000001:return ang
    elif abs(n12dot + 1.0) < 0.000001:return PI
    else:ang = numpy.arccos(n12dot)
    #return ang                    

    #cdef float ang = numpy.arccos(dpv.dot_c(n1,n2))
    cdef dpv.vector vn = n1.cross(n2)
    #if vn.dot(n) < 0.0:ang *= -1.0
    if dpv.dot_c(vn,n) < 0.0:ang *= -1.0
    return ang                    

cpdef float signed_angle_between(dpv.vector v1,dpv.vector v2,dpv.vector n):
    return signed_angle_between_c(v1,v2,n)

cdef float angle_from_xaxis_c(dpv.vector v):
    cdef dpv.vector nv = v.copy().normalize()
    #cdef float xproj = dpv.dot_c(nv,dpv.xhat)
    #cdef float yproj = dpv.dot_c(nv,dpv.yhat)
    cdef float xproj = nv.x
    cdef float yproj = nv.y
    cdef float ang
    #print('angle_from_xaxis_c')
    ang = numpy.arccos(xproj)
    if yproj < 0.0:ang = 2.0*PI - ang
    return ang

cpdef float angle_from_xaxis(dpv.vector v):
    return angle_from_xaxis_c(v)

cdef float angle_from_xaxis_xy_c(dpv.vector v):
    cdef float oldz = v.z
    cdef float angle = angle_from_xaxis_c(v)
    v.z = oldz
    return angle

cpdef float angle_from_xaxis_xy(dpv.vector v):
    return angle_from_xaxis_xy_c(v)

#######
#######
#######

# return a vector normal to the plane containing c1,c2,c3
# returns 0 if c1,c2,c3 are colinear
cdef dpv.vector normal_c(dpv.vector c1,dpv.vector c2,dpv.vector c3):
    cdef dpv.vector c1c2 = dpv.v1_v2_c(c1,c2).normalize()
    cdef dpv.vector c2c3 = dpv.v1_v2_c(c2,c3).normalize()
    cdef dpv.vector cn = c1c2.cross(c2c3).normalize()
    return cn

# return a vector normal to the polygon poly
cdef dpv.vector polygon_normal_c(tuple poly):
    cdef dpv.vector zero = dpv.zero_c()
    cdef dpv.vector c1c2 
    cdef dpv.vector c2c3
    cdef dpv.vector pn = zero

    #c1,c2,c3 = poly[x],poly[x+1],poly[x+2]
    #c1c2 = dpv.v1_v2_c(c1,c2).normalize()
    #c2c3 = dpv.v1_v2_c(c2,c3).normalize()
    #pn = c1c2.cross(c2c3)

    #cdef dpv.vector pn = normal_c(poly[x],poly[x+1],poly[x+2])
    cdef int x = 0
    while pn.near(zero):
        #pn = normal_c(poly[x],poly[x+1],poly[x+2])
        c1,c2,c3 = poly[x],poly[x+1],poly[x+2]
        c1c2 = dpv.v1_v2_c(c1,c2)
        c2c3 = dpv.v1_v2_c(c2,c3)
        cang = angle_between_c(c1c2,c2c3)
        if cang > 0.1 and cang < PI-0.1:pn = c1c2.cross(c2c3)
        x += 1
    return pn.normalize()

# return a vector tanget to the plane containing c1,c2,c3
cdef dpv.vector tangent_c(dpv.vector c1,dpv.vector c2,dpv.vector c3):
    cdef dpv.vector tn = dpv.v1_v2_c(c1,c2).normalize()
    return tn

# given start point s, end point e, and n segments, 
# return a colinear set of points equally spaced between s and e
cdef list point_line_c(dpv.vector s,dpv.vector e,int n):
    cdef list line = [s.copy()]
    cdef dpv.vector tn = dpv.v1_v2_c(s,e)
    cdef float l = tn.magnitude()
    cdef int x
    cdef dpv.vector new
    tn.normalize()
    tn.scale_u(float(l)/n)
    for x in range(n):
        new = line[-1].copy().translate(tn)
        line.append(new)
    return line

# return a ring of points of radius r with n corners
cdef list point_ring_c(float r,int n):
    cdef dpv.vector st = dpv.zero_c().translate_x(r)
    cdef dpv.vector nv
    cdef float alpha = PI*(2.0/n)
    cdef list points = []
    cdef int x
    for x in range(n):
        nv = st.copy().rotate_z(x*alpha)
        points.append(nv)
    return points

# return a square of length,width l,w at position p and zrot a
cdef list square_c(float l,float w,p = None,a = None):
    cdef float l2 = l/2.0
    cdef float w2 = w/2.0
    cdef list cs = [
        dpv.vector(-l2,-w2,0),dpv.vector( l2,-w2,0), 
        dpv.vector( l2, w2,0),dpv.vector(-l2, w2,0)]
    if not a is None:dpv.rotate_z_coords_c(cs,a)
    if not p is None:dpv.translate_coords_c(cs,p)
    return cs

# consider xy project of polygon corners and xy projection of pt
# return 0 is pt is outside of polygon in this projection
cdef bint inside_c(dpv.vector pt,list corners):
    cdef float x = pt.x
    cdef float y = pt.y
    cdef int n = len(corners)
    cdef bint ins = 0
    cdef dpv.vector p1 = corners[0]
    cdef dpv.vector p2
    cdef float p1x
    cdef float p1y
    cdef float p2x
    cdef float p2y
    cdef int i
    p1x,p1y = p1.x,p1.y
    for i in range(n+1):
        p2 = corners[i % n]
        p2x,p2y = p2.x,p2.y
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:ins = 1 - ins
        p1x,p1y = p2x,p2y
    return ins

# return 1 if pt is inside a sphere of radius r centered at c
# otherwise return 0
cdef bint inside_circle_c(dpv.vector pt,dpv.vector c,float r):
    cdef bint ins = not dpv.distance_c(pt,c) > r
    return ins

# given 3 points and a plane, determine the center and radius
# of the circumcenter found in the plane plane by projecting p1,p2,p3
# in the plane
cdef tuple circumscribe_tri_c(dpv.vector p1,dpv.vector p2,dpv.vector p3):
    cdef dpv.vector cp1 = p1.xy()
    cdef dpv.vector cp2 = p2.xy()
    cdef dpv.vector cp3 = p3.xy()
    #cdef dpv.vector e1 = cp1 - cp3
    #cdef dpv.vector e2 = cp2 - cp3
    cdef dpv.vector e1 = dpv.v1_v2_c(cp3,cp1)
    cdef dpv.vector e2 = dpv.v1_v2_c(cp3,cp2)
    cdef float th = angle_between_c(e1,e2)
    cdef float cr = dpv.distance_c(cp1,cp2)/(2*numpy.sin(th))
    cdef dpv.vector cp = e2.copy().scale_u(
        e1.magnitude2())-e1.copy().scale_u(e2.magnitude2())
    cdef dpv.vector fp = p3+cp.cross(e1.cross(e2)).scale_u(
                    1.0/(2.0*(e1.cross(e2).magnitude2())))
    return fp,cr

# given line segment s1, line segment s2
# does s1 overlap the interior or s2?
# a segment is a tuple of two points
cdef bint segments_intersect_c(dpv.vector s11,dpv.vector s12,
            dpv.vector s21,dpv.vector s22,float err = 0.001):
    cdef dpv.vector n1 = dpv.v1_v2_c(s11,s12).rotate_z(PI2)
    cdef dpv.vector n2 
    cdef dpv.vector2d proj1
    cdef dpv.vector2d proj2
    cdef float proj11
    cdef float proj12
    cdef float proj21
    cdef float proj22
    proj11 = s11.x*n1.x + s11.y*n1.y + s11.z*n1.z
    proj12 = s12.x*n1.x + s12.y*n1.y + s12.z*n1.z
    proj21 = s21.x*n1.x + s21.y*n1.y + s21.z*n1.z
    proj22 = s22.x*n1.x + s22.y*n1.y + s22.z*n1.z
    proj1 = dpv.vector2d(min(proj11,proj12),max(proj11,proj12))
    proj2 = dpv.vector2d(min(proj21,proj22),max(proj21,proj22))
    if proj1.x - proj2.x > err and proj2.y - proj1.x > err:
        n2 = dpv.v1_v2_c(s21,s22).rotate_z(PI2)
        proj11 = s11.x*n2.x + s11.y*n2.y + s11.z*n2.z
        proj12 = s12.x*n2.x + s12.y*n2.y + s12.z*n2.z
        proj21 = s21.x*n2.x + s21.y*n2.y + s21.z*n2.z
        proj22 = s22.x*n2.x + s22.y*n2.y + s22.z*n2.z
        proj1 = dpv.vector2d(min(proj11,proj12),max(proj11,proj12))
        proj2 = dpv.vector2d(min(proj21,proj22),max(proj21,proj22))
        if proj2.x - proj1.x > err and proj1.y - proj2.x > err:return 1
    return 0

# calculate the barycentric coordinates of the point pt for the triangle abc
# assume all points are in the xy plane 
cdef tuple barycentric_xy_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c): 
    cdef float v0x =  c.x-a.x
    cdef float v0y =  c.y-a.y
    cdef float v1x =  b.x-a.x
    cdef float v1y =  b.y-a.y
    cdef float v2x = pt.x-a.x
    cdef float v2y = pt.y-a.y
    cdef float dot00 = v0x*v0x + v0y*v0y
    cdef float dot01 = v0x*v1x + v0y*v1y
    cdef float dot02 = v0x*v2x + v0y*v2y
    cdef float dot11 = v1x*v1x + v1y*v1y
    cdef float dot12 = v1x*v2x + v1y*v2y
    cdef float invdenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
    cdef float u = (dot11 * dot02 - dot01 * dot12) * invdenom
    cdef float v = (dot00 * dot12 - dot01 * dot02) * invdenom
    return u,v

# determine if the point pt is inside the triangle abc
# assume all points are in the xy plane 
cdef bint intriangle_xy_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c):
    cdef float u,v
    u,v = barycentric_xy_c(pt,a,b,c)
    if u > 0 or abs(u) < 0.001:
        if v > 0 or abs(v) < 0.001:
            if 1-u-v > 0 or abs(1-u-v) < 0.001:
                return 1
    return 0

# NOTE: DOES THE POINT NEED TO BE PROJECTED INTO THE PLANE OF THE TRIANGLE????
# NOTE: DOES THE POINT NEED TO BE PROJECTED INTO THE PLANE OF THE TRIANGLE????
# NOTE: DOES THE POINT NEED TO BE PROJECTED INTO THE PLANE OF THE TRIANGLE????
# NOTE: DOES THE POINT NEED TO BE PROJECTED INTO THE PLANE OF THE TRIANGLE????
# NOTE: DOES THE POINT NEED TO BE PROJECTED INTO THE PLANE OF THE TRIANGLE????
# calculate the barycentric coordinates of the point pt for the triangle abc
cdef dpv.vector2d barycentric_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c): 
    cdef dpv.vector v0 = dpv.v1_v2_c(a,c)
    cdef dpv.vector v1 = dpv.v1_v2_c(a,b)
    cdef dpv.vector v2 = dpv.v1_v2_c(a,pt)
    cdef float dot00 = v0.x*v0.x + v0.y*v0.y + v0.z*v0.z  
    cdef float dot01 = v0.x*v1.x + v0.y*v1.y + v0.z*v1.z  
    cdef float dot02 = v0.x*v2.x + v0.y*v2.y + v0.z*v2.z  
    cdef float dot11 = v1.x*v1.x + v1.y*v1.y + v1.z*v1.z  
    cdef float dot12 = v1.x*v2.x + v1.y*v2.y + v1.z*v2.z  
    cdef float invdenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
    cdef float u = (dot11 * dot02 - dot01 * dot12) * invdenom
    cdef float v = (dot00 * dot12 - dot01 * dot02) * invdenom
    cdef dpv.vector2d bary = dpv.vector2d(u,v)
    return bary

# determine if the point pt is inside the triangle abc
cdef bint intriangle_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c):
    cdef dpv.vector2d bary = barycentric_c(pt,a,b,c)
    cdef bint i1 = near_c(bary.x,0) >= 0
    cdef bint i2 = near_c(bary.y,0) >= 0
    cdef bint i3 = near_c(1-bary.x-bary.y,0) >= 0
    cdef bint ins = i1 and i2 and i3
    return ins

##### DO WORK
# determine if the point pt is inside the convex polygon poly
cdef bint inconvex_c(dpv.vector pt,tuple poly):
    raise NotImplemented
    # why the hell doenst this work...
    cdef int ecnt = len(poly)
    cdef int edx
    for edx in range(ecnt):
        p0,p1 = poly[edx-1],poly[edx]
        sarea = orient2d_c(p1,p0,pt)
        if near_c(sarea,0) > 0:return 1
    return 0
#####

# determine if the point pt is inside the concave polygon poly
cdef bint inconcave_xy_c(dpv.vector pt,tuple poly):
    cdef dpv.vector p1,p2
    cdef float angle = 0.0
    cdef float ang,n12dot,e1x,e1y,e2x,e2y,e1m,e2m
    cdef int pcnt = len(poly)
    cdef int x
    for x in range(pcnt):
        p1,p2 = poly[x-1],poly[x]
        e1x = p1.x-pt.x
        e1y = p1.y-pt.y
        e2x = p2.x-pt.x
        e2y = p2.y-pt.y
        e1m = math.sqrt(e1x**2+e1y**2)
        e2m = math.sqrt(e2x**2+e2y**2)
        if e1m == 0:return 0
        if e2m == 0:return 0
        e1x /= e1m
        e1y /= e1m
        e2x /= e2m
        e2y /= e2m
        n12dot = e1x*e2x + e1y*e2y
        if   abs(n12dot - 1.0) < 0.0001:ang = 0
        elif abs(n12dot + 1.0) < 0.0001:ang = PI
        else:ang = numpy.arccos(n12dot)
        if e1x*e2y - e1y*e2x < 0.0:ang *= -1.0
        angle += ang
    if abs(angle) < PI:return 0
    else:return 1

# given concave polygon p1, concave polygon p2
# does p1 overlap the interior p2?
# a polygon is a tuple of points
# NOTE: this assumes com(p2) is inside p2!
cdef bint concaves_contains_c(tuple p1,tuple p2):
    cdef bint isegsectfound = 0
    cdef int p1cnt = len(p1)
    cdef int p2cnt = len(p2)
    cdef int px
    cdef int py
    cdef dpv.vector i2 = dpv.com(list(p2))
    if not inconcave_xy_c(i2,p1):return 0
    for px in range(p1cnt):
        if isegsectfound:break
        for py in range(p2cnt):
            if segments_intersect_c(p1[px-1],p1[px],p2[py-1],p2[py]):
                isegsectfound = 1
                break
    return 1-isegsectfound

# given concave polygon p1, concave polygon p2
# determine if facets of p1 intersect facets of p2
# a polygon is a tuple of points
cdef bint concaves_intersect_c(tuple p1,tuple p2):
    cdef bint isegsectfound = 0
    cdef int p1cnt = len(p1)
    cdef int p2cnt = len(p2)
    cdef int px
    cdef int py
    for px in range(p1cnt):
        if isegsectfound:break
        for py in range(p2cnt):
            if segments_intersect_c(p1[px-1],p1[px],p2[py-1],p2[py]):
                isegsectfound = 1
                break
    return isegsectfound

# return the point with the highest y value
cdef dpv.vector find_y_apex_c(list pts):
    cdef dpv.vector hi = pts[0]
    cdef int pcnt = len(pts)
    cdef int px
    for px in range(1,pcnt):
        pt = pts[px]
        if pt.y > hi.y:hi = pt
    return hi

# return the point with the highest x value
cdef dpv.vector find_x_apex_c(list pts):
    cdef dpv.vector hi = pts[0]
    cdef int pcnt = len(pts)
    cdef int px
    for px in range(1,pcnt):
        pt = pts[px]
        if pt.x > hi.x:hi = pt
    return hi

# perform a sweep search of a set a points with respect to another point
cdef dpv.vector sweep_search_c(list pts,dpv.vector center,tangent = None):
    cdef dpv.vector offset = center.copy().flip()
    cdef float tangent_rot
    cdef float tpang
    dpv.translate_coords_c(pts,offset)
    if not tangent is None:
        tangent_rot = angle_from_xaxis_xy_c(tangent)
        dpv.rotate_z_coords_c(pts,-tangent_rot)
    cdef dpv.vector which = center
    cdef float pang = twoPI
    cdef int pcnt = len(pts)
    cdef int adx
    cdef dpv.vector pt
    for adx in range(pcnt):
        pt = pts[adx]
        #if pt is center:continue
        if pt.near(center):continue
        tpang = angle_from_xaxis_xy_c(pt)
        if tpang < pang:
            pang = tpang
            which = pt
    if not tangent is None:dpv.rotate_z_coords_c(pts,tangent_rot)
    dpv.translate_coords_c(pts,offset.flip())
    return which

# find a convex hull in the xy-plane for a set of points
# NOTE:pts should not be a colinear set!
cdef list pts_to_convex_xy_c(list pts):
    cdef dpv.vector new = find_x_apex_c(pts)
    cdef list shape = []
    tang = None
    while not new in shape:
        shape.append(new)
        if len(shape) > 1:
            tang = dpv.v1_v2_c(shape[-2],shape[-1]).rotate_z(-0.001)
        new = sweep_search_c(pts,new,tang)
    return shape

# move the points of a convex (or star) polygon along local normals
cdef list inflate_c(list convex,float radius):
    cdef list enorms = dpv.edge_normals_xy_c(convex)
    cdef int ccnt = len(convex)
    cdef int cdx
    cdef dpv.vector lead
    cdef dpv.vector rear
    cdef dpv.vector norm
    for cdx in range(ccnt):
        lead = enorms[cdx]
        rear = enorms[cdx-1]
        norm = dpv.midpoint_c(lead,rear).normalize()
        convex[cdx].translate(norm.scale_u(radius))
    return convex

# add index offset to a list of faces
cdef list offset_faces_c(list faces,int offset):
    cdef int fcnt = len(faces)
    cdef int fdx
    cdef list fa
    for fdx in range(fcnt):
        fa = faces[fdx]
        #tfcnt = len(fa)
        #for tfdx in range(tfcnt):
        #    fa[tfdx] += offset
        fa[0] += offset
        fa[1] += offset
        fa[2] += offset
    return faces

# copy a polygon: (extbnd,(holes...)) 
cdef tuple copy_polygon_c(tuple polygon):
    cdef list eb = [x.copy() for x in polygon[0]]
    cdef list ibnds = []
    for ibnd in polygon[1]:
        ibnds.append(tuple([x.copy() for x in ibnd]))
    return (tuple(eb),tuple(ibnds))

# translate a polygon: (extbnd,(holes...)) by vector tv
cdef tuple translate_polygon_c(tuple polygon,dpv.vector tv):
    cdef tuple ebnd
    cdef tuple ibnds
    cdef tuple ibnd
    ebnd,ibnds = polygon
    cdef int elen = len(ebnd)
    cdef int ex
    cdef int islen = len(ibnds)
    cdef int ibx
    cdef int ilen 
    cdef int ix
    for ex in range(elen):
        ebnd[ex].translate(tv)
    for ibx in range(islen):
        ibnd = ibnds[ibx]
        ilen = len(ibnd)
        for ix in range(ilen):
            ibnd[ix].translate(tv)
    return polygon

# rotate a polygon: (extbnd,(holes...)) by a quaternion q
cdef tuple rotate_polygon_c(tuple polygon,dpq.quaternion q):
    cdef tuple ebnd
    cdef tuple ibnds
    cdef tuple ibnd
    ebnd,ibnds = polygon
    cdef int elen = len(ebnd)
    cdef int ex
    cdef int islen = len(ibnds)
    cdef int ibx
    cdef int ilen 
    cdef int ix
    for ex in range(elen):
        ebnd[ex].rotate(q)
    for ibx in range(islen):
        ibnd = ibnds[ibx]
        ilen = len(ibnd)
        for ix in range(ilen):
            ibnd[ix].rotate(q)
    return polygon

# rotate a polygon: (extbnd,(holes...)) by float a around xhat
cdef tuple rotate_x_polygon_c(tuple polygon,float a):
    cdef tuple ebnd
    cdef tuple ibnds
    cdef tuple ibnd
    ebnd,ibnds = polygon
    cdef int elen = len(ebnd)
    cdef int ex
    cdef int islen = len(ibnds)
    cdef int ibx
    cdef int ilen 
    cdef int ix
    for ex in range(elen):
        ebnd[ex].rotate_x(a)
    for ibx in range(islen):
        ibnd = ibnds[ibx]
        ilen = len(ibnd)
        for ix in range(ilen):
            ibnd[ix].rotate_x(a)
    return polygon

# translate a polygon: (extbnd,(holes...)) by float a around zhat
cdef tuple rotate_z_polygon_c(tuple polygon,float a):
    cdef tuple ebnd
    cdef tuple ibnds
    cdef tuple ibnd
    ebnd,ibnds = polygon
    cdef int elen = len(ebnd)
    cdef int ex
    cdef int islen = len(ibnds)
    cdef int ibx
    cdef int ilen 
    cdef int ix
    for ex in range(elen):
        ebnd[ex].rotate_z(a)
    for ibx in range(islen):
        ibnd = ibnds[ibx]
        ilen = len(ibnd)
        for ix in range(ilen):
            ibnd[ix].rotate_z(a)
    return polygon

# return the signed area of the triangle created 
# by the vectors a-c,b-c
# return 0 if a,b,c are colinear
# this assumes theyre in the xy plane!!!
cdef float orient2d_c(dpv.vector a,dpv.vector b,dpv.vector c):
    cdef float m11 = a.x-c.x
    cdef float m12 = a.y-c.y
    cdef float m21 = b.x-c.x
    cdef float m22 = b.y-c.y
    cdef float det = m11*m22-m12*m21
    return near_c(det,0)

# return the signed volume of the parallelpiped created
# by the vectors a-d,b-d,c-d
# return 0 if a,b,c,d are coplanar
cdef float orient3d_c(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d):
    cdef float m11 = a.x-d.x
    cdef float m12 = a.y-d.y
    cdef float m13 = a.z-d.z
    cdef float m21 = b.x-d.x
    cdef float m22 = b.y-d.y
    cdef float m23 = b.z-d.z
    cdef float m31 = c.x-d.x
    cdef float m32 = c.y-d.y
    cdef float m33 = c.z-d.z
    cdef float det = m11*(m22*m33-m23*m32)-m12*(m21*m33-m23*m31)+m13*(m21*m32-m22*m31)
    return near_c(det,0)

# determine if d is inside the circumcircle of the triangle a,b,c
cdef float incircle_c(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d):
    cdef float m11 = a.x-d.x
    cdef float m12 = a.y-d.y
    cdef float m13 = m11*m11 + m12*m12
    cdef float m21 = b.x-d.x
    cdef float m22 = b.y-d.y
    cdef float m23 = m21*m21 + m22*m22
    cdef float m31 = c.x-d.x
    cdef float m32 = c.y-d.y
    cdef float m33 = m31*m31 + m32*m32
    cdef float det1 = m11*(m22*m33-m23*m32)
    cdef float det2 = m12*(m21*m33-m23*m31)
    cdef float det3 = m13*(m21*m32-m22*m31)
    cdef float incirc = near_c(det1 - det2 + det3,0)
    return incirc

### THIS NEEDS MORE WORK
### THIS NEEDS MORE WORK
### THIS NEEDS MORE WORK
# let a,b,c,d be such that orient3d(a,b,c,d) is nonnegative
# return > 0 if e is inside sphere passing through a,b,c,d
# return < 0 if e is outside sphere passing through a,b,c,d
# return 0 if e is on the surface of the sphere passing through a,b,c,d
# return 0 if all five points are coplanar
cdef float insphere_c(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d,dpv.vector e):
    m11 = a.x-e.x;m12 = a.y-e.y;m13 = a.z-e.z
    m14 = m11*m11 + m12*m12 + m13*m13
    m21 = b.x-e.x;m22 = b.y-e.y;m23 = b.z-e.z
    m24 = m21*m21 + m22*m22 + m23*m23
    m31 = c.x-e.x;m32 = c.y-e.y;m33 = c.z-e.z
    m34 = m31*m31 + m32*m32 + m33*m33
    m41 = d.x-e.x;m42 = d.y-e.y;m43 = d.z-e.z
    m44 = m41*m41 + m42*m42 + m43*m43
    det1 = m11*(m22*(m33*m44-m34*m43)-m23*(m32*m44-m34*m42)+m24*(m32*m43-m33*m42))
    det2 = m12*(m21*(m33*m44-m34*m43)-m23*(m31*m44-m34*m41)+m24*(m31*m43-m33*m41))
    det3 = m13*(m21*(m32*m44-m34*m42)-m22*(m31*m44-m34*m41)+m24*(m31*m42-m32*m41))
    det4 = m14*(m21*(m32*m43-m33*m42)-m22*(m31*m43-m33*m41)+m23*(m31*m42-m32*m41))
    insphr = near_c(det1 - det2 + det3 - det4,0)
    return insphr

###############################################################################
### python space
###############################################################################

# if a is within c of b, return True
# else return False
cpdef bint isnear(float a,float b,float c = 0.0001):
    '''determine if a is within a neighborhood c of b'''
    return isnear_c(a,b,c)

# if a is within c of b, return b
# else return a
cpdef float near(float a,float b,float c = 0.0001):
    '''effectively round a to b if within a neighborhood c'''
    return near_c(a,b,c)

# is a on the interior of (a,b) given an error of d
cpdef bint inrange(float a,float b,float c,float d = 0.0001):
    '''determine if a value is on an open interval'''
    return inrange_c(a,b,c,d)

# return the index of the smallest value in values
cpdef int locate_smallest(list values):
    '''locate the smallest value in a list of values'''
    return locate_smallest_c(values)

# return the ordered indices for a list of values (ascending)
cpdef list order_ascending(list values):
    '''determine the ascending ordering of a list of values'''
    return order_ascending_c(values)

# return the shortest angular distance between two angles
cpdef float adist(float a1,float a2):
    '''find the angular distance between two angles'''
    return adist_c(a1,a2)

# is seq1 a cyclic permutation of seq2?
cpdef bint cyclic_permutation(seq1,seq2):
    '''determine if one sequence is a cyclic permutation of another'''
    return cyclic_permutation_c(seq1,seq2)

# convert an angle from radians to degrees
cpdef float deg(float rad):
    '''convert an angle from radians to degrees'''
    return deg_c(rad)

# convert an angle from degrees to radians
cpdef float rad(float deg):
    '''convert an angle from degrees to radians'''
    return rad_c(deg)

# keep the value val bounded by f and c by flooring
cpdef float clamp(float v,float f,float c):
    '''clamp a float between two floats using closed boundaries'''
    return clamp_c(v,f,c)

# keep the value val bounded by f and c by wrapping around
cpdef float clamp_periodic(float v,float f,float c):
    '''clamp a float between two floats using periodic boundaries'''
    return clamp_periodic_c(v,f,c)

# compute the distance from pt to the edge segment e1,e2 along nm
cpdef float distance_to_edge(dpv.vector pt,dpv.vector e1,dpv.vector e2,dpv.vector nm):
    '''compute the distance from a point to an edge segment along a unit vector'''
    return distance_to_edge_c(pt,e1,e2,nm)

# revolve pt around the edge segment e1,e2 by ang
cpdef dpv.vector revolve_about_edge(dpv.vector pt,dpv.vector e1,dpv.vector e2,float ang):
    '''compute the distance from a point to an edge segment along a unit vector'''
    return revolve_about_edge_c(pt,e1,e2,ang)

# rotate a list of vectors by a quaternion q
cpdef list rotate_coords(list coords,dpq.quaternion q):
    '''rotate a list of vectors by a quaternion'''
    return rotate_coords_c(coords,q)

# return a vector normal to the plane containing c1,c2,c3
# returns 0 if c1,c2,c3 are colinear
cpdef dpv.vector normal(dpv.vector c1,dpv.vector c2,dpv.vector c3):
    '''find a vector normal to the plane containing c1,c2,c3'''
    return normal_c(c1,c2,c3)

# return a vector normal to the polygon poly
cpdef dpv.vector polygon_normal(tuple poly):
    '''find a vector normal to a polygon'''
    return polygon_normal_c(poly)

# return a vector tanget to the plane containing c1,c2,c3
cpdef dpv.vector tangent(dpv.vector c1,dpv.vector c2,dpv.vector c3):
    '''find a vector tangent to the plane containing c1,c2,c3'''
    return tangent_c(c1,c2,c3)

# return a ring of points of radius r with n corners
cpdef list point_line(dpv.vector s,dpv.vector e,int n):
    '''return a line of n points starting with s, ending with e'''
    return point_line_c(s,e,n)

# return a ring of points of radius r with n corners
cpdef list point_ring(float r,int n):
    '''return a ring of points of radius r with n corners'''
    return point_ring_c(r,n)

# return a square of length,width l,w at position p and zrot a
cpdef list square(float l,float w,p = None,a = None):
    '''return a rectangle centered and oriented about a point in the xy plane'''
    return square_c(l,w,p,a)

# consider xy project of polygon corners and xy projection of pt
# return 0 is pt is outside of polygon in this projection
cpdef bint inside(dpv.vector pt,list corners):
    '''determine whether a polygon contains a point'''
    return inside_c(pt,corners)

# return 1 if pt is inside a sphere of radius r centered at c
# otherwise return 0
cpdef bint inside_circle(dpv.vector pt,dpv.vector c,float r):
    '''determine whether a point is contained by a circle'''
    return inside_circle_c(pt,c,r)

# given 3 points and a plane, determine the center and radius
# of the circumcenter found in the plane plane by projecting p1,p2,p3
# in the plane
cpdef tuple circumscribe_tri(dpv.vector p1,dpv.vector p2,dpv.vector p3):
    '''return the circumcenter and circumradius of a triangle'''
    return circumscribe_tri_c(p1,p2,p3)
                                            
# given line segment s1, line segment s2
# does s1 overlap the interior or s2?
# a segment is a tuple of two points
cpdef bint segments_intersect(dpv.vector s11,dpv.vector s12,
            dpv.vector s21,dpv.vector s22,float err = 0.001):
    '''determine if two line segments intersect or not'''
    return segments_intersect_c(s11,s12,s21,s22,err)

# calculate the barycentric coordinates of the point pt for the triangle abc
# assume all points are in the xy plane
cpdef dpv.vector2d barycentric_xy(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c): 
    '''calculate a barycentric representation of a point relative to a triangle in the xy plane'''
    return barycentric_xy_c(pt,a,b,c)

# determine if the point pt is inside the triangle abc
# assume all points are in the xy plane
cpdef bint intriangle_xy(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c):
    '''determine if a point lies within a triangle in the xy plane'''
    return intriangle_xy_c(pt,a,b,c)

# calculate the barycentric coordinates of the point pt for the triangle abc
cpdef dpv.vector2d barycentric(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c): 
    '''calculate a barycentric representation of a point relative to a triangle'''
    return barycentric_c(pt,a,b,c)

# determine if the point pt is inside the triangle abc
cpdef bint intriangle(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c):
    '''determine if a point lies within a triangle'''
    return intriangle_c(pt,a,b,c)
  
# determine if the point pt is inside the convex polygon poly
cpdef bint inconvex(dpv.vector pt,tuple poly):
    '''determine if a pt lies within a convex polygon'''
    return inconvex_c(pt,poly)

# determine if the point pt is inside the concave polygon poly
cpdef bint inconcave_xy(dpv.vector pt,tuple poly):
    '''determine if a point is inside a concave polygon'''
    return inconcave_xy_c(pt,poly)

# given concave polygon p1, concave polygon p2
# does p1 overlap the interior p2?
# a polygon is a tuple of points
# NOTE: this assumes com(p2) is inside p2!
cpdef bint concaves_contains(tuple p1,tuple p2):
    '''determine if one polygon overlaps the interior of another'''
    return concaves_contains_c(p1,p2)

# given concave polygon p1, concave polygon p2
# determine if facets of p1 intersect facets of p2
# a polygon is a tuple of points
cpdef bint concaves_intersect(tuple p1,tuple p2):
    '''determine if the bounds of one polygon intersect those of another'''
    return concaves_intersect_c(p1,p2)

# return the point with the highest y value
cpdef dpv.vector find_y_apex(list pts):
    '''find the point which maximizes the y coordinate within a set of points'''
    return find_y_apex_c(pts)

# return the point with the highest x value
cpdef dpv.vector find_x_apex(list pts):
    '''find the point which maximizes the x coordinate within a set of points'''
    return find_x_apex_c(pts)

# perform a sweep search of a set a points with respect to another point
cpdef dpv.vector sweep_search(list pts,dpv.vector center,tangent = None):
    '''perform a sweep search on a set of points with respect to a point'''
    return sweep_search_c(pts,center,tangent)

# find a convex hull in the xy-plane for a set of points
# NOTE:pts should not be a colinear set!
cpdef list pts_to_convex_xy(list pts):
    '''generate a convex hull in the xy-plane for a set of points'''
    return pts_to_convex_xy_c(pts)

# move the points of a convex (or star) polygon along local normals
cpdef list inflate(list convex,float radius):
    '''inflate a convex polygon along local normals by a radius'''
    return inflate_c(convex,radius)

# add index offset to a list of faces
cpdef list offset_faces(list faces,int offset):
    '''apply an index offset to a list of triangles'''
    return offset_faces_c(faces,offset)

# copy a polygon: (extbnd,(holes...)) 
cpdef tuple copy_polygon(tuple polygon):
    '''create a copy of a concave polygon with holes'''
    return copy_polygon_c(polygon)

# translate a polygon: (extbnd,(holes...)) by vector tv
cpdef tuple translate_polygon(tuple polygon,dpv.vector tv):
    '''translate a concave polygon and its holes by a vector'''
    return translate_polygon_c(polygon,tv)

# rotate a polygon: (extbnd,(holes...)) by a quaternion q
cpdef tuple rotate_polygon(tuple polygon,dpq.quaternion q):
    '''rotate a concave polygon and its holes by a quaternion'''
    return rotate_polygon_c(polygon,q)

# rotate a polygon: (extbnd,(holes...)) by float a about zhat
cpdef tuple rotate_z_polygon(tuple polygon,float a):
    '''rotate a concave polygon and its holes by a float about zhat'''
    return rotate_z_polygon_c(polygon,a)

# rotate a polygon: (extbnd,(holes...)) by float a about xhat
cpdef tuple rotate_x_polygon(tuple polygon,float a):
    '''rotate a concave polygon and its holes by a float about xhat'''
    return rotate_x_polygon_c(polygon,a)

# return the signed area of the triangle created 
# by the vectors a-c,b-c
# return 0 if a,b,c are colinear
# this assumes theyre in the xy plane!!!
cpdef float orient2d(dpv.vector a,dpv.vector b,dpv.vector c):
    '''determine whether a,b,c form a positively oriented triangle'''
    return orient2d_c(a,b,c)

# return the signed volume of the parallelpiped created
# by the vectors a-d,b-d,c-d
# return 0 if a,b,c,d are coplanar
cpdef float orient3d(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d):
    '''determine whether a,b,c,d form a positively oriented tetrahedron'''
    return orient3d_c(a,b,c,d)

# determine if d is inside the circumcircle of the triangle a,b,c
cpdef float incircle(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d):
    '''determine if d is inside the circumcircle of the triangle a,b,c'''
    return incircle_c(a,b,c,d)

# let a,b,c,d be such that orient3d(a,b,c,d) is nonnegative
# return > 0 if e is inside sphere passing through a,b,c,d
# return < 0 if e is outside sphere passing through a,b,c,d
# return 0 if e is on the surface of the sphere passing through a,b,c,d
# return 0 if all five points are coplanar
cpdef float insphere(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d,dpv.vector e):
    '''determine if e is inside the circumsphere of the tetrahedron a,b,c,d'''
    return insphere_c(a,b,c,d,e)








