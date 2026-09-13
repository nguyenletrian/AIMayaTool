from __future__ import absolute_import

import unittest

from aimayatool.tools.skinning import skirt_parent, topology_region


class _Vec(object):
    def __init__(self, *values):
        if len(values) == 1 and hasattr(values[0], '__iter__'):
            values = tuple(values[0])
        self.x, self.y, self.z = [float(value) for value in values]
    def __sub__(self, other):
        return _Vec(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, other):
        if isinstance(other, _Vec):
            return self.x * other.x + self.y * other.y + self.z * other.z
        return _Vec(self.x * other, self.y * other, self.z * other)


class _OM(object):
    class MSpace(object):
        kWorld = 0
    MVector = _Vec


class _MeshFn(object):
    def __init__(self):
        self.points = [_Vec(-1, 0, -1), _Vec(1, 0, -1), _Vec(1, 0, 1), _Vec(-1, 0, 1)]
        self.edges = {0: (0, 1), 1: (1, 2), 2: (2, 3), 3: (3, 0)}
    def getEdgeVertices(self, edge_id):
        return self.edges[edge_id]
    def getPoints(self, space=None):
        return self.points


class SkirtParentTests(unittest.TestCase):
    def setUp(self):
        self.original_om = topology_region._om
        topology_region._om = lambda: _OM
        self.mesh_fn = _MeshFn()
        self.root_loop = ['mesh.e[0]', 'mesh.e[1]', 'mesh.e[2]', 'mesh.e[3]']
        self.joints = ['j0', 'j1', 'j2', 'j3']
        self.joint_positions = {'j0': (-1, 0, -1), 'j1': (1, 0, -1), 'j2': (1, 0, 1), 'j3': (-1, 0, 1)}
        self.vertex_positions = {'mesh.vtx[0]': (-1, 0, -1), 'mesh.vtx[1]': (1, 0, -1), 'mesh.vtx[2]': (1, 0, 1), 'mesh.vtx[3]': (-1, 0, 1)}

    def tearDown(self):
        topology_region._om = self.original_om

    def _selector(self, mesh, **kwargs):
        pair = kwargs.get('edgeRingPath') or kwargs.get('edgeLoopPath')
        if pair is not None:
            return list(range(min(pair), max(pair) + 1))
        return []

    def _groups(self, mesh, vertices, **kwargs):
        return {vertex: [vertex] for vertex in vertices}

    def _plan(self, **kwargs):
        values = dict(mesh='mesh', joint_parent='parent', joints=self.joints, root_loop=self.root_loop, joint_positions=self.joint_positions, root_vertex_positions=self.vertex_positions, mesh_fn=self.mesh_fn, selector=self._selector, group_builder=self._groups, radius_scale=0.6)
        values.update(kwargs)
        return skirt_parent.build_skirt_parent_plan(**values)

    def test_closed_loop_adds_wrap_span(self):
        plan = self._plan()
        self.assertTrue(plan['closed'])
        self.assertEqual(len(plan['spans']), 4)

    def test_assignment_uses_nearest_joint_radius(self):
        plan = self._plan()
        assignment = next(item for item in plan['assignments'] if item['joint'] == 'j0')
        self.assertAlmostEqual(assignment['radius'], 1.2)
        self.assertEqual(assignment['root_vertices'], ['mesh.vtx[0]'])

    def test_assignments_build_explicit_strips(self):
        plan = self._plan()
        for assignment in plan['assignments']:
            self.assertEqual(set(assignment['strips']), set(assignment['root_vertices']))

    def test_requires_minimum_inputs(self):
        with self.assertRaises(ValueError):
            self._plan(joints=['j0'])
        with self.assertRaises(ValueError):
            self._plan(root_loop=[])


if __name__ == '__main__':
    unittest.main()
