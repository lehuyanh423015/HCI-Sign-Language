"""Record camera-relative palm orientation without rendering screenshots."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--clip", default="S002_MAIN")
    parser.add_argument("--frames", default="23,31,40")
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(values)


def rounded(vector):
    return [round(float(value), 6) for value in vector]


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    args = arguments()
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    if bpy.data.actions.get(args.clip) is None:
        raise RuntimeError("Required Action missing: %s" % args.clip)

    frames = [int(value.strip()) for value in args.frames.split(",") if value.strip()]
    if frames != sorted(set(frames)):
        raise RuntimeError("--frames must contain unique increasing frame numbers")

    scene = bpy.context.scene
    armature = bpy.data.objects["Human.rig"]
    camera_data = bpy.data.cameras.new("TASK0012B_PalmDiagnosticCameraData")
    camera = bpy.data.objects.new("TASK0012B_PalmDiagnosticCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = Vector((0.0, -2.35, 1.42))
    camera.data.lens = 58
    look_at(camera, Vector((0.0, -0.04, 1.30)))
    bpy.context.view_layer.update()
    camera_inverse = camera.matrix_world.to_3x3().inverted()

    def point(name, tail=False):
        bone = armature.pose.bones[name]
        return armature.matrix_world @ (bone.tail if tail else bone.head)

    def direction_in_camera(vector):
        return camera_inverse @ vector

    def screen_projection(point_world):
        value = world_to_camera_view(scene, camera, point_world)
        return [round(float(value.x), 6), round(float(value.y), 6), round(float(value.z), 6)]

    def bone_axes(name):
        bone = armature.pose.bones[name]
        world_rotation = (armature.matrix_world @ bone.matrix).to_3x3()
        return {
            "x": rounded(world_rotation @ Vector((1.0, 0.0, 0.0))),
            "y_longitudinal": rounded(world_rotation @ Vector((0.0, 1.0, 0.0))),
            "z": rounded(world_rotation @ Vector((0.0, 0.0, 1.0))),
        }

    rows = []
    for frame in frames:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        frame_row = {"frame": frame, "hands": {}}
        for side in ("L", "R"):
            wrist = point("wrist.%s" % side)
            elbow = point("lowerarm01.%s" % side)
            shoulder = point("upperarm01.%s" % side)
            index_base = point("finger2-1.%s" % side)
            little_base = point("finger5-1.%s" % side)
            middle_tip = point("finger3-3.%s" % side, tail=True)
            landmark_normal = (index_base - wrist).cross(little_base - wrist).normalized()
            # MPFB left/right rest bones have opposite handedness. This sign convention
            # points from the dorsal plane toward the anatomical palm side.
            palmar_normal = landmark_normal if side == "R" else -landmark_normal
            palm_longitudinal = (((index_base + little_base) / 2.0) - wrist).normalized()
            finger_direction = (middle_tip - wrist).normalized()
            palm_center = (wrist + index_base + little_base) / 3.0
            palmar_camera = direction_in_camera(palmar_normal)
            longitudinal_camera = direction_in_camera(palm_longitudinal)
            finger_camera = direction_in_camera(finger_direction)
            lowerarm = armature.pose.bones["lowerarm01.%s" % side]
            wrist_bone = armature.pose.bones["wrist.%s" % side]
            frame_row["hands"][side] = {
                "landmarks_world": {
                    "shoulder": rounded(shoulder),
                    "elbow": rounded(elbow),
                    "wrist": rounded(wrist),
                    "index_base": rounded(index_base),
                    "little_base": rounded(little_base),
                    "palm_center": rounded(palm_center),
                },
                "screen_projection_normalized": {
                    "shoulder": screen_projection(shoulder),
                    "elbow": screen_projection(elbow),
                    "wrist": screen_projection(wrist),
                    "palm_center": screen_projection(palm_center),
                },
                "palmar_normal_world": rounded(palmar_normal),
                "palmar_normal_camera": rounded(palmar_camera),
                "components": {
                    "world_up_z": round(float(palmar_normal.z), 6),
                    "camera_up_y": round(float(palmar_camera.y), 6),
                    "toward_camera_z": round(float(palmar_camera.z), 6),
                },
                "palm_longitudinal_world": rounded(palm_longitudinal),
                "palm_longitudinal_camera": rounded(longitudinal_camera),
                "middle_finger_direction_world": rounded(finger_direction),
                "middle_finger_direction_camera": rounded(finger_camera),
                "bone_local_axes_world": {
                    "lowerarm01": bone_axes("lowerarm01.%s" % side),
                    "lowerarm02": bone_axes("lowerarm02.%s" % side),
                    "wrist": bone_axes("wrist.%s" % side),
                },
                "local_euler_degrees": {
                    "lowerarm01": [round(math.degrees(value), 6) for value in lowerarm.rotation_euler],
                    "lowerarm02": [round(math.degrees(value), 6) for value in armature.pose.bones["lowerarm02.%s" % side].rotation_euler],
                    "wrist": [round(math.degrees(value), 6) for value in wrist_bone.rotation_euler],
                },
            }
        rows.append(frame_row)

    report = {
        "schema_version": 1,
        "artifact": "palm_orientation_diagnostic",
        "status": "MEASURED",
        "blender_version": bpy.app.version_string,
        "clip": args.clip,
        "coordinate_conventions": {
            "world_up": "+Z",
            "camera_up": "+Y",
            "toward_camera": "+Z in review-camera local space",
            "palmar_normal": "landmark cross product with MPFB side-specific sign: R raw, L negated",
        },
        "review_camera": {
            "location_world": rounded(camera.location),
            "target_world": [0.0, -0.04, 1.30],
            "lens_mm": camera.data.lens,
        },
        "frames": rows,
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("MEASURED palm orientation: %s -> %s" % (",".join(str(frame) for frame in frames), output))


if __name__ == "__main__":
    main()
