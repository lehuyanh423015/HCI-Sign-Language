"""Reusable data-driven pose helpers for the released MPFB Master Avatar v1.

The module operates on actual MPFB bone names and discovers finger flex axes by
probing each bone in its local coordinate system. Pose names in JSON are
technical rig controls and carry no linguistic meaning.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

from master_v1_utils import CORE_NMM, inventory


EXPECTED_HIERARCHY_SHA256 = "0A14E14E5899D4697732D0B0E3F6AC1D6531979B87A7CD23E2652865D9DC2F89"
FINGER_FAMILIES = {
    "thumb": "finger1",
    "index": "finger2",
    "middle": "finger3",
    "ring": "finger4",
    "little": "finger5",
}
SIDES = ("L", "R")


class PoseAuthoringError(RuntimeError):
    pass


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_pose_library(path):
    payload = load_json(path)
    if payload.get("schema_version") != 1 or not isinstance(payload.get("poses"), dict):
        raise PoseAuthoringError("Unsupported or invalid pose library")
    return payload


def require_armature():
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or armature.type != "ARMATURE":
        raise PoseAuthoringError("Human.rig armature is missing")
    if body is None or body.type != "MESH" or body.data.shape_keys is None:
        raise PoseAuthoringError("Human mesh or Shape Keys are missing")
    return armature, body


def validate_canonical_rig():
    current = inventory()
    failures = []
    if current["bone_count"] != 137:
        failures.append("bone_count")
    if current["hierarchy_sha256"] != EXPECTED_HIERARCHY_SHA256:
        failures.append("hierarchy")
    if set(current["core_nmm_targets"]) != set(CORE_NMM):
        failures.append("core_nmm_targets")
    if failures:
        raise PoseAuthoringError("Canonical rig validation failed: %s" % ", ".join(failures))
    return current


def finger_chains(side):
    if side not in SIDES:
        raise PoseAuthoringError("Unsupported side: %s" % side)
    return {
        semantic: ["%s-%d.%s" % (family, segment, side) for segment in range(1, 4)]
        for semantic, family in FINGER_FAMILIES.items()
    }


def all_hand_bones(side):
    chains = finger_chains(side)
    return [name for chain in chains.values() for name in chain]


def semantic_finger_name(name, side):
    suffix = ".%s" % side
    return name if name.endswith(suffix) else name + suffix


def require_pose_bone(armature, name):
    bone = armature.pose.bones.get(name)
    if bone is None:
        raise PoseAuthoringError("Invalid bone name: %s" % name)
    return bone


def reset_bone(armature, name):
    require_pose_bone(armature, name).matrix_basis.identity()


def reset_hand(armature, side, include_wrist=True):
    for name in all_hand_bones(side):
        reset_bone(armature, name)
    if include_wrist:
        reset_bone(armature, "wrist.%s" % side)
    bpy.context.view_layer.update()


def reset_full_pose(armature, body=None):
    for bone in armature.pose.bones:
        bone.matrix_basis.identity()
    if body and body.data.shape_keys:
        for name in CORE_NMM:
            if name in body.data.shape_keys.key_blocks:
                body.data.shape_keys.key_blocks[name].value = 0.0
    bpy.context.view_layer.update()


def _palm_center(armature, side):
    names = ["wrist.%s" % side]
    names.extend("metacarpal%d.%s" % (index, side) for index in range(1, 5))
    points = [armature.matrix_world @ require_pose_bone(armature, name).head for name in names]
    return sum(points, Vector()) / len(points)


def _chain_tip(armature, chain):
    return armature.matrix_world @ require_pose_bone(armature, chain[-1]).tail


def discover_flex_axis(armature, bone_name, chain, side, probe_degrees=12.0):
    """Choose the local Euler axis/sign that moves the chain tip toward its palm."""
    pose_bone = require_pose_bone(armature, bone_name)
    original_mode = pose_bone.rotation_mode
    original_basis = pose_bone.matrix_basis.copy()
    center = _palm_center(armature, side)
    probe = math.radians(probe_degrees)
    candidates = []
    try:
        for axis_index in range(3):
            for sign in (-1, 1):
                pose_bone.matrix_basis.identity()
                pose_bone.rotation_mode = "XYZ"
                bpy.context.view_layer.update()
                before = (_chain_tip(armature, chain) - center).length
                pose_bone.rotation_euler[axis_index] = sign * probe
                bpy.context.view_layer.update()
                after = (_chain_tip(armature, chain) - center).length
                candidates.append({
                    "axis_index": axis_index,
                    "axis": "XYZ"[axis_index],
                    "sign": sign,
                    "score": before - after,
                })
    finally:
        pose_bone.rotation_mode = original_mode
        pose_bone.matrix_basis = original_basis
        bpy.context.view_layer.update()
    best = max(candidates, key=lambda item: item["score"])
    return {**best, "probe_degrees": probe_degrees, "candidates": candidates}


class PoseAuthor:
    def __init__(self, armature, body):
        self.armature = armature
        self.body = body
        self.axis_map = {}

    def axis_for(self, bone_name, chain, side):
        if bone_name not in self.axis_map:
            self.axis_map[bone_name] = discover_flex_axis(self.armature, bone_name, chain, side)
        return self.axis_map[bone_name]

    def apply_flex(self, bone_name, chain, side, degrees):
        bone = require_pose_bone(self.armature, bone_name)
        axis = self.axis_for(bone_name, chain, side)
        bone.matrix_basis.identity()
        bone.rotation_mode = "XYZ"
        bone.rotation_euler[axis["axis_index"]] = axis["sign"] * math.radians(float(degrees))
        return axis

    def apply_named_hand_pose(self, side, pose_name, library, overrides=None):
        pose = library.get("poses", {}).get(pose_name)
        if pose is None:
            raise PoseAuthoringError("Unknown pose name: %s" % pose_name)
        if pose.get("applies_to") not in ("BOTH", side):
            raise PoseAuthoringError("Pose %s does not support side %s" % (pose_name, side))
        values = dict(pose.get("bones", {}))
        values.update(overrides or {})
        chains = finger_chains(side)
        affected = []
        for semantic, degrees in values.items():
            actual = semantic_finger_name(semantic, side)
            family = next((name for name, chain in chains.items() if actual in chain), None)
            if family is None:
                raise PoseAuthoringError("Unsupported finger pose bone: %s" % semantic)
            self.apply_flex(actual, chains[family], side, degrees)
            affected.append(actual)
        bpy.context.view_layer.update()
        return affected

    def apply_local_rotation(self, bone_name, degrees_xyz):
        if len(degrees_xyz) != 3:
            raise PoseAuthoringError("Rotation requires three degree values: %s" % bone_name)
        bone = require_pose_bone(self.armature, bone_name)
        bone.matrix_basis.identity()
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = tuple(math.radians(float(value)) for value in degrees_xyz)
        bpy.context.view_layer.update()
        return bone_name

    def apply_morphs(self, values):
        keys = self.body.data.shape_keys.key_blocks
        for name in CORE_NMM:
            if name in keys:
                keys[name].value = float(values.get(name, 0.0))
        bpy.context.view_layer.update()

    def keyframe_bones(self, names, frame):
        keyed = []
        for name in sorted(set(names)):
            bone = require_pose_bone(self.armature, name)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=name)
            keyed.append(name)
        return keyed

    def keyframe_morphs(self, frame):
        keys = self.body.data.shape_keys.key_blocks
        keyed = []
        for name in CORE_NMM:
            if name in keys:
                keys[name].keyframe_insert(data_path="value", frame=frame)
                keyed.append(name)
        return keyed

    def evaluate(self, frame, bone_names):
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        return {
            "frame": frame,
            "bones": {
                name: [round(float(value), 8) for row in require_pose_bone(self.armature, name).matrix_basis for value in row]
                for name in sorted(set(bone_names))
            },
            "morphs": {
                name: float(self.body.data.shape_keys.key_blocks[name].value)
                for name in CORE_NMM if name in self.body.data.shape_keys.key_blocks
            },
        }


def identity_matrix_values(matrix):
    identity = Matrix.Identity(4)
    return all(abs(float(matrix[row][column]) - float(identity[row][column])) <= 1e-6 for row in range(4) for column in range(4))
