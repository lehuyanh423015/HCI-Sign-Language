"""Calibrate Snow finger controls and preview the technical hand poses."""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import evaluated_mesh_vertices, mesh_delta, sha256

FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")
FRAMES = {1: "neutral_hand", 16: "closed_fist", 31: "index_flexed", 46: "thumb_flexed", 61: "neutral_hand"}


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--poses", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--render", action="store_true")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:])


def chains():
    return {
        side: [[f"FK-Finger_{finger}{joint}.{side}" for joint in (1, 2, 3)] for finger in FINGERS]
        for side in ("L", "R")
    }


def center_and_span(bones, hand):
    knuckles = [bones[finger[0]].head.copy() for finger in hand[1:]]
    wrist = bones[hand[1][0]].parent.head.copy()
    return (wrist + sum(knuckles, Vector()) / len(knuckles)) / 2, (knuckles[0] - knuckles[-1]).length


def discover_axis(bone, tip, direction, basis):
    """Probe the two transverse local axes, retaining the Snow neutral rotation."""
    bpy.context.view_layer.update()
    rest_tip = tip.tail.copy()
    candidates = []
    for axis in (0, 2):
        for sign in (-1, 1):
            local_axis = Vector((float(axis == 0), 0.0, float(axis == 2)))
            bone.rotation_quaternion = basis @ Quaternion(local_axis, sign * math.radians(12))
            bpy.context.view_layer.update()
            candidates.append(((tip.tail - rest_tip).dot(direction), axis, sign))
    bone.rotation_quaternion = basis
    bpy.context.view_layer.update()
    return max(candidates)


def pose_snapshot(rig, body, hands, palms, baseline_vertices, baseline_tips):
    bpy.context.view_layer.update()
    distances = {}
    for side, hand in hands.items():
        distances[side] = {}
        for finger, chain in zip(FINGERS, hand):
            tip = rig.pose.bones[chain[-1]].tail
            distances[side][finger] = {
                "tip_move": round((tip - baseline_tips[side][finger]).length, 6),
                "palm_distance": round((tip - palms[side]).length, 6),
            }
    vertices = evaluated_mesh_vertices(body)
    if len(vertices) != len(baseline_vertices):
        raise RuntimeError("Evaluated mesh vertex count changed")
    return {
        "fingers": distances,
        "mesh": mesh_delta(baseline_vertices, vertices),
        "moved_vertices_by_side": {
            side: sum(
                1 for before, after in zip(baseline_vertices, vertices)
                if (before.x - rig.matrix_world.translation.x) * (1 if side == "L" else -1) > 0
                and (before - after).length > 1e-6
            )
            for side in hands
        },
    }


def hand_directions(bones, hand, side, center):
    along = (bones[hand[1][0]].head - center).normalized()
    across = (bones[hand[1][0]].head - bones[hand[-1][0]].head).normalized()
    dorsal = along.cross(across).normalized() * (1 if side == "L" else -1)
    return along, across, dorsal


def render_hands(scene, rig, hands, output):
    camera_data = bpy.data.cameras.new("Snow hand review")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = "ORTHO"
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.62, 0.72, 0.8)
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    for frame, pose in list(FRAMES.items())[:-1]:
        scene.frame_set(frame)
        for side, hand in hands.items():
            bones = rig.pose.bones
            center, span = center_and_span(bones, hand)
            along, across, dorsal = hand_directions(bones, hand, side, center)
            target = rig.matrix_world @ (center + along * span * 0.3)
            camera_data.ortho_scale = span * 3.6 * rig.matrix_world.to_scale().x
            for label, face in (("back", dorsal), ("palm", -dorsal)):
                view = face + across * 0.38 + along * 0.3
                camera.location = target + (rig.matrix_world.to_3x3() @ view).normalized() * max(span * 12, 0.7)
                camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
                scene.render.filepath = str(output / f"{frame:02}-{pose}-{side}-{label}.png")
                bpy.ops.render.render(write_still=True)


