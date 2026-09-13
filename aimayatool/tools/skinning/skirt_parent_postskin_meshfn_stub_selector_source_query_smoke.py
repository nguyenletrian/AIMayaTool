from __future__ import absolute_import


def run_skirt_parent_postskin_meshfn_stub_selector_source_query_smoke():
    import importlib
    import math
    import maya.api.OpenMaya as om
    import maya.cmds as cmds
    from aimayatool.tools.skinning import skirt_parent
    importlib.reload(skirt_parent)

    cmds.file(new=True, force=True)
    mesh = cmds.polyCylinder(name='AIMayaToolSkirtPostSkinMeshFnMesh', radius=2.0, height=3.0, subdivisionsX=8, subdivisionsY=2, subdivisionsZ=1)[0]

    pre_selection = om.MSelectionList(); pre_selection.add(mesh)
    pre_mesh_fn = om.MFnMesh(pre_selection.getDagPath(0))
    points = pre_mesh_fn.getPoints(om.MSpace.kWorld)
    max_y = max(point.y for point in points)
    max_radius = max(math.sqrt(point.x * point.x + point.z * point.z) for point in points if abs(point.y - max_y) < 1e-5)
    root_loop = []
    for edge_id in range(pre_mesh_fn.numEdges):
        v0, v1 = pre_mesh_fn.getEdgeVertices(edge_id)
        r0 = math.sqrt(points[v0].x * points[v0].x + points[v0].z * points[v0].z)
        r1 = math.sqrt(points[v1].x * points[v1].x + points[v1].z * points[v1].z)
        if abs(points[v0].y - max_y) < 1e-5 and abs(points[v1].y - max_y) < 1e-5 and abs(r0 - max_radius) < 1e-5 and abs(r1 - max_radius) < 1e-5:
            root_loop.append('%s.e[%d]' % (mesh, edge_id))
    if len(root_loop) != 8:
        raise RuntimeError('Expected 8 top-ring circumference edges, got %d' % len(root_loop))

    parent = cmds.createNode('joint', name='AIMayaToolSkirtPostSkinMeshFnParent')
    cmds.xform(parent, worldSpace=True, translation=(0.0, max_y, 0.0))
    joints = []
    for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        joint = cmds.createNode('joint', name='AIMayaToolSkirtPostSkinMeshFnJoint%d' % index)
        cmds.xform(joint, worldSpace=True, translation=(math.cos(angle) * 2.0, max_y, math.sin(angle) * 2.0))
        joints.append(joint)

    skin_cluster = cmds.skinCluster([parent] + joints, mesh, toSelectedBones=True, normalizeWeights=1, maximumInfluences=5)[0]
    all_vertices = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    cmds.skinPercent(skin_cluster, all_vertices, transformValue=[(parent, 1.0)] + [(joint, 0.0) for joint in joints], normalize=True)

    post_selection = om.MSelectionList(); post_selection.add(mesh)
    post_mesh_fn = om.MFnMesh(post_selection.getDagPath(0))
    if post_mesh_fn.numVertices <= 0:
        raise RuntimeError('Expected fresh post-skin MFnMesh to expose vertices')

    def selector_stub(node, **kwargs):
        pair = kwargs.get('edgeRingPath') or kwargs.get('edgeLoopPath')
        return list(pair) if pair is not None else []

    def group_builder_stub(node, vertices, **kwargs):
        vertices = list(vertices or [])
        return {'stub': vertices} if vertices else {}

    plan = skirt_parent.build_skirt_parent_plan(mesh, parent, joints, root_loop, mesh_fn=post_mesh_fn, selector=selector_stub, group_builder=group_builder_stub)
    assignments = list(plan.get('assignments') or [])
    if not assignments:
        raise RuntimeError('Expected at least one assignment')
    components = []
    for strip in (assignments[0].get('strips') or {}).values():
        components.extend(strip or [])
    if not components:
        raise RuntimeError('Expected at least one first-assignment component')

    source_weight = cmds.skinPercent(skin_cluster, components[0], query=True, transform=parent)
    if source_weight < 0.0:
        raise RuntimeError('Unexpected negative source weight')
    if not cmds.objExists(mesh):
        raise RuntimeError('Expected mesh to exist after fresh post-skin mesh_fn planner query')
    return 'SKINNING_SKIRT_PARENT_POSTSKIN_MESHFN_STUB_SELECTOR_SOURCE_QUERY_SMOKE_OK'
