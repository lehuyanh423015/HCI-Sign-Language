"""Read-only Blender/MPFB/rig inventory for TASK-0002 preparation.

Run only on a copy/working file. This script never calls save or mutates scene data.
"""

import json
import bpy


def addon_names():
    return sorted(module.__name__ for module in bpy.context.preferences.addons)


def armature_summary(obj):
    bones = obj.data.bones
    bone_rows = [
        {
            "name": bone.name,
            "parent": bone.parent.name if bone.parent else None,
            "use_deform": bone.use_deform,
        }
        for bone in bones
    ]
    finger_tokens = ("thumb", "index", "middle", "ring", "pinky", "finger")
    finger_candidates = sorted(
        bone.name for bone in bones if any(token in bone.name.lower() for token in finger_tokens)
    )
    meshes = []
    for mesh in bpy.data.objects:
        if mesh.type != "MESH":
            continue
        modifiers = [
            modifier.object.name
            for modifier in mesh.modifiers
            if modifier.type == "ARMATURE" and modifier.object
        ]
        if obj.name in modifiers or mesh.parent == obj:
            meshes.append(mesh.name)
    return {
        "name": obj.name,
        "bone_count": len(bones),
        "bones": bone_rows,
        "finger_control_candidates": finger_candidates,
        "related_meshes": sorted(meshes),
    }


report = {
    "status": "READ_ONLY",
    "blender_version": bpy.app.version_string,
    "file": bpy.data.filepath or None,
    "mpfb_candidates": [name for name in addon_names() if "mpfb" in name.lower()],
    "armatures": [armature_summary(obj) for obj in bpy.data.objects if obj.type == "ARMATURE"],
    "actions": sorted(action.name for action in bpy.data.actions),
}

print("HCI_PREFLIGHT_JSON_BEGIN")
print(json.dumps(report, ensure_ascii=False, indent=2))
print("HCI_PREFLIGHT_JSON_END")
