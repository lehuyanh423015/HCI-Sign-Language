"""Deterministic inventory helpers for the Master Avatar v1 release."""

from __future__ import annotations

import hashlib
import json
import struct

import bpy


CORE_NMM = (
    "NMM_BROW_RAISE_L",
    "NMM_BROW_RAISE_R",
    "NMM_EYE_BLINK_L",
    "NMM_EYE_BLINK_R",
    "NMM_LIPS_ROUND",
    "NMM_LIPS_SPREAD",
)

TECHNICAL_ACTIONS = (
    "NMM_BLINK_TEST",
    "NMM_BROW_TEST",
    "NMM_MOUTH_TEST",
    "TECH_HAND_FACE_TEST",
)

EYE_OBJECTS = (
    "NMM_Eyeball.L",
    "NMM_Iris.L",
    "NMM_Pupil.L",
    "NMM_Eyeball.R",
    "NMM_Iris.R",
    "NMM_Pupil.R",
)


def _text(digest, value):
    digest.update(str(value).encode("utf-8"))
    digest.update(b"\0")


def _vector(digest, value):
    digest.update(struct.pack("<3d", float(value[0]), float(value[1]), float(value[2])))


def _matrix(digest, matrix):
    for row in matrix:
        digest.update(struct.pack("<4d", *(float(item) for item in row)))


def hierarchy_fingerprint(armature):
    digest = hashlib.sha256()
    for bone in sorted(armature.data.bones, key=lambda item: item.name):
        _text(digest, bone.name)
        _text(digest, bone.parent.name if bone.parent else "")
        _text(digest, int(bone.use_deform))
        _vector(digest, bone.head_local)
        _vector(digest, bone.tail_local)
        _matrix(digest, bone.matrix_local)
    return digest.hexdigest().upper()


def geometry_fingerprint(mesh_objects):
    digest = hashlib.sha256()
    for obj in sorted(mesh_objects, key=lambda item: item.name):
        _text(digest, obj.name)
        _text(digest, obj.data.name)
        for vertex in obj.data.vertices:
            _vector(digest, vertex.co)
        for polygon in obj.data.polygons:
            digest.update(struct.pack("<I", len(polygon.vertices)))
            for index in polygon.vertices:
                digest.update(struct.pack("<I", int(index)))
        keys = obj.data.shape_keys
        if keys:
            for key in keys.key_blocks:
                _text(digest, key.name)
                for point in key.data:
                    _vector(digest, point.co)
    return digest.hexdigest().upper()


def binding_fingerprint(mesh_objects):
    digest = hashlib.sha256()
    for obj in sorted(mesh_objects, key=lambda item: item.name):
        _text(digest, obj.name)
        group_names = {group.index: group.name for group in obj.vertex_groups}
        for index in sorted(group_names):
            _text(digest, index)
            _text(digest, group_names[index])
        for vertex in obj.data.vertices:
            digest.update(struct.pack("<I", vertex.index))
            for group in sorted(vertex.groups, key=lambda item: item.group):
                digest.update(struct.pack("<Id", group.group, float(group.weight)))
        for modifier in obj.modifiers:
            if modifier.type == "ARMATURE":
                _text(digest, modifier.name)
                _text(digest, modifier.object.name if modifier.object else "")
    return digest.hexdigest().upper()


def transform_fingerprint(objects):
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        _text(digest, obj.name)
        _matrix(digest, obj.matrix_world)
    return digest.hexdigest().upper()


def action_fingerprint(actions):
    digest = hashlib.sha256()
    for action in sorted(actions, key=lambda item: item.name):
        _text(digest, action.name)
        _text(digest, action.frame_range[0])
        _text(digest, action.frame_range[1])
        for layer in action.layers:
            _text(digest, layer.name)
            for strip in layer.strips:
                _text(digest, strip.type)
                for bag in strip.channelbags:
                    _text(digest, bag.slot_handle)
                    for curve in bag.fcurves:
                        _text(digest, curve.data_path)
                        _text(digest, curve.array_index)
                        for point in curve.keyframe_points:
                            digest.update(struct.pack("<2d", float(point.co[0]), float(point.co[1])))
    return digest.hexdigest().upper()


