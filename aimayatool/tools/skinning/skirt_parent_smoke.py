from __future__ import absolute_import


def run_skirt_parent_smoke():
    import importlib
    import math
    import maya.api.OpenMaya as om
    import maya.cmds as cmds
    from aimayatool.tools.skinning import skirt_parent
    importlib.reload(skirt_parent)

    cmds.file(new=True, force=True)
    mesh = cmds.polyCylinder(name='AIMayaToolSkirtPlanMesh', radius=2.0, height=4.0, subdivisionsX=16, subdivisionsY=3, subdivisionsZ=1)[0]
    selection = om.MSelectionList()
    selection.add(mesh)
    mesh_fn = om.MFnMesh(selection.getDagPath(0))
    points = mesh_fn.getPoints(om.MSpace.kWorld)
    max_y = max(point.y for point in points)
    root_loop = []
    for edge_id in range(mesh_fn.numEdges):
        v0, v1 = mesh_fn.getEdgeVertices(edge_id)
        if abs(points[v0].y - max_y) < 1e-5 and abs(points[v1].y - max_y) < 1e-5:
            root_loop.append('%s.e[%d]' % (mesh, edge_id))
    if len(root_loop) != 16:
        raise RuntimeError('Expected 16 top-ring edges, got %d' % len(root_loop))

    parent = cmds.createNode('joint', name='AIMayaToolSkirtParent')
    cmds.xform(parent, worldSpace=True, translation=(0.0, max_y, 0.0))
    joints = []
    for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        joint = cmds.createNode('joint', name='AIMayaToolSkirtJoint%d' % index)
        cmds.xform(joint, worldSpace=True, translation=(math.cos(angle) * 2.0, max_y, math.sin(angle) * 2.0))
        joints.append(joint)

    def loop_selector(node, **kwargs):
        pair = kwargs.get('edgeRingPath') or kwargs.get('edgeLoopPath')
        if pair is not None:
            return cmds.polySelect(node, edgeLoopPath=pair, noSelection=True)
        return cmds.polySelect(node, **kwargs)

    plan = skirt_parent.build_skirt_parent_plan(mesh, parent, joints, root_loop, mesh_fn=mesh_fn, selector=loop_selector)
    if not plan['closed']:
        raise RuntimeError('Expected closed skirt root loop')
    if len(plan['joints']) != 4 or len(plan['assignments']) != 4 or len(plan['spans']) != 4:
        raise RuntimeError('Unexpected composed skirt plan counts')
    if not all(item['root_vertices'] for item in plan['assignments']):
        raise RuntimeError('Expected each joint to own root-loop vertices')
    if not all(item['strips'] for item in plan['assignments']):
        raise RuntimeError('Expected perpendicular strip groups for each joint region')
    if not all(item['edges'] and item['vertices'] for item in plan['spans']):
        raise RuntimeError('Expected non-empty smoothing spans')
    return 'SKINNING_SKIRT_PARENT_PLAN_SMOKE_OK'
