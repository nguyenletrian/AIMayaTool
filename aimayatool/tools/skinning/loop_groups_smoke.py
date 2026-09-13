from __future__ import absolute_import


def run_loop_groups_smoke():
    import importlib
    import maya.cmds as cmds
    from aimayatool.tools.skinning import loop_groups
    importlib.reload(loop_groups)
    cmds.file(new=True, force=True)
    mesh = cmds.polyPlane(name='AIMayaToolLoopGroupsMesh', width=2.0, height=2.0, subdivisionsX=2, subdivisionsY=2)[0]
    root_vertices = ['%s.vtx[%d]' % (mesh, index) for index in (0, 1, 2)]
    groups = loop_groups.group_vertices_by_perpendicular_loops(mesh, root_vertices)
    if not groups:
        raise RuntimeError('Expected perpendicular loop groups')
    for vertex, strip in groups.items():
        if vertex not in root_vertices or not strip:
            raise RuntimeError('Unexpected grouped strip')
        if not all(component.startswith(mesh + '.vtx[') for component in strip):
            raise RuntimeError('Unexpected vertex component')
    return 'SKINNING_LOOP_GROUPS_SMOKE_OK'
