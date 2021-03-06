import dilap.core.model as dmo
import dilap.core.tools as dpr
import dilap.core.vector as dpv

import pdb

class cube(dmo.model):

    def __init__(self,*args,**kwargs):
        dmo.model.__init__(self,*args,**kwargs)
        self._geo()

    def _geo(self):
        og = dpv.one().scale_u(0.5).flip()
        bottom = [og.copy(),
            og.copy().translate_x(1),
            og.copy().translate_x(1).translate_y(1),
            og.copy().translate_y(1)]
        top = [b.copy().translate_z(1) for b in bottom]
        bottom.reverse()
        self._quad(*bottom)
        self._quad(*top)
        top.reverse()
        bottom.append(bottom[0])
        top.append(top[0])
        self._bridge(bottom,top)


