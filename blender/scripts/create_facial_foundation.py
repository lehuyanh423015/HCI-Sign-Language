"""Create the TASK-0006 facial candidate from the read-only canonical master."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import FINGER_CHAINS, action_fcurves, discover_flex_axis, establish_neutral_pose, matrix_signature, sha256


CANONICAL_SHA256 = "A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232"
CANDIDATE_VERSION = "1.0.0-rc.2"
NMM_TARGETS = (
    "NMM_BROW_RAISE_L",
    "NMM_BROW_RAISE_R",
    "NMM_EYE_BLINK_L",
    "NMM_EYE_BLINK_R",
    "NMM_LIPS_ROUND",
    "NMM_LIPS_SPREAD",
)
CLIP_NAMES = ("NMM_BLINK_TEST", "NMM_BROW_TEST", "NMM_MOUTH_TEST", "TECH_HAND_FACE_TEST")
EYE_OBJECTS = (
    "NMM_Eyeball.L", "NMM_Iris.L", "NMM_Pupil.L",
    "NMM_Eyeball.R", "NMM_Iris.R", "NMM_Pupil.R",
)


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--preview-directory", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def hierarchy_signature(armature):
    rows = sorted(
        "%s|%s|%d" % (bone.name, bone.parent.name if bone.parent else "", int(bone.use_deform))
        for bone in armature.data.bones
    )
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest().upper()


def key_coordinate_hash(key):
    digest = hashlib.sha256()
    for point in key.data:
        digest.update(("%.9f,%.9f,%.9f;" % tuple(point.co)).encode("ascii"))
    return digest.hexdigest().upper()


def make_material(name, color, roughness):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = 0.0
    return material


def eye_basis(armature, side):
    bone = armature.data.bones["eye.%s" % side]
    forward = (bone.tail_local - bone.head_local).normalized()
    lateral = Vector((1.0, 0.0, 0.0))
    lateral = (lateral - forward * forward.dot(lateral)).normalized()
    up = forward.cross(lateral).normalized()
    center = bone.head_local.lerp(bone.tail_local, 0.43) - forward * 0.004
    return center, lateral, forward, up


def ellipsoid_mesh(name, center, basis, radii, segments=28, rings=14):
    lateral, forward, up = basis
    mesh = bpy.data.meshes.new("%s_Mesh" % name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=1.0)
    for vertex in bm.verts:
        source = vertex.co.copy()
        vertex.co = (
            center
            + lateral * (source.x * radii[0])
            + forward * (source.y * radii[1])
            + up * (source.z * radii[2])
        )
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return mesh


def bind_eye_object(body, armature, name, mesh, material, bone_name, role):
    previous = bpy.data.objects.get(name)
    if previous:
        bpy.data.objects.remove(previous, do_unlink=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = armature
    obj.matrix_world = body.matrix_world.copy()
    obj.data.materials.append(material)
    group = obj.vertex_groups.new(name=bone_name)
    group.add(list(range(len(mesh.vertices))), 1.0, "REPLACE")
    modifier = obj.modifiers.new("Armature", "ARMATURE")
    modifier.object = armature
    modifier.use_vertex_groups = True
    obj["task0006_role"] = role
    obj["task0006_eye_bone"] = bone_name
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def create_eye_assets(body, armature):
    sclera = make_material("NMM_Eye_Sclera", (0.82, 0.84, 0.82, 1.0), 0.42)
    iris = make_material("NMM_Eye_Iris", (0.06, 0.24, 0.22, 1.0), 0.38)
    pupil = make_material("NMM_Eye_Pupil", (0.006, 0.009, 0.008, 1.0), 0.32)
    objects = []
    for side in ("L", "R"):
        center, lateral, forward, up = eye_basis(armature, side)
        radius = 0.0123
        objects.append(bind_eye_object(
            body, armature, "NMM_Eyeball.%s" % side,
            ellipsoid_mesh("NMM_Eyeball.%s" % side, center, (lateral, forward, up), (radius, radius, radius)),
            sclera, "eye.%s" % side, "eyeball",
        ))
        iris_center = center + forward * (radius * 0.91)
        objects.append(bind_eye_object(
            body, armature, "NMM_Iris.%s" % side,
            ellipsoid_mesh("NMM_Iris.%s" % side, iris_center, (lateral, forward, up), (0.0062, 0.00115, 0.0062), 24, 10),
            iris, "eye.%s" % side, "iris",
        ))
        pupil_center = center + forward * (radius * 1.015)
        objects.append(bind_eye_object(
            body, armature, "NMM_Pupil.%s" % side,
            ellipsoid_mesh("NMM_Pupil.%s" % side, pupil_center, (lateral, forward, up), (0.0028, 0.00075, 0.0028), 20, 8),
            pupil, "eye.%s" % side, "pupil",
        ))
    return objects


def create_eye_blink_shape_keys(objects, armature):
    """Add matching blink targets to the visible eye meshes.

    The canonical MPFB body has limited eyelid topology.  Its body target still
    provides a real lid deformation, while these companion targets flatten and
    retract the technical eye assembly so the full-weight state reads as a
    closed eye instead of leaving the pupil visible through the lid.
    """
    records = []
    for obj in objects:
        side = obj.name.rsplit(".", 1)[1]
        target_name = "NMM_EYE_BLINK_%s" % side
        center, lateral, forward, up = eye_basis(armature, side)
        basis = obj.shape_key_add(name="Basis", from_mix=False)
        key = obj.shape_key_add(name=target_name, from_mix=False)
        key.relative_key = basis
        key.value = 0.0
        key.slider_min = 0.0
        key.slider_max = 1.0
        for index, point in enumerate(basis.data):
            relative = point.co - center
            key.data[index].co = (
                center
                + lateral * lateral.dot(relative)
                + forward * (forward.dot(relative) - 0.020)
                + up * (up.dot(relative) * 0.05)
            )
        records.append({"object": obj.name, "target": target_name})
    return records


def vertex_weights(obj):
    by_index = {group.index: group.name for group in obj.vertex_groups}
    result = []
    for vertex in obj.data.vertices:
        result.append({by_index[membership.group]: membership.weight for membership in vertex.groups if membership.group in by_index})
    return result


def spatial_mask(co, center, width_x, width_z):
    dx = (co.x - center.x) / width_x
    dz = (co.z - center.z) / width_z
    return math.exp(-(dx * dx + dz * dz) * 1.7)


def create_nmm_shape_keys(body, armature):
    shape_keys = body.data.shape_keys
    if shape_keys is None:
        raise RuntimeError("Canonical Human mesh has no Shape Keys")
    basis = shape_keys.reference_key
    existing = {
        key.name: {"value": key.value, "hash": key_coordinate_hash(key)}
        for key in shape_keys.key_blocks
    }
    if any(name.startswith("NMM_") for name in existing):
        raise RuntimeError("Canonical source unexpectedly contains NMM Shape Keys")
    weights = vertex_weights(body)
    centers = {side: eye_basis(armature, side)[0] for side in ("L", "R")}
    mouth_center = armature.data.bones["oris01"].head_local.copy()

    def group_mask(index, names):
        return max((weights[index].get(name, 0.0) for name in names), default=0.0)

    created = []
    for target_name in NMM_TARGETS:
        key = body.shape_key_add(name=target_name, from_mix=False)
        key.relative_key = basis
        key.value = 0.0
        key.slider_min = 0.0
        key.slider_max = 1.0
        for index, point in enumerate(basis.data):
            co = point.co.copy()
            delta = Vector((0.0, 0.0, 0.0))
            if target_name.endswith("_L") or target_name.endswith("_R"):
                side = target_name.rsplit("_", 1)[1]
                center = centers[side]
                if target_name.startswith("NMM_BROW"):
                    names = ("oculi01.%s" % side, "orbicularis03.%s" % side, "levator05.%s" % side, "temporalis01.%s" % side)
                    mask = max(group_mask(index, names), spatial_mask(co, center + Vector((0.0, 0.0, 0.020)), 0.040, 0.027) * 0.55)
                    if co.z > center.z + 0.006 and abs(co.x - center.x) < 0.050 and co.y < -0.090:
                        delta.z += 0.0062 * min(mask, 1.0)
                        delta.y -= 0.0010 * min(mask, 1.0)
                else:
                    # Keep the blink local to the eyelid aperture.  The MPFB eye
                    # groups also contain socket/temple vertices, so using their
                    # full weight makes the orbit expand instead of closing.
                    # Move the upper lid to the eye centre, assist with the lower
                    # lid, and bring the skin forward enough to occlude the
                    # separately modelled technical eyeball.
                    mask = spatial_mask(co, center, 0.030, 0.018)
                    if abs(co.x - center.x) < 0.034 and abs(co.z - center.z) < 0.023 and co.y < -0.120:
                        if co.z >= center.z:
                            delta.z += (center.z - co.z) * 0.94 * mask
                            delta.y -= 0.0008 * mask
                        else:
                            delta.z += (center.z - co.z) * 0.38 * mask
                            delta.y -= 0.0005 * mask
            else:
                names = ("oris01", "oris03.L", "oris03.R", "oris05", "oris07.L", "oris07.R", "risorius03.L", "risorius03.R")
                mask = max(group_mask(index, names), spatial_mask(co, mouth_center, 0.050, 0.036) * 0.48)
                if abs(co.x - mouth_center.x) < 0.055 and abs(co.z - mouth_center.z) < 0.042 and co.y < -0.105:
                    if target_name == "NMM_LIPS_ROUND":
                        delta.x += (mouth_center.x - co.x) * 0.20 * min(mask, 1.0)
                        delta.z += (mouth_center.z - co.z) * 0.08 * min(mask, 1.0)
                        delta.y -= 0.0042 * min(mask, 1.0)
                    else:
                        direction = -1.0 if co.x < mouth_center.x else 1.0
                        delta.x += direction * 0.0060 * min(mask, 1.0)
                        delta.z += (mouth_center.z - co.z) * 0.05 * min(mask, 1.0)
            key.data[index].co = co + delta
        distances = [(left.co - right.co).length for left, right in zip(key.data, basis.data)]
        moved = [distance for distance in distances if distance > 1e-7]
        if not moved:
            raise RuntimeError("Generated zero-delta Shape Key: %s" % target_name)
        created.append({
            "name": target_name,
            "moved_vertices": len(moved),
            "max_delta_m": max(moved),
            "mean_delta_m": sum(moved) / len(moved),
            "value": key.value,
            "slider_min": key.slider_min,
            "slider_max": key.slider_max,
        })

    preserved = all(
        shape_keys.key_blocks[name].value == row["value"]
        and key_coordinate_hash(shape_keys.key_blocks[name]) == row["hash"]
        for name, row in existing.items()
    )
    if not preserved:
        raise RuntimeError("One or more canonical MPFB Shape Keys changed")
    return created, existing


def clear_animation_assignments(armature, shape_keys):
    armature.animation_data_clear()
    if shape_keys.animation_data:
        shape_keys.animation_data_clear()
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def new_multislot_action(name, armature, shape_keys):
    action = bpy.data.actions.new(name)
    action.use_fake_user = True
    object_slot = action.slots.new(id_type="OBJECT", name=armature.name)
    key_slot = action.slots.new(id_type="KEY", name=shape_keys.name)
    armature.animation_data_create().action = action
    armature.animation_data.action_slot = object_slot
    shape_keys.animation_data_create().action = action
    shape_keys.animation_data.action_slot = key_slot
    return action, object_slot, key_slot


def reset_expression(armature, shape_keys):
    establish_neutral_pose(armature)
    for side in ("L", "R"):
        armature.pose.bones["eye.%s" % side].scale = (1.0, 1.0, 1.0)
    for name in NMM_TARGETS:
        shape_keys.key_blocks[name].value = 0.0
    for object_name in EYE_OBJECTS:
        eye = bpy.data.objects.get(object_name)
        if eye and eye.data.shape_keys:
            for key in eye.data.shape_keys.key_blocks:
                if key.name.startswith("NMM_EYE_BLINK_"):
                    key.value = 0.0
    bpy.context.view_layer.update()


def key_shape(shape_keys, name, frame, value):
    key = shape_keys.key_blocks[name]
    key.value = value
    key.keyframe_insert(data_path="value", frame=frame)


def key_bone(armature, name, frame, rotation):
    bone = armature.pose.bones[name]
    bone.rotation_mode = "XYZ"
    bone.rotation_euler = rotation
    bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=name)


def key_bone_scale(armature, name, frame, scale):
    bone = armature.pose.bones[name]
    bone.scale = scale
    bone.keyframe_insert(data_path="scale", frame=frame, group=name)


def finalize_action(action, object_slot, key_slot):
    curves = list(action_fcurves(action, object_slot)) + list(action_fcurves(action, key_slot))
    for curve in curves:
        for point in curve.keyframe_points:
            point.interpolation = "BEZIER"
    return {
        "name": action.name,
        "slots": [object_slot.identifier, key_slot.identifier],
        "fcurve_count": len(curves),
        "keyframe_points": sum(len(curve.keyframe_points) for curve in curves),
        "data_paths": sorted({curve.data_path for curve in curves}),
    }


def create_actions(armature, body):
    shape_keys = body.data.shape_keys
    clear_animation_assignments(armature, shape_keys)
    actions = []

    action, obj_slot, key_slot = new_multislot_action("NMM_BLINK_TEST", armature, shape_keys)
    reset_expression(armature, shape_keys)
    for frame, value in ((1, 0.0), (10, 1.0), (20, 0.0), (30, 0.0)):
        key_shape(shape_keys, "NMM_EYE_BLINK_L", frame, value)
        key_shape(shape_keys, "NMM_EYE_BLINK_R", frame, value)
        eye_scale = (1.0, 1.0, 1.0 - 0.94 * value)
        key_bone_scale(armature, "eye.L", frame, eye_scale)
        key_bone_scale(armature, "eye.R", frame, eye_scale)
    actions.append(finalize_action(action, obj_slot, key_slot))

    action, obj_slot, key_slot = new_multislot_action("NMM_BROW_TEST", armature, shape_keys)
    reset_expression(armature, shape_keys)
    for frame, value in ((1, 0.0), (15, 1.0), (30, 0.0)):
        key_shape(shape_keys, "NMM_BROW_RAISE_L", frame, value)
        key_shape(shape_keys, "NMM_BROW_RAISE_R", frame, value)
    actions.append(finalize_action(action, obj_slot, key_slot))

    action, obj_slot, key_slot = new_multislot_action("NMM_MOUTH_TEST", armature, shape_keys)
    reset_expression(armature, shape_keys)
    for frame in (1, 30):
        key_shape(shape_keys, "NMM_LIPS_ROUND", frame, 0.0)
        key_shape(shape_keys, "NMM_LIPS_SPREAD", frame, 0.0)
        key_bone(armature, "jaw", frame, (0.0, 0.0, 0.0))
    key_shape(shape_keys, "NMM_LIPS_ROUND", 10, 1.0)
    key_shape(shape_keys, "NMM_LIPS_SPREAD", 10, 0.0)
    key_bone(armature, "jaw", 10, (math.radians(5.0), 0.0, 0.0))
    key_shape(shape_keys, "NMM_LIPS_ROUND", 20, 0.0)
    key_shape(shape_keys, "NMM_LIPS_SPREAD", 20, 1.0)
    key_bone(armature, "jaw", 20, (math.radians(8.0), 0.0, 0.0))
    actions.append(finalize_action(action, obj_slot, key_slot))

    action, obj_slot, key_slot = new_multislot_action("TECH_HAND_FACE_TEST", armature, shape_keys)
    reset_expression(armature, shape_keys)
    axis_map = {
        bone_name: discover_flex_axis(armature, bone_name, chain)
        for chain in FINGER_CHAINS.values() for bone_name in chain
    }
    for frame, amount in ((1, 0.0), (23, 0.62), (45, 0.0)):
        for chain in FINGER_CHAINS.values():
            for joint_index, bone_name in enumerate(chain):
                rotation = [0.0, 0.0, 0.0]
                axis = axis_map[bone_name]
                rotation[axis["axis_index"]] = axis["sign"] * math.radians((44.0, 60.0, 42.0)[joint_index]) * amount
                key_bone(armature, bone_name, frame, tuple(rotation))
        key_bone(armature, "wrist.R", frame, (0.0, 0.0, math.radians(7.0) * amount))
        key_bone(armature, "head", frame, (0.0, math.radians(-3.0) * amount, math.radians(6.0) * amount))
        key_bone(armature, "neck02", frame, (0.0, math.radians(3.0) * amount, math.radians(-2.0) * amount))
        key_bone(armature, "jaw", frame, (math.radians(7.0) * amount, 0.0, 0.0))
        key_bone(armature, "eye.L", frame, (0.0, 0.0, math.radians(7.0) * amount))
        key_bone(armature, "eye.R", frame, (0.0, 0.0, math.radians(7.0) * amount))
        key_bone_scale(armature, "eye.L", frame, (1.0, 1.0, 1.0 - 0.52 * amount))
        key_bone_scale(armature, "eye.R", frame, (1.0, 1.0, 1.0 - 0.33 * amount))
        key_shape(shape_keys, "NMM_EYE_BLINK_L", frame, 0.55 * amount)
        key_shape(shape_keys, "NMM_EYE_BLINK_R", frame, 0.35 * amount)
        key_shape(shape_keys, "NMM_BROW_RAISE_L", frame, 0.45 * amount)
        key_shape(shape_keys, "NMM_BROW_RAISE_R", frame, 0.72 * amount)
        key_shape(shape_keys, "NMM_LIPS_ROUND", frame, 0.82 * amount)
        key_shape(shape_keys, "NMM_LIPS_SPREAD", frame, 0.0)
    actions.append(finalize_action(action, obj_slot, key_slot))

    scene = bpy.context.scene
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 45
    scene.frame_set(1)
    reset_expression(armature, shape_keys)
    combined = bpy.data.actions["TECH_HAND_FACE_TEST"]
    armature.animation_data.action = combined
    armature.animation_data.action_slot = next(slot for slot in combined.slots if slot.target_id_type == "OBJECT")
    shape_keys.animation_data.action = combined
    shape_keys.animation_data.action_slot = next(slot for slot in combined.slots if slot.target_id_type == "KEY")
    scene.frame_set(1)
    return actions


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_evidence(scene, body, armature, output_directory):
    output_directory.mkdir(parents=True, exist_ok=True)
    camera_data = bpy.data.cameras.new("TASK0006_FACE_CAMERA_DATA")
    camera = bpy.data.objects.new("TASK0006_FACE_CAMERA", camera_data)
    scene.collection.objects.link(camera)
    target = body.matrix_world @ Vector((0.0, -0.125, 1.555))
    camera.location = body.matrix_world @ Vector((0.0, -0.58, 1.57))
    camera_data.lens = 72
    camera_data.clip_start = 0.01
    look_at(camera, target)
    scene.camera = camera

    lights = []
    for suffix, energy, local_position, size in (
        ("KEY", 700, Vector((-0.45, -0.55, 1.95)), 0.8),
        ("FILL", 350, Vector((0.45, -0.35, 1.72)), 0.7),
        ("RIM", 450, Vector((0.0, 0.15, 1.9)), 0.6),
    ):
        data = bpy.data.lights.new("TASK0006_%s_DATA" % suffix, "AREA")
        data.energy = energy
        data.size = size
        light = bpy.data.objects.new("TASK0006_%s" % suffix, data)
        scene.collection.objects.link(light)
        light.location = body.matrix_world @ local_position
        look_at(light, target)
        lights.append(light)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.025, 0.035, 0.033)
    shape_keys = body.data.shape_keys
    outputs = []

    def reset():
        if armature.animation_data:
            armature.animation_data.action = None
        if shape_keys.animation_data:
            shape_keys.animation_data.action = None
        scene.frame_set(1)
        reset_expression(armature, shape_keys)

    def set_blink(side, value):
        shape_keys.key_blocks["NMM_EYE_BLINK_%s" % side].value = value
        for object_name in EYE_OBJECTS:
            if object_name.endswith(".%s" % side):
                eye_shape_keys = bpy.data.objects[object_name].data.shape_keys
                eye_shape_keys.key_blocks["NMM_EYE_BLINK_%s" % side].value = value

    def render(name, setup):
        reset()
        setup()
        bpy.context.view_layer.update()
        path = output_directory / (name + ".png")
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs.append({"state": name, "path": str(path), "sha256": sha256(path)})

    render("01-neutral-face", lambda: None)
    render("02-eyes-look-left", lambda: [setattr(armature.pose.bones[name].rotation_euler, "z", math.radians(7.0)) for name in ("eye.L", "eye.R")])
    render("03-eyes-look-right", lambda: [setattr(armature.pose.bones[name].rotation_euler, "z", math.radians(-7.0)) for name in ("eye.L", "eye.R")])
    render("04-left-eye-blink", lambda: set_blink("L", 1.0))
    render("05-right-eye-blink", lambda: set_blink("R", 1.0))
    render("06-both-eyes-blink", lambda: [set_blink(side, 1.0) for side in ("L", "R")])
    render("07-eyebrows-raised", lambda: [setattr(shape_keys.key_blocks[name], "value", 1.0) for name in ("NMM_BROW_RAISE_L", "NMM_BROW_RAISE_R")])
    render("08-mouth-open", lambda: setattr(armature.pose.bones["jaw"].rotation_euler, "x", math.radians(8.0)))
    render("09-lips-rounded", lambda: setattr(shape_keys.key_blocks["NMM_LIPS_ROUND"], "value", 1.0))
    render("10-lips-spread", lambda: setattr(shape_keys.key_blocks["NMM_LIPS_SPREAD"], "value", 1.0))
    render("11-head-rotation", lambda: setattr(armature.pose.bones["head"].rotation_euler, "z", math.radians(8.0)))

    def combined_setup():
        combined = bpy.data.actions["TECH_HAND_FACE_TEST"]
        armature.animation_data.action = combined
        armature.animation_data.action_slot = next(slot for slot in combined.slots if slot.target_id_type == "OBJECT")
        shape_keys.animation_data.action = combined
        shape_keys.animation_data.action_slot = next(slot for slot in combined.slots if slot.target_id_type == "KEY")
        scene.frame_set(23)
        camera.location = body.matrix_world @ Vector((0.0, -2.25, 1.38))
        camera.data.lens = 55
        look_at(camera, body.matrix_world @ Vector((0.0, -0.05, 1.30)))

    render("12-combined-hand-face", combined_setup)
    reset()
    bpy.data.objects.remove(camera, do_unlink=True)
    for light in lights:
        bpy.data.objects.remove(light, do_unlink=True)
    return outputs


def eye_record(obj):
    expected_bone = obj["task0006_eye_bone"]
    group = obj.vertex_groups.get(expected_bone)
    weighted = 0
    if group:
        for vertex in obj.data.vertices:
            if any(membership.group == group.index and abs(membership.weight - 1.0) < 1e-6 for membership in vertex.groups):
                weighted += 1
    return {
        "name": obj.name,
        "role": obj["task0006_role"],
        "bone": expected_bone,
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "fully_weighted_vertices": weighted,
        "armature_modifiers": [modifier.object.name for modifier in obj.modifiers if modifier.type == "ARMATURE" and modifier.object],
        "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
    }


def main():
    args = arguments()
    if not bpy.app.version_string.startswith(args.expected_version):
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    source_path = Path(bpy.data.filepath).resolve()
    source_hash = sha256(source_path)
    if source_hash != CANONICAL_SHA256:
        raise RuntimeError("Canonical source hash mismatch: %s" % source_hash)
    output = Path(args.output_blend).resolve()
    if source_path == output:
        raise RuntimeError("Refusing to overwrite canonical master")
    armature = bpy.data.objects.get("Human.rig")
    body = bpy.data.objects.get("Human")
    if armature is None or body is None or len(armature.data.bones) != 137:
        raise RuntimeError("Canonical Human/Human.rig structure is missing")
    hierarchy_before = hierarchy_signature(armature)
    armature_matrix_before = matrix_signature(armature.matrix_world)

    eyes = create_eye_assets(body, armature)
    eye_blink_targets = create_eye_blink_shape_keys(eyes, armature)
    shape_key_rows, existing_keys = create_nmm_shape_keys(body, armature)
    action_rows = create_actions(armature, body)
    scene = bpy.context.scene
    scene["master_avatar_version"] = CANDIDATE_VERSION
    scene["master_avatar_status"] = "experimental-facial-candidate"
    scene["master_avatar_source_sha256"] = CANONICAL_SHA256

    output.parent.mkdir(parents=True, exist_ok=True)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)
    previews = render_evidence(scene, body, armature, Path(args.preview_directory).resolve())
    scene.frame_set(1)
    reset_expression(armature, body.data.shape_keys)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), check_existing=False)

    eye_rows = [eye_record(obj) for obj in eyes]
    output_hash = sha256(output)
    manifest = {
        "schema_version": 1,
        "version": CANDIDATE_VERSION,
        "status": "experimental-owner-review-candidate",
        "canonical_source": {"path": "blender/master/avatar_master.blend", "sha256": CANONICAL_SHA256},
        "candidate_file": "blender/working/huy-anh/task-0006-facial-foundation/avatar_master_facial_candidate.blend",
        "candidate_sha256": output_hash,
        "blender_version": bpy.app.version_string,
        "mpfb_version": "2.0.18",
        "bone_count": len(armature.data.bones),
        "hierarchy_sha256": hierarchy_signature(armature),
        "eye_objects": [row["name"] for row in eye_rows],
        "morph_targets": [row["name"] for row in shape_key_rows],
        "technical_clips": [row["name"] for row in action_rows],
        "fps": scene.render.fps,
        "linguistic_status": "NOT YET TESTED",
        "last_validation_date": "2026-11-17",
    }
    manifest_path = Path(args.manifest).resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema_version": 1,
        "artifact": "task0006_facial_candidate_creation",
        "status": "PASS",
        "technical_fixture_only": True,
        "linguistic_status": "NOT YET TESTED",
        "blender_version": bpy.app.version_string,
        "source": {"path": str(source_path), "sha256": source_hash},
        "output": {"path": str(output), "sha256": output_hash, "version": CANDIDATE_VERSION},
        "preservation": {
            "canonical_output_separate": source_path != output,
            "bone_count": len(armature.data.bones),
            "hierarchy_unchanged": hierarchy_before == hierarchy_signature(armature),
            "armature_object_transform_unchanged": armature_matrix_before == matrix_signature(armature.matrix_world),
            "existing_shape_key_count": len(existing_keys),
            "existing_shape_keys_preserved": all(
                body.data.shape_keys.key_blocks[name].value == row["value"]
                and key_coordinate_hash(body.data.shape_keys.key_blocks[name]) == row["hash"]
                for name, row in existing_keys.items()
            ),
        },
        "eye_assets": eye_rows,
        "eye_blink_targets": eye_blink_targets,
        "morph_targets": shape_key_rows,
        "actions": action_rows,
        "previews": previews,
    }
    if not all(row["fully_weighted_vertices"] == row["vertices"] for row in eye_rows):
        report["status"] = "FAIL"
    if not all(row["moved_vertices"] > 0 for row in shape_key_rows):
        report["status"] = "FAIL"
    if not all(report["preservation"].values()):
        report["status"] = "FAIL"
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("[%s] facial candidate: %s" % (report["status"], output))
    print("Eyes: %d objects; Morph Targets: %d; Actions: %d" % (len(eyes), len(shape_key_rows), len(action_rows)))
    print("JSON report: %s" % report_path)
    if report["status"] != "PASS":
        raise RuntimeError("Facial candidate creation checks failed")


if __name__ == "__main__":
    main()
