from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import loop_groups


class _Point(object):
    def __init__(self, x, y, z):
        self.values = (x, y, z)
    def __getitem__(self, index):
        return self.values[index]


class _MeshFn(object):
    def __init__(self):
        self.points = [_Point(0, 0, 0), _Point(1, 0, 0), _Point(2, 0, 0), _Point(0, 1, 0), _Point(1, 1, 0), _Point(2, 1, 0)]
        self.edges = [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
        self.polygons = [(0, 1, 4, 3), (1, 2, 5, 4)]
        self.numEdges = len(self.edges)
        self.numPolygons = len(self.polygons)
    def getEdgeVertices(self, edge_id):
        return self.edges[edge_id]
    def getPolygonVertices(self, face_id):
        return self.polygons[face_id]
    def getPoints(self):
        return self.points


class LoopGroupTests(unittest.TestCase):
    def setUp(self):
        self.mesh_fn = _MeshFn()

    def test_connected_vertices_are_limited_to_set(self):
        result = loop_groups.connected_vertices_in_set('mesh', 'mesh.vtx[1]', ['mesh.vtx[0]', 'mesh.vtx[1]', 'mesh.vtx[2]'], mesh_fn=self.mesh_fn)
        self.assertEqual([item[1] for item in result], ['mesh.vtx[0]', 'mesh.vtx[2]'])

    def test_perpendicular_edge_from_pair(self):
        edge = loop_groups.perpendicular_edge_from_vertices('mesh', 'mesh.vtx[1]', 'mesh.vtx[2]', mesh_fn=self.mesh_fn)
        self.assertEqual(edge, 'mesh.e[5]')

    def test_perpendicular_threshold_rejects_non_perpendicular(self):
        edge = loop_groups.perpendicular_edge_from_vertices('mesh', 'mesh.vtx[0]', 'mesh.vtx[1]', threshold=-0.01, mesh_fn=self.mesh_fn)
        self.assertIsNone(edge)

    def test_api_quad_loop_expansion_without_selector(self):
        result = loop_groups.edge_loop_vertices('mesh', 'mesh.e[5]', mesh_fn=self.mesh_fn)
        self.assertEqual(result, ['mesh.vtx[0]', 'mesh.vtx[1]', 'mesh.vtx[2]', 'mesh.vtx[3]', 'mesh.vtx[4]', 'mesh.vtx[5]'])

    def test_group_vertices_expands_perpendicular_loops(self):
        def selector(mesh, **kwargs):
            return [4, 5, 6]
        result = loop_groups.group_vertices_by_perpendicular_loops('mesh', ['mesh.vtx[0]', 'mesh.vtx[1]', 'mesh.vtx[2]'], mesh_fn=self.mesh_fn, selector=selector)
        self.assertEqual(result['mesh.vtx[1]'], ['mesh.vtx[0]', 'mesh.vtx[1]', 'mesh.vtx[2]', 'mesh.vtx[3]', 'mesh.vtx[4]', 'mesh.vtx[5]'])


if __name__ == '__main__':
    unittest.main()
