import unittest

from aimayatool.tools.skinning.skirt_parent_workflow import run_skirt_parent_workflow


class SkirtParentWorkflowTests(unittest.TestCase):
    def test_runs_all_phases_in_order(self):
        calls = []
        plan = {'mesh': 'mesh', 'joint_parent': 'parent', 'assignments': [], 'spans': []}
        smoothing_plan = {'mesh': 'mesh', 'operations': []}

        def plan_builder(mesh, joint_parent, joints, root_loop, **kwargs):
            calls.append(('plan', mesh, joint_parent, list(joints), list(root_loop), kwargs))
            return plan

        def transfer_applier(skin_cluster, value, normalize=True):
            calls.append(('transfer', skin_cluster, value, normalize))
            return ['transfer-result']

        def smoothing_builder(value):
            calls.append(('smooth-plan', value))
            return smoothing_plan

        def smoothing_applier(skin_cluster, value, normalize=True):
            calls.append(('smooth-apply', skin_cluster, value, normalize))
            return ['smooth-result']

        result = run_skirt_parent_workflow('mesh', 'skin', 'parent', ['j1', 'j2'], ['mesh.e[1]'], plan_builder=plan_builder, transfer_applier=transfer_applier, smoothing_builder=smoothing_builder, smoothing_applier=smoothing_applier, normalize=False, radius_scale=0.5)
        self.assertEqual([item[0] for item in calls], ['plan', 'transfer', 'smooth-plan', 'smooth-apply'])
        self.assertIs(result['plan'], plan)
        self.assertEqual(result['transfers'], ['transfer-result'])
        self.assertIs(result['smoothing_plan'], smoothing_plan)
        self.assertEqual(result['smoothing'], ['smooth-result'])
        self.assertEqual(calls[0][-1], {'radius_scale': 0.5})
        self.assertFalse(calls[1][-1])
        self.assertFalse(calls[3][-1])

    def test_rejects_missing_mesh(self):
        with self.assertRaises(ValueError):
            run_skirt_parent_workflow('', 'skin', 'parent', ['j1', 'j2'], ['mesh.e[1]'])

    def test_rejects_missing_skin_cluster(self):
        with self.assertRaises(ValueError):
            run_skirt_parent_workflow('mesh', '', 'parent', ['j1', 'j2'], ['mesh.e[1]'])

    def test_stops_before_later_phases_when_transfer_fails(self):
        calls = []
        def plan_builder(*args, **kwargs):
            calls.append('plan')
            return {'mesh': 'mesh', 'joint_parent': 'parent', 'assignments': [], 'spans': []}
        def transfer_applier(*args, **kwargs):
            calls.append('transfer')
            raise RuntimeError('transfer failed')
        def smoothing_builder(*args, **kwargs):
            calls.append('smooth-plan')
            return {}
        with self.assertRaises(RuntimeError):
            run_skirt_parent_workflow('mesh', 'skin', 'parent', ['j1', 'j2'], ['mesh.e[1]'], plan_builder=plan_builder, transfer_applier=transfer_applier, smoothing_builder=smoothing_builder)
        self.assertEqual(calls, ['plan', 'transfer'])


if __name__ == '__main__':
    unittest.main()
