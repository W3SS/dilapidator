


cdef class pointset:

    def __iter__(self):
        return self.ps.__iter__()

    def __init__(self):
        self.ps = []
        self.pcnt = 0

    def get_points_copy(self,*rng):
        if not rng:rng = range(self.pcnt)
        return [self.ps[x].copy() for x in rng]

    def get_points(self,*rng):
        if not rng:rng = range(self.pcnt)
        return [self.ps[x] for x in rng]

    def add_point(self,np):
        px = self.pcnt
        self.ps.append(np)
        self.pcnt += 1
        return px

    def add_points(self,*nps):
        pxs = self.pcnt
        for np in nps:
            self.ps.append(np)
            self.pcnt += 1
        return range(pxs,self.pcnt)

    def new_point(self,np):
        x = self.find_point(np)
        if x is None:return self.add_point(np)
        else:return x

    def new_points(self,*nps):
        xs = self.find_points(*nps)
        nxs = []
        for x in range(len(nps)):
            if xs[x] is None:nxs.append(self.add_point(nps[x]))
            else:nxs.append(xs[x])
        else:return nxs

    # given a point p, return the index of a point that is near p
    # or return None if no such point exists in self.ps
    def find_point(self,p):
        for px in range(self.pcnt):
            if self.ps[px].near(p):
                return px

    # given a sequence of points, return whatever 
    # find_point would in a one to one sequence
    def find_points(self,*ps):
        return [self.find_point(p) for p in ps]
        
    # is the intersection of self and other nonempty
    def nonempty_intersect(self,other):
        for x in range(self.pcnt):
            p = self.ps[x]
            for y in range(other.pcnt):
                q = other.ps[y]
                if p.near(q):return True
        return False
        



 