def inventory():
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or body is None:
        raise RuntimeError("Human/Human.rig missing")
    meshes = sorted((obj for obj in bpy.data.objects if obj.type == "MESH"), key=lambda item: item.name)
    bound = sorted(
        (
            obj for obj in meshes
            if any(mod.type == "ARMATURE" and mod.object == armature for mod in obj.modifiers)
        ),
        key=lambda item: item.name,
    )
    keys = body.data.shape_keys.key_blocks if body.data.shape_keys else []
    key_names = [key.name for key in keys]
    return {
        "armature_object": armature.name,
        "bone_count": len(armature.data.bones),
        "deform_bone_count": sum(1 for bone in armature.data.bones if bone.use_deform),
        "hierarchy_sha256": hierarchy_fingerprint(armature),
        "mesh_count": len(meshes),
        "mesh_objects": [obj.name for obj in meshes],
        "bound_mesh_objects": [obj.name for obj in bound],
        "geometry_sha256": geometry_fingerprint(meshes),
        "binding_sha256": binding_fingerprint(meshes),
        "object_transform_sha256": transform_fingerprint([armature, *meshes]),
        "shape_keys": key_names,
        "core_nmm_targets": [name for name in CORE_NMM if name in key_names],
        "eye_objects": [name for name in EYE_OBJECTS if bpy.data.objects.get(name) is not None],
        "actions": sorted(action.name for action in bpy.data.actions),
        "technical_action_sha256": action_fingerprint(
            [bpy.data.actions[name] for name in TECHNICAL_ACTIONS if name in bpy.data.actions]
        ),
    }


def neutral_state():
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    nmm_values = {}
    if body and body.data.shape_keys:
        nmm_values = {
            name: float(body.data.shape_keys.key_blocks[name].value)
            for name in CORE_NMM
            if name in body.data.shape_keys.key_blocks
        }
    pose_non_identity = []
    if armature:
        for bone in armature.pose.bones:
            identity = [1.0, 0.0, 0.0, 0.0]
            if any(abs(float(a) - float(b)) > 1e-7 for a, b in zip(bone.rotation_quaternion, identity)):
                pose_non_identity.append(bone.name)
            if any(abs(float(value)) > 1e-7 for value in bone.location):
                pose_non_identity.append(bone.name)
            if any(abs(float(value) - 1.0) > 1e-7 for value in bone.scale):
                pose_non_identity.append(bone.name)
    assigned = []
    ids = list(bpy.data.objects)
    ids.extend(mesh.shape_keys for mesh in bpy.data.meshes if mesh.shape_keys)
    for data_block in ids:
        animation = getattr(data_block, "animation_data", None)
        if animation and (animation.action or animation.nla_tracks):
            assigned.append(getattr(data_block, "name", repr(data_block)))
    return {
        "frame_current": bpy.context.scene.frame_current,
        "fps": bpy.context.scene.render.fps,
        "frame_start": bpy.context.scene.frame_start,
        "frame_end": bpy.context.scene.frame_end,
        "nmm_values": nmm_values,
        "pose_non_identity": sorted(set(pose_non_identity)),
        "animation_assignments": sorted(assigned),
    }


def same_release_structure(before, after):
    keys = (
        "bone_count",
        "deform_bone_count",
        "hierarchy_sha256",
        "mesh_count",
        "mesh_objects",
        "bound_mesh_objects",
        "geometry_sha256",
        "binding_sha256",
        "object_transform_sha256",
        "shape_keys",
        "core_nmm_targets",
        "eye_objects",
        "actions",
        "technical_action_sha256",
    )
    return all(before[key] == after[key] for key in keys)


def write_json(path, payload):
    from pathlib import Path

    output = Path(path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
