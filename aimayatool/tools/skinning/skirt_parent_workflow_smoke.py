from __future__ import absolute_import


def run_skirt_parent_workflow_smoke():
    import importlib
    import math
    import maya.api.OpenMaya as om
    import maya.cmds as cmds
    from aimayatool.tools.skinning import skirt_parent_workflow
    importlib.reload(skirt_parent_workflow)

    cmds.file(new=True, force=True)
    mesh = cmds.polyCylinder(name='AIMayaToolSkirtWorkflowMesh', radius=2.0, height=3.0, subdivisionsX=8, subdivisionsY=2, subdivisionsZ=1)[0]
    selection = om.MSelectionList()
    selection.add(mesh)
    preskin_mesh_fn = om.MFnMesh(selection.getDagPath(0))
    points = preskin_mesh_fn.getPoints(om.MSpace.kWorld)
    max_y = max(point.y for point in points)
    max_radius = max(math.sqrt(point.x * point.x + point.z * point.z) for point in points if abs(point.y - max_y) < 1e-5)
    root_loop = []
    for edge_id in range(preskin_mesh_fn.numEdges):
        v0, v1 = preskin_mesh_fn.getEdgeVertices(edge_id)
        radius0 = math.sqrt(points[v0].x * points[v0].x + points[v0].z * points[v0].z)
        radius1 = math.sqrt(points[v1].x * points[v1].x + points[v1].z * points[v1].z)
        if (abs(points[v0].y - max_y) < 1e-5 and abs(points[v1].y - max_y) < 1e-5 and
                abs(radius0 - max_radius) < 1e-5 and abs(radius1 - max_radius) < 1e-5):
            root_loop.append('%s.e[%d]' % (mesh, edge_id))
    if len(root_loop) != 8:
        raise RuntimeError('Expected 8 top-ring circumference edges, got %d' % len(root_loop))

    parent = cmds.createNode('joint', name='AIMayaToolSkirtWorkflowParent')
    cmds.xform(parent, worldSpace=True, translation=(0.0, max_y, 0.0))
    joints = []
    for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        joint = cmds.createNode('joint', name='AIMayaToolSkirtWorkflowJoint%d' % index)
        cmds.xform(joint, worldSpace=True, translation=(math.cos(angle) * 2.0, max_y, math.sin(angle) * 2.0))
        joints.append(joint)

    skin_cluster = cmds.skinCluster([parent] + joints, mesh, toSelectedBones=True, normalizeWeights=1, maximumInfluences=5)[0]
    all_vertices = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    cmds.skinPercent(
        skin_cluster,
        all_vertices,
        transformValue=[(parent, 1.0)] + [(joint, 0.0) for joint in joints],
        normalize=True,
    )

    postskin_selection = om.MSelectionList()
    postskin_selection.add(mesh)
    postskin_mesh_fn = om.MFnMesh(postskin_selection.getDagPath(0))

    def loop_selector(node, **kwargs):
        pair = kwargs.get('edgeRingPath') or kwargs.get('edgeLoopPath')
        if pair is not None:
            return cmds.polySelect(node, edgeLoopPath=pair, noSelection=True)
        return cmds.polySelect(node, **kwargs)

    result = skirt_parent_workflow.run_skirt_parent_workflow(
        mesh,
        skin_cluster,
        parent,
        joints,
        root_loop,
        mesh_fn=postskin_mesh_fn,
        selector=loop_selector,
    )
    plan = result['plan']
    transfers = result['transfers']
    smoothing_plan = result['smoothing_plan']
    smoothing = result['smoothing']
    if not plan['closed'] or len(plan['assignments']) != 4 or len(plan['spans']) != 4:
        raise RuntimeError('Unexpected workflow plan output')
    if len(transfers) != 4 or not any(item['changed'] for item in transfers):
        raise RuntimeError('Expected parent-transfer mutations')
    if len(smoothing_plan['operations']) != 4 or len(smoothing) != 4:
        raise RuntimeError('Expected four smoothing operations')
    changed_components = [component for item in transfers for component in item['changed']]
    if not changed_components:
        raise RuntimeError('Expected changed transfer components')
    sample = changed_components[0]
    parent_weight = cmds.skinPercent(skin_cluster, sample, query=True, transform=parent)
    child_total = sum(cmds.skinPercent(skin_cluster, sample, query=True, transform=joint) for joint in joints)
    if parent_weight > 1e-5 or child_total < 0.999:
        raise RuntimeError('Expected parent weight transferred into skirt joints')
    if not any(item['propagated'] for item in smoothing):
        raise RuntimeError('Expected smoothing ratio propagation')
    return 'SKINNING_SKIRT_PARENT_WORKFLOW_SMOKE_OK'
