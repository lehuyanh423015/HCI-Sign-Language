"""Measure projected arm landmarks from an actual Blender sign scene.

The output is intended for technical before/after comparison. It does not
claim linguistic correctness and does not infer hidden depth from 2D media.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import sha256


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--frames", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    parser.add_argument("--identifier", default="S001")
    parser.add_argument("--clip", default="S001_MAIN")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def bone_point(armature, bone_name, endpoint="head"):
    bone = armature.pose.bones[bone_name]
    local = bone.head if endpoint == "head" else bone.tail
    return armature.matrix_world @ local


def fingertip(armature, side):
    for name in ("finger2-3.%s" % side, "finger2-2.%s" % side, "finger2-1.%s" % side):
        if name in armature.pose.bones:
            return bone_point(armature, name, "tail")
    raise RuntimeError("No index-finger chain found for side %s" % side)


def project(scene, camera, point):
    ndc = world_to_camera_view(scene, camera, point)
    return {"x": round(float(ndc.x), 6), "y": round(float(ndc.y), 6), "depth": round(float(ndc.z), 6)}


def main():
    args = arguments()
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    action = bpy.data.actions.get(args.clip)
    if action is None:
        raise RuntimeError("Required Action missing: %s" % args.clip)
    armature = bpy.data.objects.get("Human.rig")
    if armature is None:
        raise RuntimeError("Human.rig missing")
    frames = [int(value.strip()) for value in args.frames.split(",") if value.strip()]
    labels = [value.strip() for value in args.labels.split(",") if value.strip()]
    if len(frames) != len(labels) or len(frames) < 2:
        raise RuntimeError("--frames and --labels must contain matching entries")

    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new("TASK0011B_LandmarkCameraData")
    camera = bpy.data.objects.new("TASK0011B_LandmarkCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = Vector((0.0, -2.35, 1.42))
    camera.data.lens = 58
    look_at(camera, Vector((0.0, -0.04, 1.30)))

    samples = []
    for frame, label in zip(frames, labels):
        scene.frame_set(frame)
        points = {}
        for side in ("L", "R"):
            points[side] = {
                "shoulder": project(scene, camera, bone_point(armature, "upperarm01.%s" % side)),
                "elbow": project(scene, camera, bone_point(armature, "lowerarm01.%s" % side)),
                "wrist": project(scene, camera, bone_point(armature, "wrist.%s" % side)),
                "index_fingertip": project(scene, camera, fingertip(armature, side)),
            }
        shoulder_center_x = (points["L"]["shoulder"]["x"] + points["R"]["shoulder"]["x"]) / 2.0
        shoulder_center_y = (points["L"]["shoulder"]["y"] + points["R"]["shoulder"]["y"]) / 2.0
        shoulder_span = abs(points["L"]["shoulder"]["x"] - points["R"]["shoulder"]["x"])
        normalized = {}
        for side in ("L", "R"):
            normalized[side] = {}
            for name, value in points[side].items():
                normalized[side][name] = {
                    "x_from_shoulder_center": round((value["x"] - shoulder_center_x) / shoulder_span, 6),
                    "y_up_from_shoulder_center": round((value["y"] - shoulder_center_y) / shoulder_span, 6),
                }
        samples.append({
            "frame": frame,
            "semantic_label": label,
            "shoulder_center_ndc": {"x": round(shoulder_center_x, 6), "y": round(shoulder_center_y, 6)},
            "shoulder_span_ndc": round(shoulder_span, 6),
            "landmarks_ndc": points,
            "landmarks_shoulder_normalized": normalized,
        })

    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    source_path = Path(bpy.data.filepath).resolve()
    report = {
        "schema_version": 1,
        "artifact": "projected_sign_landmark_measurement",
        "status": "PASS",
        "identifier": args.identifier,
        "clip": args.clip,
        "classification": "TECHNICAL_GEOMETRY_MEASUREMENT_NOT_LINGUISTIC_VALIDATION",
        "blender_version": bpy.app.version_string,
        "source": {"path": str(source_path), "sha256": sha256(source_path)},
        "camera": {"location": [0.0, -2.35, 1.42], "lens_mm": 58, "target": [0.0, -0.04, 1.30]},
        "coordinate_notes": "NDC uses image width/height in [0,1]; shoulder-normalized values divide by projected shoulder span. Positive y is upward.",
        "samples": samples,
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("PASS landmark measurement: %d semantic samples" % len(samples))


if __name__ == "__main__":
    main()
