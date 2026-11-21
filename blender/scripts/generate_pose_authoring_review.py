"""Generate labeled visual evidence and MP4 from the actual Blender pilot scene."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from array import array
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import sha256


FIXTURE_ID = "TECH_POSE_AUTHORING_PILOT"
CLIP_NAME = "TECH_POSE_AUTHORING_PILOT"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--expected-version", default="5.2.4 LTS")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(values)


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_emission_material():
    material = bpy.data.materials.new("TASK0010_LabelMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (1.0, 0.54, 0.12, 1.0)
    principled.inputs["Emission Color"].default_value = (1.0, 0.25, 0.03, 1.0)
    principled.inputs["Emission Strength"].default_value = 2.5
    principled.inputs["Roughness"].default_value = 1.0
    return material


def create_label(scene, camera):
    data = bpy.data.curves.new("TASK0010_LabelData", "FONT")
    data.align_x = "LEFT"
    data.align_y = "TOP"
    data.size = 0.020
    data.extrude = 0.001
    obj = bpy.data.objects.new("TASK0010_Label", data)
    scene.collection.objects.link(obj)
    obj.parent = camera
    obj.location = (-0.46, 0.40, -1.45)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    material = make_emission_material()
    data.materials.append(material)
    return obj, data, material


def hand_target(armature, side):
    names = ["wrist.%s" % side, "finger2-1.%s" % side, "finger5-1.%s" % side]
    return sum((armature.matrix_world @ armature.pose.bones[name].head for name in names), Vector()) / len(names)


def configure_camera(camera, mode, armature):
    if mode == "left_hand":
        target = hand_target(armature, "L")
        camera.location = target + Vector((0.0, -0.50, 0.06))
        camera.data.lens = 66
    elif mode == "right_hand":
        target = hand_target(armature, "R")
        camera.location = target + Vector((0.0, -0.50, 0.06))
        camera.data.lens = 66
    elif mode == "three_quarter":
        target = Vector((0.0, -0.04, 1.24))
        camera.location = Vector((1.75, -2.25, 1.48))
        camera.data.lens = 58
    elif mode == "full_front":
        target = Vector((0.0, -0.04, 1.00))
        camera.location = Vector((0.0, -3.20, 1.30))
        camera.data.lens = 58
    else:
        target = Vector((0.0, -0.04, 1.30))
        camera.location = Vector((0.0, -2.35, 1.42))
        camera.data.lens = 58
    look_at(camera, target)


def render_still(scene, camera, label, frame, mode, output):
    scene.frame_set(frame)
    configure_camera(camera, mode, bpy.data.objects["Human.rig"])
    label.data.body = "ID/CLIP: TECH_POSE_AUTHORING_PILOT\nF%03d | %.2fs\nTECHNICAL FIXTURE | NOT A SIGN" % (
        frame, (frame - 1) / scene.render.fps,
    )
    scene.render.filepath = str(output)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    return {"frame": frame, "view": mode, "path": str(output), "sha256": sha256(output)}


def create_contact_sheet(scene, sources, output, columns=3):
    loaded = [bpy.data.images.load(str(path), check_existing=False) for path in sources]
    try:
        width, height = loaded[0].size
        rows = (len(loaded) + columns - 1) // columns
        sheet = bpy.data.images.new("TASK0010_ContactSheet", width=width * columns, height=height * rows, alpha=True, float_buffer=False)
        pixels = array("f", [0.035, 0.045, 0.04, 1.0]) * (sheet.size[0] * sheet.size[1])
        for image_index, image in enumerate(loaded):
            source = array("f", [0.0]) * (width * height * 4)
            image.pixels.foreach_get(source)
            column = image_index % columns
            row = rows - 1 - image_index // columns
            for y in range(height):
                source_start = y * width * 4
                destination_start = ((row * height + y) * sheet.size[0] + column * width) * 4
                pixels[destination_start:destination_start + width * 4] = source[source_start:source_start + width * 4]
        sheet.pixels.foreach_set(pixels)
        sheet.filepath_raw = str(output)
        sheet.file_format = "PNG"
        sheet.save()
        bpy.data.images.remove(sheet)
    finally:
        for image in loaded:
            bpy.data.images.remove(image)
    return {"path": str(output), "sha256": sha256(output), "columns": columns, "rows": rows}


def main():
    args = arguments()
    if bpy.app.version_string != args.expected_version:
        raise RuntimeError("Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    scene = bpy.context.scene
    if bpy.data.actions.get(CLIP_NAME) is None:
        raise RuntimeError("Required Action missing: %s" % CLIP_NAME)
    output_directory = Path(args.output_directory).resolve()
    raw_directory = output_directory / "raw"
    raw_directory.mkdir(parents=True, exist_ok=True)
    original_camera = scene.camera

    camera_data = bpy.data.cameras.new("TASK0010_ReviewCameraData")
    camera = bpy.data.objects.new("TASK0010_ReviewCamera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.clip_start = 0.01
    scene.camera = camera
    label, label_data, label_material = create_label(scene, camera)

    lights = []
    for name, energy, location, size in (
        ("KEY", 850, (-1.8, -2.2, 3.0), 2.0),
        ("FILL", 500, (2.0, -1.4, 2.0), 2.3),
        ("RIM", 650, (0.0, 1.2, 2.6), 1.8),
    ):
        data = bpy.data.lights.new("TASK0010_%s_Data" % name, "AREA")
        data.energy = energy
        data.size = size
        obj = bpy.data.objects.new("TASK0010_%s" % name, data)
        scene.collection.objects.link(obj)
        obj.location = location
        look_at(obj, Vector((0.0, 0.0, 1.25)))
        lights.append((obj, data))

    scene.render.engine = "BLENDER_EEVEE"
    scene.world.color = (0.025, 0.035, 0.032)
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False

    evidence = []
    evidence.append(render_still(scene, camera, label, 24, "upper_body", output_directory / "upper-body-frame-024.png"))
    evidence.append(render_still(scene, camera, label, 36, "left_hand", output_directory / "left-hand-frame-036.png"))
    evidence.append(render_still(scene, camera, label, 24, "right_hand", output_directory / "right-hand-frame-024.png"))
    evidence.append(render_still(scene, camera, label, 48, "full_front", output_directory / "front-frame-048.png"))
    evidence.append(render_still(scene, camera, label, 48, "three_quarter", output_directory / "three-quarter-frame-048.png"))

    key_paths = []
    for frame in (1, 12, 24, 36, 48, 60):
        path = raw_directory / ("key-pose-%03d.png" % frame)
        evidence.append(render_still(scene, camera, label, frame, "upper_body", path))
        key_paths.append(path)
    contact = create_contact_sheet(scene, key_paths, output_directory / "key-pose-contact-sheet.png")

    configure_camera(camera, "upper_body", bpy.data.objects["Human.rig"])
    scene.frame_start = 1
    scene.frame_end = 60
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    sequence_directory = output_directory / "animation-frames"
    sequence_directory.mkdir(parents=True, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    video_path = output_directory / "tech-pose-authoring-pilot.mp4"
    scene.render.filepath = str(sequence_directory / "frame_")

    def update_label(current_scene):
        frame = current_scene.frame_current
        label.data.body = "ID/CLIP: TECH_POSE_AUTHORING_PILOT\nF%03d | %.2fs\nTECHNICAL FIXTURE | NOT A SIGN" % (
            frame, (frame - 1) / current_scene.render.fps,
        )

    bpy.app.handlers.frame_change_pre.append(update_label)
    try:
        bpy.ops.render.render(animation=True)
    finally:
        bpy.app.handlers.frame_change_pre.remove(update_label)

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("System FFmpeg executable is required for MP4 encoding")
    ffmpeg_command = [
        ffmpeg, "-y", "-framerate", "30", "-start_number", "1",
        "-i", str(sequence_directory / "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video_path),
    ]
    completed = subprocess.run(ffmpeg_command, check=False, capture_output=True, text=True)
    if completed.returncode != 0 or not video_path.exists():
        raise RuntimeError("FFmpeg encoding failed: %s" % completed.stderr[-2000:])
    for frame_path in sequence_directory.glob("frame_*.png"):
        frame_path.unlink()
    sequence_directory.rmdir()
    video = {
        "path": str(video_path), "sha256": sha256(video_path), "size_bytes": video_path.stat().st_size,
        "frames": 60, "fps": 30, "encoder": ffmpeg, "command": ffmpeg_command,
    }
    scene.camera = original_camera
    bpy.data.objects.remove(label, do_unlink=True)
    bpy.data.curves.remove(label_data)
    bpy.data.materials.remove(label_material)
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    for obj, data in lights:
        bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.lights.remove(data)

    report = {
        "schema_version": 1,
        "artifact": "task0010_pose_authoring_visual_review",
        "status": "PASS" if len(evidence) == 11 and video["size_bytes"] > 0 else "FAIL",
        "classification": "TECHNICAL_FIXTURE_NOT_A_SIGN",
        "linguistic_status": "NOT_APPLICABLE",
        "blender_version": bpy.app.version_string,
        "source": {"path": bpy.data.filepath, "sha256": sha256(bpy.data.filepath)},
        "stills": evidence,
        "contact_sheet": contact,
        "video": video,
        "visual_quality": "NOT YET TESTED - owner must inspect generated evidence",
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("%s visual review: %d stills, contact sheet, %d-byte MP4" % (report["status"], len(evidence), video["size_bytes"]))
    if report["status"] != "PASS":
        raise RuntimeError("Visual review generation failed")


if __name__ == "__main__":
    main()
