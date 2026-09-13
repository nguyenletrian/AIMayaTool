from __future__ import absolute_import


def run_skirt_parent_interactive_smoke():
    import importlib
    import math
    import maya.api.OpenMaya as om
    import maya.cmds as cmds
    from aimayatool.tools.skinning import ratio_weights, skirt_parent_smoothing_apply, skirt_parent_workflow, skirt_parent_interactive
    importlib.reload(ratio_weights)
    importlib.reload(skirt_parent_smoothing_apply)
    importlib.reload(skirt_parent_workflow)
    importlib.reload(skirt_parent_interactive)

    cmds.file(new=True, force=True)
    mesh = cmds.polyCylinder(name='AIMayaToolSkirtInteractiveMesh', radius=2.0, height=3.0, subdivisionsX=8, subdivisionsY=2, subdivisionsZ=1)[0]
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
        raise RuntimeError('Expected 8 root-loop edges, got %d' % len(root_loop))

    parent = cmds.createNode('joint', name='AIMayaToolSkirtInteractiveParent')
    cmds.xform(parent, worldSpace=True, translation=(0.0, max_y, 0.0))
    joints = []
    for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        joint = cmds.createNode('joint', name='AIMayaToolSkirtInteractiveJoint%d' % index)
        cmds.xform(joint, worldSpace=True, translation=(math.cos(angle) * 2.0, max_y, math.sin(angle) * 2.0))
        joints.append(joint)

    skin_cluster = cmds.skinCluster([parent] + joints, mesh, toSelectedBones=True, normalizeWeights=1, maximumInfluences=5)[0]
    all_vertices = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    cmds.skinPercent(skin_cluster, all_vertices, transformValue=[(parent, 1.0)] + [(joint, 0.0) for joint in joints], normalize=True)

    explicit_selection = [parent] + joints + root_loop
    context = skirt_parent_interactive.context_from_selection(explicit_selection)
    if context['joint_parent'] != parent or context['joints'] != joints or context['root_loop'] != root_loop:
        raise RuntimeError('Interactive selection context did not preserve parent/joints/root loop contract')
    result = skirt_parent_interactive.run_from_selection(explicit_selection)
    if len(result['transfers']) != 4 or len(result['smoothing']) != 4:
        raise RuntimeError('Expected four transfer and smoothing results')
    if not any(item['propagated'] for item in result['smoothing']):
        raise RuntimeError('Expected ratio propagation from interactive workflow')
    return 'AIBRIDGE_UI_SMOKE_OK:SKINNING_SKIRT_PARENT_INTERACTIVE_SMOKE_OK'
