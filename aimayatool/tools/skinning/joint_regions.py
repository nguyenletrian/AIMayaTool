from __future__ import absolute_import

import math


def _cmds():
    import maya.cmds as cmds
    return cmds


def circular_order(items, positions, clockwise=False):
    """Sort item names around their centroid using a stable geometric frame."""
    items = list(items or [])
    if len(items) < 3:
        return items[:]
    pts = {item: tuple(float(v) for v in positions[item]) for item in items}
    center = tuple(sum(pts[item][axis] for item in items) / float(len(items)) for axis in range(3))
    best_pair = None
    best_dist = -1.0
    for index, item_a in enumerate(items):
        for item_b in items[index + 1:]:
            delta = tuple(pts[item_a][axis] - pts[item_b][axis] for axis in range(3))
            dist = sum(value * value for value in delta)
            if dist > best_dist:
                best_dist, best_pair = dist, (item_a, item_b)
    def normalize(vector):
        length = math.sqrt(sum(value * value for value in vector))
        return tuple(value / length for value in vector) if length > 1e-12 else None
    x_axis = normalize(tuple(pts[best_pair[0]][axis] - pts[best_pair[1]][axis] for axis in range(3)))
    vectors = [tuple(pts[item][axis] - center[axis] for axis in range(3)) for item in items]
    normal = [0.0, 0.0, 0.0]
    for index, a in enumerate(vectors):
        for b in vectors[index + 1:]:
            cross = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
            for axis in range(3):
                normal[axis] += cross[axis]
    normal = normalize(normal)
    if x_axis is None or normal is None:
        return items[:]
    y_axis = normalize((normal[1] * x_axis[2] - normal[2] * x_axis[1], normal[2] * x_axis[0] - normal[0] * x_axis[2], normal[0] * x_axis[1] - normal[1] * x_axis[0]))
    if y_axis is None:
        return items[:]
    result = []
    for item in items:
        vector = tuple(pts[item][axis] - center[axis] for axis in range(3))
        x = sum(vector[axis] * x_axis[axis] for axis in range(3))
        y = sum(vector[axis] * y_axis[axis] for axis in range(3))
        result.append((math.atan2(y, x), item))
    result.sort(key=lambda value: value[0], reverse=clockwise)
    return [item for _, item in result]


def closest_items(target, positions, count=1):
    """Return up to count nearest item names and distances, excluding target itself."""
    target_pos = positions[target]
    result = []
    for item, point in positions.items():
        if item == target:
            continue
        distance = math.sqrt(sum((float(point[axis]) - float(target_pos[axis])) ** 2 for axis in range(3)))
        result.append((item, distance))
    result.sort(key=lambda value: value[1])
    return result[:max(0, int(count))]


def indices_within_radius(points, center, radius):
    """Return point indices within an inclusive Euclidean radius."""
    radius_sq = float(radius) * float(radius)
    center = tuple(float(v) for v in center)
    return [index for index, point in enumerate(points) if sum((float(point[axis]) - center[axis]) ** 2 for axis in range(3)) <= radius_sq]


def joint_positions(joints):
    cmds = _cmds()
    return {joint: tuple(cmds.xform(joint, query=True, worldSpace=True, translation=True)) for joint in joints}


def sort_circular_joints(joints, clockwise=False):
    return circular_order(joints, joint_positions(joints), clockwise=clockwise)


def closest_joints(target_joint, joints, count=1):
    positions = joint_positions(joints)
    return closest_items(target_joint, positions, count=count)
