cimport dilap.core.vector as dpv
cimport dilap.core.quaternion as dpq

cdef float epsilon_c
cdef float epsilonsq_c

cdef float maxfloat_c

cdef bint isnear_c(float a,float b)
cdef float near_c(float a,float b)
cdef bint cyclic_permutation_c(seq1,seq2)
cdef float rad_c(float deg)
cdef float deg_c(float rad)
cdef float clamp_c(float v,float f,float c)
cdef float clamp_periodic_c(float v,float f,float c)
cdef float distance_to_line_c(dpv.vector pt,dpv.vector e1,dpv.vector e2,dpv.vector nm)
cdef float angle_from_xaxis_xy_c(dpv.vector v)
cdef float angle_between_xy_c(dpv.vector v1,dpv.vector v2)
cdef float angle_between_c(dpv.vector v1,dpv.vector v2)
cdef float signed_angle_between_c(dpv.vector v1,dpv.vector v2,dpv.vector n)
cdef float signed_angle_between_xy_c(dpv.vector v1,dpv.vector v2)
cdef dpq.quaternion q_to_xy_c(dpv.vector v)
cdef dpv.vector normal_c(dpv.vector c1,dpv.vector c2,dpv.vector c3)
cdef dpv.vector polygon_normal_c(tuple poly)
cdef dpv.vector tangent_c(dpv.vector c1,dpv.vector c2,dpv.vector c3)
cdef tuple translate_polygon_c(tuple polygon,dpv.vector tv)
cdef tuple rotate_polygon_c(tuple polygon,dpq.quaternion q)
cdef tuple rotate_x_polygon_c(tuple polygon,float a)
cdef list point_line_c(dpv.vector s,dpv.vector e,int n)
cdef list point_ring_c(float r,int n)
cdef list square_c(float l,float w,p = ?,a = ?)
cdef bint inside_c(dpv.vector pt,list corners)
cdef bint inside_circle_c(dpv.vector pt,dpv.vector c,float r)
cdef tuple circumscribe_tri_c(dpv.vector p1,dpv.vector p2,dpv.vector p3)
cdef bint segments_intersect_noncolinear_c(dpv.vector s11,dpv.vector s12,dpv.vector s21,dpv.vector s22)
cdef bint insegment_xy_c(dpv.vector p,dpv.vector s1,dpv.vector s2)
cdef tuple barycentric_xy_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c)
cdef dpv.vector2d barycentric_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c)
cdef bint intriangle_xy_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c)
cdef bint intriangle_c(dpv.vector pt,dpv.vector a,dpv.vector b,dpv.vector c)
cdef bint inconvex_c(dpv.vector pt,tuple poly)
cdef bint inconcave_xy_c(dpv.vector pt,tuple poly)
cdef bint concaves_contains_c(tuple p1,tuple p2)
cdef dpv.vector find_y_apex_c(list pts)
cdef dpv.vector find_x_apex_c(list pts)
cdef dpv.vector sweep_search_c(list pts,dpv.vector center,tangent = ?)
cdef list pts_to_convex_xy_c(list pts)
cdef list inflate_c(list convex,float radius)
cdef list offset_faces_c(list faces,int offset)
cdef float orient2d_c(dpv.vector a,dpv.vector b,dpv.vector c)
cdef float orient3d_c(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d)
cdef float incircle_c(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d)
cdef float insphere_c(dpv.vector a,dpv.vector b,dpv.vector c,dpv.vector d,dpv.vector e)
