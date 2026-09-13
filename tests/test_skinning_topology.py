from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import topology


class _MeshFn(object):
    def __init__(self, edges):
        self.edges = dict(edges)

    def getEdgeVertices(self, edge_id):
        return self.edges[edge_id]


class TopologyTests(unittest.TestCase):
    def test_component_index(self):
        self.assertEqual(topology.component_index('mesh.e[12]'), 12)
        self.assertEqual(topology.component_index(7), 7)

    def test_vertices_from_edges_returns_sorted_unique_vertices(self):
        mesh_fn = _MeshFn({2: (3, 1), 4: (1, 5)})
        self.assertEqual(topology.vertices_from_edges('mesh', ['mesh.e[4]', 'mesh.e[2]'], mesh_fn=mesh_fn), ['mesh.vtx[1]', 'mesh.vtx[3]', 'mesh.vtx[5]'])

    def test_is_edge_loop_closed(self):
        closed = _MeshFn({0: (0, 1), 1: (1, 2), 2: (2, 0)})
        open_chain = _MeshFn({0: (0, 1), 1: (1, 2)})
        self.assertTrue(topology.is_edge_loop_closed('mesh', ['mesh.e[0]', 'mesh.e[1]', 'mesh.e[2]'], mesh_fn=closed))
        self.assertFalse(topology.is_edge_loop_closed('mesh', ['mesh.e[0]', 'mesh.e[1]'], mesh_fn=open_chain))
        self.assertFalse(topology.is_edge_loop_closed('mesh', [], mesh_fn=closed))

    def test_edges_between_ring_then_loop_fallback(self):
        calls = []
        def selector(mesh, **kwargs):
            calls.append(kwargs)
            if 'edgeRingPath' in kwargs:
                return None
            return [2, 3, 4]
        result = topology.edges_between('mesh', 'mesh.e[2]', 'mesh.e[4]', selector=selector)
        self.assertEqual(result, ['mesh.e[2]', 'mesh.e[3]', 'mesh.e[4]'])
        self.assertIn('edgeRingPath', calls[0])
        self.assertIn('edgeLoopPath', calls[1])


if __name__ == '__main__':
    unittest.main()
