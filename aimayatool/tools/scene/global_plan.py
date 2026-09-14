from __future__ import absolute_import

from .pattern_descriptor import normalize_global_pattern_descriptor


def build_global_pattern_plan(descriptor):
    """Build an explicit, host-independent operation plan for legacy Global pattern data."""
    data = normalize_global_pattern_descriptor(descriptor)
    operations = []
    for child in data["children"]:
        operations.append({
            "operation": "global_parent_blend",
            "child": child,
            "parent": data["parent"],
            "attr_name": data["attr_name"],
            "default_value": data["default_value"],
            "maintain_offset": data["maintain_offset"],
        })
    return tuple(operations)
