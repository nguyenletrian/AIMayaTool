from __future__ import absolute_import

import math

import maya.cmds as cmds

from aimayatool.maya import geometry
from . import closest_face


def _near(a, b, eps=1e-5):
    return all(abs(float(x) - float(y)) <= eps for x, y in zip(a, b))


def run_closest_face_smoke():
    cmds.file(new=True, force=True)
    target = cmds.polyCube(width=2.0, height=2.0, depth=2.0, name='closestFaceTarget')[0]
    cmds.move(5.0, 2.0, -3.0, target, absolute=True, worldSpace=True)
    source = cmds.polyPlane(width=1.0, height=1.0, subdivisionsX=1, subdivisionsY=1, name='closestFaceSource')[0]
    cmds.move(7.0, 2.0, -3.0, source, absolute=True, worldSpace=True)

    component = source + '.vtx[0]'
    result = closest_face.closest_face_for_component(component, target)
    direct_point, direct_face = geometry.closest_point_and_face(target, result['source_point'])

    if result['face_index'] != direct_face:
        raise AssertionError('Adapter face index does not match geometry primitive')
    if result['face'] != '%s.f[%d]' % (target, direct_face):
        raise AssertionError('Adapter face component string is incorrect')
    if not _near(result['closest_point'], direct_point):
        raise AssertionError('Adapter closest point does not match geometry primitive')
    if direct_face < 0:
        raise AssertionError('Closest face index must be non-negative')

    source_point = result['source_point']
    distance = math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(source_point, direct_point)))
    if distance <= 0.0:
        raise AssertionError('Smoke setup did not produce a separated query point')

    selected = [component, target]
    cmds.select(selected, replace=True)
    matches = closest_face.match_from_selection()
    if len(matches) != 1 or matches[0]['face_index'] != direct_face:
        raise AssertionError('Selection adapter did not preserve closest-face result')
    if cmds.ls(selection=True, flatten=True) != selected:
        raise AssertionError('Closest-face matching must not mutate caller selection')

    marker = 'AIBRIDGE_UI_SMOKE_OK:SKINNING_CLOSEST_FACE_SMOKE_OK'
    print(marker)
    return marker
