from __future__ import absolute_import

def greedy_assign(joints, component_count, distances):
    joints = [str(j).strip() for j in joints if str(j).strip()]
    if len(set(joints)) != len(joints):
        raise ValueError("Joint names must be unique.")
    component_count = int(component_count)
    if component_count < 0:
        raise ValueError("component_count must be non-negative.")
    candidates = []
    for joint_order, joint in enumerate(joints):
        for component_index in range(component_count):
            key = (joint, component_index)
            if key not in distances:
                raise ValueError("Missing distance for {0} -> component {1}".format(joint, component_index))
            distance = float(distances[key])
            if distance < 0:
                raise ValueError("Distances must be non-negative.")
            candidates.append((distance, joint_order, component_index, joint))
    candidates.sort(key=lambda x: (x[0], x[1], x[2]))
    assigned_joints, assigned_components, result = set(), set(), []
    for distance, _, component_index, joint in candidates:
        if joint in assigned_joints or component_index in assigned_components:
            continue
        assigned_joints.add(joint); assigned_components.add(component_index)
        result.append({"joint":joint,"component_index":component_index,"distance":distance})
        if len(assigned_joints) == len(joints) or len(assigned_components) == component_count:
            break
    return result
