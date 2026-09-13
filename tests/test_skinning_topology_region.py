from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import topology_region


class _Vec(object):
    def __init__(self, *values):
        if len(values) == 1 and hasattr(values[0], '__iter__'):
            values = tuple(values[0])
        self.x, self.y, self.z = [float(v) for v in values]
    def __add__(self, other):
        return _Vec(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return _Vec(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, value):
        if isinstance(value, _Vec):
            return self.x * value.x + self.y * value.y + self.z * value.z
        return _Vec(self.x * value, self.y * value, self.z * value)


class _OM(object):
    class MSpace(object):
        kWorld = 0
    MVector = _Vec


class _MeshFn(object):
    def __init__(self):
        self.points = [_Vec(0, 0, 0), _Vec(2, 0, 0), _Vec(4, 0, 0), _Vec(6, 0, 0)]
        self.edges = {0: (0, 1), 1: (1, 2), 2: (2, 3)}
    def getEdgeVertices(self, edge_id):
        return self.edges[edge_id]
    def getPoints(self, space):
        return self.points


class TopologyRegionTests(unittest.TestCase):
    def setUp(self):
        self.original_om = topology_region._om
        topology_region._om = lambda: _OM
        self.mesh_fn = _MeshFn()

    def tearDown(self):
        topology_region._om = self.original_om

    def test_closest_edge_to_point(self):
        edge = topology_region.closest_edge_to_point('mesh', ['mesh.e[0]', 'mesh.e[1]', 'mesh.e[2]'], (4.9, 0, 0), mesh_fn=self.mesh_fn)
        self.assertEqual(edge, 'mesh.e[2]')

    def test_closest_edge_empty(self):
        self.assertIsNone(topology_region.closest_edge_to_point('mesh', [], (0, 0, 0), mesh_fn=self.mesh_fn))

    def test_region_between_points_returns_edges_and_vertices(self):
        def selector(mesh, **kwargs):
            return [0, 1]
        result = topology_region.edge_region_between_points('mesh', ['mesh.e[0]', 'mesh.e[1]', 'mesh.e[2]'], (0.1, 0, 0), (3.5, 0, 0), mesh_fn=self.mesh_fn, selector=selector)
        self.assertEqual(result['source_edge'], 'mesh.e[0]')
        self.assertEqual(result['target_edge'], 'mesh.e[1]')
        self.assertEqual(result['edges'], ['mesh.e[0]', 'mesh.e[1]'])
        self.assertEqual(result['vertices'], ['mesh.vtx[0]', 'mesh.vtx[1]', 'mesh.vtx[2]'])

    def test_region_empty_loop_is_explicit(self):
        result = topology_region.edge_region_between_points('mesh', [], (0, 0, 0), (1, 0, 0), mesh_fn=self.mesh_fn, selector=lambda *args, **kwargs: [])
        self.assertEqual(result, {'source_edge': None, 'target_edge': None, 'edges': [], 'vertices': []})


if __name__ == '__main__':
    unittest.main()