def main():
    args = arguments()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    source = Path(bpy.data.filepath).resolve()
    destination = args.output / "snow-hand-pilot.blend"
    if source == destination:
        raise ValueError("Specify a separate, disposable Snow input file.")
    hands = chains()
    names = [name for hand in hands.values() for chain in hand for name in chain]
    rig = next(obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE" and all(name in obj.pose.bones for name in names))
    skinned = [
        obj for obj in bpy.context.scene.objects if obj.type == "MESH"
        and any(mod.type == "ARMATURE" and mod.object == rig for mod in obj.modifiers)
    ]
    body = max(skinned, key=lambda obj: sum("finger" in group.name.lower() for group in obj.vertex_groups))
    scene = bpy.context.scene
    snapshot = {name: rig.pose.bones[name].matrix_basis.copy() for name in names}
    rig.animation_data_create()
    rig.animation_data.action = None
    for track in rig.animation_data.nla_tracks:
        track.mute = True
    rotations = {}
    for name in names:
        bone = rig.pose.bones[name]
        bone.rotation_mode = "QUATERNION"
        bone.matrix_basis = snapshot[name]
        rotations[name] = bone.rotation_quaternion.copy()
    bpy.context.view_layer.update()
    palms = {side: center_and_span(rig.pose.bones, hand)[0] for side, hand in hands.items()}
    baseline_tips = {
        side: {finger: rig.pose.bones[chain[-1]].tail.copy() for finger, chain in zip(FINGERS, hand)}
        for side, hand in hands.items()
    }
    baseline_vertices = evaluated_mesh_vertices(body)
    axes = {}
    for side, hand in hands.items():
        _, _, dorsal = hand_directions(rig.pose.bones, hand, side, palms[side])
        for index, chain in enumerate(hand):
            tip = rig.pose.bones[chain[-1]]
            toward_palm = -dorsal
            if index == 0:
                toward_palm = ((palms[side] - tip.tail).normalized() - dorsal * 0.65).normalized()
            for name in chain:
                axes[name] = discover_axis(rig.pose.bones[name], tip, toward_palm, rotations[name])
    poses = json.loads(args.poses.read_text(encoding="utf-8"))["poses"]
    evidence = {}
    for frame, pose in FRAMES.items():
        angles = poses[pose]["bones"]
        for hand in hands.values():
            for index, chain in enumerate(hand, 1):
                for joint, name in enumerate(chain, 1):
                    bone = rig.pose.bones[name]
                    _, axis, sign = axes[name]
                    direction = Vector((float(axis == 0), 0.0, float(axis == 2)))
                    angle = math.radians(angles[f"finger{index}-{joint}"]) * sign
                    bone.rotation_quaternion = rotations[name] @ Quaternion(direction, angle)
                    bone.keyframe_insert("rotation_quaternion", frame=frame, group=name)
        scene.frame_set(frame)
        evidence[str(frame)] = {"pose": pose, **pose_snapshot(rig, body, hands, palms, baseline_vertices, baseline_tips)}
        scene.timeline_markers.new(pose, frame=frame)
    rig.animation_data.action.name = "TECH_SNOW_HAND_PILOT"
    scene.frame_start, scene.frame_end = min(FRAMES), max(FRAMES)
    scene.frame_set(1)
    metrics = {
        "classification": "TECHNICAL_FIXTURE_NOT_A_SIGN",
        "blender_version": bpy.app.version_string,
        "source_sha256": sha256(source),
        "rig": rig.name,
        "mesh": body.name,
        "axes": {name: {"axis": "XYZ"[axis], "sign": sign, "probe_palmward_displacement": round(score, 8)} for name, (score, axis, sign) in axes.items()},
        "frames": evidence,
    }
    (args.output / "snow-hand-pilot.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), relative_remap=True, compress=True)
    if args.render:
        render_hands(scene, rig, hands, args.output)


if __name__ == "__main__":
    main()
