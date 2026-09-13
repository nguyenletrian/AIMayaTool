from __future__ import absolute_import


def run_skirt_parent_preplan_source_query_smoke():
    import math
    import maya.api.OpenMaya as om
    import maya.cmds as cmds

    cmds.file(new=True, force=True)
    mesh = cmds.polyCylinder(name='AIMayaToolSkirtPrePlanSourceQueryMesh', radius=2.0, height=3.0, subdivisionsX=8, subdivisionsY=2, subdivisionsZ=1)[0]
    selection = om.MSelectionList(); selection.add(mesh)
    mesh_fn = om.MFnMesh(selection.getDagPath(0))
    points = mesh_fn.getPoints(om.MSpace.kWorld)
    max_y = max(point.y for point in points)

    parent = cmds.createNode('joint', name='AIMayaToolSkirtPrePlanSourceQueryParent')
    cmds.xform(parent, worldSpace=True, translation=(0.0, max_y, 0.0))
    joints = []
    for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        joint = cmds.createNode('joint', name='AIMayaToolSkirtPrePlanSourceQueryJoint%d' % index)
        cmds.xform(joint, worldSpace=True, translation=(math.cos(angle) * 2.0, max_y, math.sin(angle) * 2.0))
        joints.append(joint)

    skin_cluster = cmds.skinCluster([parent] + joints, mesh, toSelectedBones=True, normalizeWeights=1, maximumInfluences=5)[0]
    all_vertices = cmds.ls(mesh + '.vtx[*]', flatten=True) or []
    cmds.skinPercent(skin_cluster, all_vertices, transformValue=[(parent, 1.0)] + [(joint, 0.0) for joint in joints], normalize=True)
    if not all_vertices:
        raise RuntimeError('Expected skinned vertices')

    source_weight = cmds.skinPercent(skin_cluster, all_vertices[0], query=True, transform=parent)
    if source_weight < 0.0:
        raise RuntimeError('Unexpected negative source weight')
    if not cmds.objExists(mesh):
        raise RuntimeError('Expected mesh to exist after pre-plan source query')
    return 'SKINNING_SKIRT_PARENT_PREPLAN_SOURCE_QUERY_SMOKE_OK'
