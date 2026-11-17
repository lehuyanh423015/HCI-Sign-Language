"""Create the editable TECH_HAND_CONTROL_TEST fixture on a working copy."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import FINGER_CHAINS, TECHNICAL_BONES, action_fcurves, discover_flex_axis, establish_neutral_pose, matrix_signature, require_rig, sha256


ACTION_NAME = "TECH_HAND_CONTROL_TEST"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--preview-directory", required=True)
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(args)


def look_at(obj, target: Vector):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_previews(scene, armature, preview_directory: Path):
    preview_directory.mkdir(parents=True, exist_ok=True)
    original_camera = scene.camera
    camera_data = bpy.data.cameras.new("HCI_TECH_PREVIEW_CAMERA_DATA")
    camera = bpy.data.objects.new("HCI_TECH_PREVIEW_CAMERA", camera_data)
    scene.collection.objects.link(camera)

    scene.frame_set(15)
    bpy.context.view_layer.update()
    hand_points = [armature.matrix_world @ armature.pose.bones[name].head for name in ["wrist.R", "finger2-1.R", "finger5-1.R"]]
    target = sum(hand_points, Vector()) / len(hand_points)
    camera.location = target + Vector((0.0, -0.52, 0.08))
    camera_data.lens = 58
    camera_data.clip_start = 0.01
    look_at(camera, target)
    scene.camera = camera

    light_data = bpy.data.lights.new("HCI_TECH_PREVIEW_KEY_DATA", "AREA")
    light_data.energy = 700
    light_data.shape = "DISK"
    light_data.size = 2.0
    light = bpy.data.objects.new("HCI_TECH_PREVIEW_KEY", light_data)
    scene.collection.objects.link(light)
    light.location = target + Vector((0.2, -0.35, 0.45))
    look_at(light, target)

    fill_data = bpy.data.lights.new("HCI_TECH_PREVIEW_FILL_DATA", "AREA")
    fill_data.energy = 350
    fill_data.size = 1.5
    fill = bpy.data.objects.new("HCI_TECH_PREVIEW_FILL", fill_data)
    scene.collection.objects.link(fill)
    fill.location = target + Vector((-0.35, -0.15, 0.2))
    look_at(fill, target)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = (0.035, 0.045, 0.04)
    outputs = []
    for frame in (1, 15, 30):
        scene.frame_set(frame)
        output = preview_directory / ("technical-hand-test-frame-%03d.png" % frame)
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        outputs.append({"frame": frame, "path": str(output), "sha256": sha256(output)})

    scene.camera = original_camera
    for obj in (camera, light, fill):
        bpy.data.objects.remove(obj, do_unlink=True)
    for data in (camera_data, light_data, fill_data):
        if data.users == 0:
            if isinstance(data, bpy.types.Camera):
                bpy.data.cameras.remove(data)
            else:
                bpy.data.lights.remove(data)
    return outputs


def main():
    args = arguments()
    armature, mesh = require_rig()
    scene = bpy.context.scene
    original_object_transform = matrix_signature(armature.matrix_world)
    original_hierarchy = sorted((bone.name, bone.parent.name if bone.parent else None) for bone in armature.data.bones)
    establish_neutral_pose(armature)

    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 30

    old_action = bpy.data.actions.get(ACTION_NAME)
    if old_action:
        bpy.data.actions.remove(old_action)
    action = bpy.data.actions.new(ACTION_NAME)
    slot = action.slots.new(id_type="OBJECT", name=armature.name)
    animation_data = armature.animation_data_create()
    animation_data.action = action
    animation_data.action_slot = slot

    axis_map = {}
    for semantic, chain in FINGER_CHAINS.items():
        for bone_name in chain:
            axis_map[bone_name] = discover_flex_axis(armature, bone_name, chain)

    joint_angles = {
        "thumb": (35.0, 42.0, 30.0),
        "index": (58.0, 68.0, 48.0),
        "middle": (62.0, 72.0, 52.0),
        "ring": (64.0, 74.0, 54.0),
        "little": (66.0, 76.0, 56.0),
    }
    keyed_paths = []
    for frame, amount in ((1, 0.0), (15, 0.5), (30, 1.0)):
        scene.frame_set(frame)
        for semantic, chain in FINGER_CHAINS.items():
            for joint_index, bone_name in enumerate(chain):
                pose_bone = armature.pose.bones[bone_name]
                pose_bone.rotation_mode = "XYZ"
                pose_bone.rotation_euler = (0.0, 0.0, 0.0)
                axis = axis_map[bone_name]
                pose_bone.rotation_euler[axis["axis_index"]] = axis["sign"] * math.radians(joint_angles[semantic][joint_index]) * amount
                pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone_name)
                keyed_paths.append((frame, bone_name, axis["axis"]))
        bpy.context.view_layer.update()

    curves = list(action_fcurves(action, slot))
    for curve in curves:
        for keyframe in curve.keyframe_points:
            keyframe.interpolation = "BEZIER"

    scene.frame_set(1)
    output_blend = Path(args.output_blend).resolve()
    output_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend), check_existing=False)

    previews = render_previews(scene, armature, Path(args.preview_directory).resolve())
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend), check_existing=False)

    hierarchy_after = sorted((bone.name, bone.parent.name if bone.parent else None) for bone in armature.data.bones)
    animated_bones = sorted({curve.data_path.split('pose.bones["', 1)[1].split('"]', 1)[0] for curve in curves if 'pose.bones["' in curve.data_path})
    report = {
        "schema_version": 1,
        "artifact": "technical_hand_control_animation",
        "technical_fixture_only": True,
        "blender_version": bpy.app.version_string,
        "output_blend": str(output_blend),
        "output_sha256": sha256(output_blend),
        "action": {
            "name": action.name,
            "slot_identifier": slot.identifier,
            "slot_target_id_type": slot.target_id_type,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "fps": scene.render.fps,
            "fcurve_count": len(curves),
            "keyframe_point_count": sum(len(curve.keyframe_points) for curve in curves),
            "animated_bones": animated_bones,
            "expected_bones": sorted(TECHNICAL_BONES),
        },
        "axis_discovery": axis_map,
        "armature_object_transform_preserved": original_object_transform == matrix_signature(armature.matrix_world),
        "rig_hierarchy_preserved": original_hierarchy == hierarchy_after,
        "body_stationary": animated_bones == sorted(TECHNICAL_BONES),
        "previews": previews,
        "status": "PASS" if action.name == ACTION_NAME and len(curves) > 0 and animated_bones == sorted(TECHNICAL_BONES) else "FAIL",
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("[%s] %s: %d curves, %d keyframe points, %d animated finger bones" % (report["status"], action.name, len(curves), report["action"]["keyframe_point_count"], len(animated_bones)))
    print("Working source: %s" % output_blend)
    print("JSON report: %s" % report_path)
    if report["status"] != "PASS" or not report["armature_object_transform_preserved"] or not report["rig_hierarchy_preserved"]:
        raise RuntimeError("Technical animation verification failed")


if __name__ == "__main__":
    main()
