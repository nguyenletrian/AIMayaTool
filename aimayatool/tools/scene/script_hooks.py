from __future__ import absolute_import
import os
from .single_script import run_script_file

HOOKS = {
    "current_after": {"scope": "current", "phase": "after", "module_name": "Scene_Pattern_CurrentAfterScript", "name": "Current AfterScript"},
    "current_post": {"scope": "current", "phase": "post", "module_name": "Scene_Pattern_CurrentPostScript", "name": "Current PostScript"},
    "up_after": {"scope": "up", "phase": "after", "module_name": "Scene_Pattern_UpAfterScript", "name": "Up AfterScript"},
    "up_post": {"scope": "up", "phase": "post", "module_name": "Scene_Pattern_UpPostScript", "name": "Up PostScript"},
}

def get_hook(key):
    if key not in HOOKS:
        raise KeyError("Unknown script hook: {0}".format(key))
    return dict(HOOKS[key])

def scene_data_path(scene_path, hook_key):
    hook = get_hook(hook_key)
    scene_dir = os.path.dirname(os.path.abspath(str(scene_path or "").strip()))
    if not scene_dir:
        raise ValueError("scene_path is required")
    if hook["scope"] == "up":
        scene_dir = os.path.dirname(scene_dir)
    return os.path.join(scene_dir, "SceneData", hook["module_name"] + ".py")

def run_hook(script_path, globals_dict=None):
    return run_script_file(script_path, globals_dict=globals_dict)
