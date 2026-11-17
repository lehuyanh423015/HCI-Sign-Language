"""Shared Blender 5.2 helpers for the technical hand-control fixture."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


FINGER_CHAINS = {
    "thumb": ["finger1-1.R", "finger1-2.R", "finger1-3.R"],
    "index": ["finger2-1.R", "finger2-2.R", "finger2-3.R"],
    "middle": ["finger3-1.R", "finger3-2.R", "finger3-3.R"],
    "ring": ["finger4-1.R", "finger4-2.R", "finger4-3.R"],
    "little": ["finger5-1.R", "finger5-2.R", "finger5-3.R"],
}
TECHNICAL_BONES = [name for chain in FINGER_CHAINS.values() for name in chain]


def sha256(file_path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(file_path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def require_rig() -> tuple[bpy.types.Object, bpy.types.Object]:
    armature = bpy.data.objects.get("Human.rig")
    mesh = bpy.data.objects.get("Human")
    if armature is None or armature.type != "ARMATURE":
        raise RuntimeError("Required armature Human.rig was not found")
    if mesh is None or mesh.type != "MESH":
        raise RuntimeError("Required mesh Human was not found")
    missing = [name for name in TECHNICAL_BONES + ["wrist.R", "lowerarm01.R", "root"] if name not in armature.pose.bones]
    if missing:
        raise RuntimeError("Required pose bones are missing: %s" % ", ".join(missing))
    return armature, mesh


def matrix_signature(matrix: Matrix, precision: int = 10) -> tuple[float, ...]:
    return tuple(round(value, precision) for row in matrix for value in row)


def pose_basis_snapshot(armature: bpy.types.Object) -> dict[str, tuple[float, ...]]:
    return {bone.name: matrix_signature(bone.matrix_basis) for bone in armature.pose.bones}


def object_transform_snapshot(armature: bpy.types.Object, mesh: bpy.types.Object) -> dict:
    return {
        armature.name: matrix_signature(armature.matrix_world),
        mesh.name: matrix_signature(mesh.matrix_world),
        "root_basis": matrix_signature(armature.pose.bones["root"].matrix_basis),
    }


def establish_neutral_pose(armature: bpy.types.Object) -> None:
    for pose_bone in armature.pose.bones:
        pose_bone.matrix_basis.identity()
    bpy.context.view_layer.update()


def evaluated_mesh_vertices(mesh: bpy.types.Object) -> list[Vector]:
    dependency_graph = bpy.context.evaluated_depsgraph_get()
    evaluated_object = mesh.evaluated_get(dependency_graph)
    evaluated_mesh = evaluated_object.to_mesh()
    try:
        return [evaluated_object.matrix_world @ vertex.co for vertex in evaluated_mesh.vertices]
    finally:
        evaluated_object.to_mesh_clear()


def mesh_delta(before: list[Vector], after: list[Vector], tolerance: float = 1e-6) -> dict:
    distances = [(right - left).length for left, right in zip(before, after)]
    moved = [distance for distance in distances if distance > tolerance]
    return {
        "moved_vertices": len(moved),
        "max_distance": max(distances, default=0.0),
        "mean_moved_distance": sum(moved) / len(moved) if moved else 0.0,
    }


def palm_center(armature: bpy.types.Object) -> Vector:
    names = ["wrist.R", "metacarpal1.R", "metacarpal2.R", "metacarpal3.R", "metacarpal4.R"]
    points = [armature.matrix_world @ armature.pose.bones[name].head for name in names]
    return sum(points, Vector()) / len(points)


def chain_tip(armature: bpy.types.Object, chain: list[str]) -> Vector:
    return armature.matrix_world @ armature.pose.bones[chain[-1]].tail


def _candidate_score(
    armature: bpy.types.Object,
    pose_bone: bpy.types.PoseBone,
    chain: list[str],
    axis: int,
    sign: int,
    probe_angle: float,
) -> float:
    pose_bone.rotation_mode = "XYZ"
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    center = palm_center(armature)
    baseline = (chain_tip(armature, chain) - center).length
    pose_bone.rotation_euler[axis] = sign * probe_angle
    bpy.context.view_layer.update()
    changed = (chain_tip(armature, chain) - center).length
    pose_bone.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    return baseline - changed


def discover_flex_axis(
    armature: bpy.types.Object,
    bone_name: str,
    chain: list[str],
    probe_degrees: float = 12.0,
) -> dict:
    """Probe all local Euler axes/signs and choose movement toward the palm."""
    pose_bone = armature.pose.bones[bone_name]
    original_mode = pose_bone.rotation_mode
    original_basis = pose_bone.matrix_basis.copy()
    probe_angle = math.radians(probe_degrees)
    candidates = []
    try:
        for axis in range(3):
            for sign in (-1, 1):
                score = _candidate_score(armature, pose_bone, chain, axis, sign, probe_angle)
                candidates.append({"axis_index": axis, "axis": "XYZ"[axis], "sign": sign, "score": score})
    finally:
        pose_bone.rotation_mode = original_mode
        pose_bone.matrix_basis = original_basis
        bpy.context.view_layer.update()
    best = max(candidates, key=lambda item: item["score"])
    return {**best, "probe_degrees": probe_degrees, "candidates": candidates}


def control_test(
    armature: bpy.types.Object,
    mesh: bpy.types.Object,
    control_name: str,
    observed_chain: list[str],
    test_degrees: float = 15.0,
) -> dict:
    establish_neutral_pose(armature)
    before_basis = pose_basis_snapshot(armature)
    before_objects = object_transform_snapshot(armature, mesh)
    before_vertices = evaluated_mesh_vertices(mesh)
    control = armature.pose.bones[control_name]
    original_mode = control.rotation_mode
    axis = discover_flex_axis(armature, control_name, observed_chain)

    control.rotation_mode = "XYZ"
    control.rotation_euler = (0.0, 0.0, 0.0)
    control.rotation_euler[axis["axis_index"]] = axis["sign"] * math.radians(test_degrees)
    bpy.context.view_layer.update()
    during_basis = pose_basis_snapshot(armature)
    after_vertices = evaluated_mesh_vertices(mesh)
    after_objects = object_transform_snapshot(armature, mesh)

    authored_changes = [name for name, signature in during_basis.items() if signature != before_basis[name]]
    unintended = [name for name in authored_changes if name != control_name]
    delta = mesh_delta(before_vertices, after_vertices)

    control.rotation_mode = original_mode
    control.matrix_basis.identity()
    bpy.context.view_layer.update()
    reset_vertices = evaluated_mesh_vertices(mesh)
    reset_delta = mesh_delta(before_vertices, reset_vertices)
    reset_basis = pose_basis_snapshot(armature)

    passed = (
        authored_changes == [control_name]
        and not unintended
        and delta["moved_vertices"] > 0
        and before_objects == after_objects
        and reset_basis == before_basis
        and reset_delta["max_distance"] <= 1e-6
    )
    return {
        "control": control_name,
        "observed_chain": observed_chain,
        "status": "PASS" if passed else "FAIL",
        "axis": axis,
        "test_degrees": test_degrees,
        "authored_pose_changes": authored_changes,
        "unintended_pose_changes": unintended,
        "mesh_delta": delta,
        "reset_mesh_delta": reset_delta,
        "object_and_root_transform_stable": before_objects == after_objects,
        "reset_pose_exact": reset_basis == before_basis,
    }


def action_fcurves(action: bpy.types.Action, slot: bpy.types.ActionSlot):
    for layer in action.layers:
        for strip in layer.strips:
            channelbag = strip.channelbag(slot, ensure=False)
            if channelbag:
                yield from channelbag.fcurves
