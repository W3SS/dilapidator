import dilap.core.vector as dpv
import dilap.core.quaternion as dpq
import dilap.core.tools as dpr
import dilap.core.context as dgc
import dilap.generate.landscape as dls
import dilap.generate.infrasystem as gif
import dilap.generate.lot as dlt
import dilap.primitive.cube as dcu

class city(dgc.context):

    def _terrain_points(self):
        return self.tpts

    def _hole_points(self):
        return self.hpts

    def _region_points(self):
        return self.rpts

    def generate(self,seed,igraph,worn = 0):
        self._nodes_to_graph(self._node_wrap(
            dcu.cube().scale_u(10).translate_z(5).translate(seed)))
        self.tpts = [seed]
        self.hpts = []
        self.rpts = dpr.point_ring(100*worn,6)
        dpv.translate_coords(self.rpts,seed)

        rsys = gif.infrastructure(igraph).generate(seed,self.rpts,worn)
        self._consume(rsys)
        self.tpts.extend(rsys._terrain_points())
        self.hpts.extend(rsys._hole_points())

        '''#
        bbs = []
        for rd in rsys.roads:
            lotspace = rd._lotspace(bbs)
            dlot = dlt.lot(lotspace[0],lotspace[1]).generate(worn)
            lsppos,lsprot = lotspace[2],lotspace[3]
            dlot._transform(lsppos,lsprot,dpv.one())
            self._consume(dlot)
        '''#
        return self


