from __future__ import absolute_import


def run_skirt_parent_transfer_smoothing_plan_production_smoke():
    import importlib
    import math
    import maya.api.OpenMaya as om
    import maya.cmds as cmds
    from aimayatool.tools.skinning import skirt_parent, skirt_parent_transfer, skirt_parent_smoothing
    importlib.reload(skirt_parent)
    importlib.reload(skirt_parent_transfer)
    importlib.reload(skirt_parent_smoothing)

    cmds.file(new=True, force=True)
    mesh = cmds.polyCylinder(name='AIMayaToolSkirtProductionSmoothingMesh', radius=2.0, height=3.0, subdivisionsX=8, subdivisionsY=2, subdivisionsZ=1)[0]
    selection = om.MSelectionList()
    selection.add(mesh)
    mesh_fn = om.MFnMesh(selection.getDagPath(0))
    points = mesh_fn.getPoints(om.MSpace.kWorld)
    max_y = max(point.y for point in points)
    max_radius = max(math.sqrt(point.x * point.x + point.z * point.z) for point in points if abs(point.y - max_y) < 1e-5)
    root_loop = []
    for edge_id in range(mesh_fn.numEdges):
        v0, v1 = mesh_fn.getEdgeVertices(edge_id)
        radius0 = math.sqrt(points[v0].x * points[v0].x + points[v0].z * points[v0].z)
        radius1 = math.sqrt(points[v1].x * points[v1].x + points[v1].z * points[v1].z)
        if (abs(points[v0].y - max_y) < 1e-5 and abs(points[v1].y - max_y) < 1e-5 and
                abs(radius0 - max_radius) < 1e-5 and abs(radius1 - max_radius) < 1e-5):
            root_loop.append('%s.e[%d]' % (mesh, edge_id))
    if len(root_loop) != 8:
        raise RuntimeError('Expected 8 top-ring circumference edges, got %d' % len(root_loop))

    parent = cmds.createNode('joint', name='AIMayaToolSkirtProductionSmoothingParent')
    cmds.xform(parent, worldSpace=True, translation=(0.0, max_y, 0.0))
    joints = []
    for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        joint = cmds.createNode('joint', name='AIMayaToolSkirtProductionSmoothingJoint%d' % index)
        cmds.xform(joint, worldSpace=True, translation=(math.cos(angle) * 2.0, max_y, math.sin(angle) * 2.0))
        joints.append(joint)

    skin_cluster = cmds.skinCluster([parent] + joints, mesh, toSelectedBones=True, normalizeWeights=1, maximumInfluences=5)[0]
    all_vertices = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    cmds.skinPercent(skin_cluster, all_vertices, transformValue=[(parent, 1.0)] + [(joint, 0.0) for joint in joints], normalize=True)

    def loop_selector(node, **kwargs):
        pair = kwargs.get('edgeRingPath') or kwargs.get('edgeLoopPath')
        if pair is not None:
            return cmds.polySelect(node, edgeLoopPath=pair, noSelection=True)
        return cmds.polySelect(node, **kwargs)

    plan = skirt_parent.build_skirt_parent_plan(mesh, parent, joints, root_loop, mesh_fn=mesh_fn, selector=loop_selector)
    transfers = skirt_parent_transfer.apply_parent_transfers(skin_cluster, plan, normalize=True)
    if len(transfers) != 4 or not any(item['changed'] for item in transfers):
        raise RuntimeError('Expected four transfer results with at least one changed component')

    # Match run_skirt_parent_workflow exactly: no cached mesh_fn or selector is forwarded here.
    smoothing_plan = skirt_parent_smoothing.build_smoothing_plan(plan)
    operations = smoothing_plan['operations']
    if len(operations) != 4:
        raise RuntimeError('Expected four smoothing operations after transfer')
    if not all(item['root_vertices'] for item in operations):
        raise RuntimeError('Expected non-empty root vertices after transfer')
    if not all(item['strips'] for item in operations):
        raise RuntimeError('Expected non-empty strips after transfer')
    return 'SKINNING_SKIRT_PARENT_TRANSFER_SMOOTHING_PLAN_PRODUCTION_SMOKE_OK'
