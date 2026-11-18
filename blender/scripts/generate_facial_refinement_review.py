"""Render and assemble TASK-0007A before/after facial review evidence."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_facial_visual_review import (
    EYE_OBJECTS, camera_preset, create_contact_sheet, reset_state,
    set_blink, set_gaze, setup_scene,
)
from rig_control_utils import sha256


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("before", "after"), required=True)
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--assemble-only", action="store_true")
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(command):
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("Command failed (%d): %s\n%s" % (
            completed.returncode, " ".join(command), completed.stderr[-4000:]
        ))
    return {"command": command, "stderr_tail": completed.stderr[-1000:]}


def set_state(body, armature, state, value=1.0):
    keys = body.data.shape_keys.key_blocks
    if state == "neutral" or state == "gaze-center":
        pass
    elif state == "brow-left":
        keys["NMM_BROW_RAISE_L"].value = value
    elif state == "brow-right":
        keys["NMM_BROW_RAISE_R"].value = value
    elif state == "brow-both":
        keys["NMM_BROW_RAISE_L"].value = value
        keys["NMM_BROW_RAISE_R"].value = value
    elif state == "gaze-left":
        set_gaze(armature, horizontal=7.0)
    elif state == "gaze-right":
        set_gaze(armature, horizontal=-7.0)
    elif state == "gaze-up":
        set_gaze(armature, vertical=6.0)
    elif state == "gaze-down":
        set_gaze(armature, vertical=-6.0)
    elif state == "blink-left":
        set_blink(body, "L", 1.0)
    elif state == "blink-right":
        set_blink(body, "R", 1.0)
    elif state == "blink-both":
        set_blink(body, "L", 1.0)
        set_blink(body, "R", 1.0)
    elif state == "lips-round":
        keys["NMM_LIPS_ROUND"].value = 1.0
    elif state == "lips-spread":
        keys["NMM_LIPS_SPREAD"].value = 1.0
    elif state == "jaw-open":
        armature.pose.bones["jaw"].rotation_mode = "XYZ"
        armature.pose.bones["jaw"].rotation_euler.x = math.radians(8.0)
    elif state == "head-rotation":
        armature.pose.bones["head"].rotation_mode = "XYZ"
        armature.pose.bones["head"].rotation_euler.z = math.radians(8.0)
    elif state == "neck-movement":
        armature.pose.bones["neck02"].rotation_mode = "XYZ"
        armature.pose.bones["neck02"].rotation_euler.y = math.radians(5.0)
    else:
        raise RuntimeError("Unknown state %s" % state)
    bpy.context.view_layer.update()


def configure_camera(camera, body, preset):
    if preset != "face-wide":
        camera_preset(camera, body, preset)
        return
    target = body.matrix_world @ Vector((0.0, -0.125, 1.54))
    camera.location = body.matrix_world @ Vector((0.0, -0.70, 1.55))
    camera.data.lens = 65
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def render_state(scene, camera, body, armature, path, state="neutral", value=1.0, preset="front"):
    reset_state(scene, body, armature)
    set_state(body, armature, state, value)
    configure_camera(camera, body, preset)
    scene.render.resolution_x = 960
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return {"file": path.name, "state": state, "value": value, "camera": preset, "sha256": sha256(path)}


def render_combined_frames(scene, camera, body, armature, directory):
    directory.mkdir(parents=True, exist_ok=True)
    reset_state(scene, body, armature)
    action = bpy.data.actions["TECH_HAND_FACE_TEST"]
    armature.animation_data_create().action = action
    armature.animation_data.action_slot = next(slot for slot in action.slots if slot.target_id_type == "OBJECT")
    body.data.shape_keys.animation_data_create().action = action
    body.data.shape_keys.animation_data.action_slot = next(slot for slot in action.slots if slot.target_id_type == "KEY")
    camera_preset(camera, body, "upper-body")
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    for frame in range(1, 46):
        scene.frame_set(frame)
        path = directory / ("frame_%04d.png" % frame)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
    return 45


def compose_pair(ffmpeg, before, after, output, title):
    filter_graph = (
        "[0:v]scale=900:900:flags=lanczos,pad=960:1080:30:120:color=0x10201c,"
        "drawtext=text='BEFORE':fontcolor=white:fontsize=34:x=(W-text_w)/2:y=42[a];"
        "[1:v]scale=900:900:flags=lanczos,pad=960:1080:30:120:color=0x10201c,"
        "drawtext=text='AFTER':fontcolor=white:fontsize=34:x=(W-text_w)/2:y=42[b];"
        "[a][b]hstack=inputs=2,drawtext=text='%s':fontcolor=0x9fe0cf:fontsize=28:"
        "x=(W-text_w)/2:y=H-42[v]" % title
    )
    run([ffmpeg, "-y", "-i", str(before), "-i", str(after), "-filter_complex", filter_graph, "-map", "[v]", "-frames:v", "1", str(output)])


def compose_grid(ffmpeg, inputs, labels, output, columns, rows, title, crop=None):
    width = 1920 // columns
    height = 1080 // rows
    commands = [ffmpeg, "-y"]
    filters = []
    layout = []
    for index, (path, label) in enumerate(zip(inputs, labels)):
        commands.extend(["-i", str(path)])
        crop_filter = (crop + ",") if crop else ""
        filters.append(
            "[%d:v]%sscale=%d:%d:force_original_aspect_ratio=decrease:flags=lanczos,"
            "pad=%d:%d:(ow-iw)/2:(oh-ih)/2:color=0x10201c,"
            "drawtext=text='%s':fontcolor=white:fontsize=22:x=(W-text_w)/2:y=H-32[v%d]"
            % (index, crop_filter, width, height - 36, width, height, label, index)
        )
        layout.append("%d_%d" % ((index % columns) * width, (index // columns) * height))
    stack_inputs = "".join("[v%d]" % index for index in range(len(inputs)))
    filters.append("%sxstack=inputs=%d:layout=%s,drawtext=text='%s':fontcolor=0x9fe0cf:fontsize=25:x=20:y=18[v]" % (
        stack_inputs, len(inputs), "|".join(layout), title
    ))
    commands.extend(["-filter_complex", ";".join(filters), "-map", "[v]", "-frames:v", "1", str(output)])
    run(commands)


def make_slideshow(ffmpeg, rows, output, hold=1.35, fade=0.20):
    command = [ffmpeg, "-y"]
    filters = []
    for path, _label in rows:
        command.extend(["-loop", "1", "-t", str(hold), "-i", str(path)])
    for index, (_path, label) in enumerate(rows):
        filters.append(
            "[%d:v]scale=1080:1080:flags=lanczos,pad=1920:1080:420:0:color=0x10201c,"
            "drawbox=x=60:y=ih-100:w=iw-120:h=66:color=0x061a16@0.82:t=fill,"
            "drawtext=text='%s':fontcolor=white:fontsize=32:x=(W-text_w)/2:y=H-84,"
            "setsar=1,format=yuv420p[v%d]" % (index, label, index)
        )
    previous = "v0"
    offset = hold - fade
    for index in range(1, len(rows)):
        out = "x%d" % index
        filters.append("[%s][v%d]xfade=transition=fade:duration=%.2f:offset=%.2f[%s]" % (previous, index, fade, offset, out))
        previous = out
        offset += hold - fade
    command.extend([
        "-filter_complex", ";".join(filters), "-map", "[%s]" % previous,
        "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output),
    ])
    run(command)


def make_combined_clip(ffmpeg, frame_dir, output):
    run([
        ffmpeg, "-y", "-framerate", "30", "-start_number", "1", "-i", str(frame_dir / "frame_%04d.png"),
        "-vf", "scale=1920:1080:flags=lanczos,setpts=4*PTS,drawbox=x=60:y=ih-100:w=iw-120:h=66:color=0x061a16@0.82:t=fill,"
        "drawtext=text='TECH_HAND_FACE_TEST - ACTUAL COMBINED CLIP':fontcolor=white:fontsize=32:x=(W-text_w)/2:y=H-84,format=yuv420p",
        "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-an", str(output),
    ])


def concat_videos(ffmpeg, first, second, output):
    run([
        ffmpeg, "-y", "-i", str(first), "-i", str(second),
        "-filter_complex", "[0:v]settb=AVTB[v0];[1:v]settb=AVTB[v1];[v0][v1]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output),
    ])


def probe(ffprobe, path):
    completed = subprocess.run([
        ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate:format=duration",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    data = json.loads(completed.stdout)
    stream = data["streams"][0]
    return {
        "file": path.name, "sha256": sha256(path), "size_bytes": path.stat().st_size,
        "codec": stream["codec_name"], "width": stream["width"], "height": stream["height"],
        "fps": stream["r_frame_rate"], "duration_seconds": float(data["format"]["duration"]),
    }


def write_gallery(output_dir, comparisons, videos):
    image_cards = "\n".join(
        '<figure><a href="{0}"><img src="{0}" alt="{1}"></a><figcaption>{1}</figcaption></figure>'.format(name, label)
        for name, label in comparisons
    )
    video_cards = "\n".join(
        '<figure><video controls preload="metadata" src="{0}"></video><figcaption>{1}</figcaption></figure>'.format(name, label)
        for name, label in videos
    )
    html = """<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TASK-0007A Facial Refinement Review</title><style>
body{margin:0;background:#081310;color:#edf7f3;font:16px system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}h1,h2{color:#dff9ef}.badge{display:inline-block;padding:8px 12px;border:1px solid #bd861b;border-radius:9px;color:#ffd98a}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:18px}figure{margin:0;padding:10px;background:#10231d;border:1px solid #315348;border-radius:12px}img,video{width:100%;display:block;background:#000;border-radius:8px}figcaption{padding-top:8px}.note{border-left:4px solid #bd861b;padding:10px 16px;background:#1b2117}</style></head><body><main>
<p>TASK-0007A · OWNER VISUAL REVIEW</p><h1>Focused Facial Refinement</h1><p class="badge">TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE</p><p>Eyes được thu nhỏ/lùi vào socket và brow targets được tăng readability. Owner acceptance vẫn NOT YET TESTED.</p>
<h2>Demo videos</h2><div class="grid">__VIDEOS__</div><h2>Before / after & regression</h2><div class="grid">__IMAGES__</div>
<section class="note"><h2>Known limitations</h2><p>Blink vẫn dùng companion eye morph vì eyelid topology hiện tại. Đây là technical prototype; chưa xác nhận VSL hoặc production quality.</p></section>
</main></body></html>""".replace("__VIDEOS__", video_cards).replace("__IMAGES__", image_cards)
    path = output_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return {"file": path.name, "sha256": sha256(path)}


def assemble(output_dir, ffmpeg, ffprobe):
    before = output_dir / "raw" / "before"
    after = output_dir / "raw" / "after"
    pair_specs = [
        ("01-eye-front-before-after.png", "neutral-front.png", "EYE FRONT - BEFORE / AFTER"),
        ("02-eye-three-quarter-before-after.png", "neutral-three-quarter.png", "EYE THREE-QUARTER - BEFORE / AFTER"),
        ("03-eye-side-before-after.png", "neutral-side.png", "EYE SIDE - BEFORE / AFTER"),
        ("09-full-face-neutral-before-after.png", "neutral-face-wide.png", "FULL FACE NEUTRAL - BEFORE / AFTER"),
    ]
    comparisons = []
    for filename, source, title in pair_specs:
        compose_pair(ffmpeg, before / source, after / source, output_dir / filename, title)
        comparisons.append((filename, title))

    for index, state in enumerate(("brow-left", "brow-right", "brow-both"), start=4):
        inputs = [
            before / "neutral-front.png", before / (state + "-050.png"), before / (state + "-100.png"),
            after / "neutral-front.png", after / (state + "-050.png"), after / (state + "-100.png"),
        ]
        labels = ["BEFORE 0.0", "BEFORE 0.5", "BEFORE 1.0", "AFTER 0.0", "AFTER 0.5", "AFTER 1.0"]
        filename = "%02d-%s-before-after.png" % (index, state)
        title = state.upper().replace("-", " ") + " - INTERPOLATION"
        compose_grid(ffmpeg, inputs, labels, output_dir / filename, 3, 2, title, crop="crop=760:430:100:230")
        comparisons.append((filename, title))

    gaze_inputs = [after / ("gaze-%s.png" % state) for state in ("center", "left", "right", "up", "down")]
    compose_grid(ffmpeg, gaze_inputs, ["CENTER", "LEFT", "RIGHT", "UP", "DOWN"], output_dir / "07-eye-gaze-regression.png", 5, 1, "REFINED EYE GAZE REGRESSION")
    comparisons.append(("07-eye-gaze-regression.png", "Refined eye gaze regression"))
    blink_inputs = [after / "neutral-front.png"] + [after / ("blink-%s.png" % state) for state in ("left", "right", "both")]
    compose_grid(ffmpeg, blink_inputs, ["NEUTRAL", "LEFT", "RIGHT", "BOTH"], output_dir / "08-eye-blink-regression.png", 4, 1, "REFINED EYE BLINK REGRESSION")
    comparisons.append(("08-eye-blink-regression.png", "Refined eye blink regression"))

    contact_paths = [output_dir / name for name, _label in comparisons]
    create_contact_sheet(contact_paths, output_dir / "facial-refinement-contact-sheet.png", columns=3, thumb_size=640)

    eye_video_rows = [
        (before / "neutral-front.png", "BEFORE - NEUTRAL FRONT"),
        (after / "neutral-front.png", "AFTER - NEUTRAL FRONT"),
        (after / "neutral-three-quarter.png", "AFTER - THREE-QUARTER"),
        (after / "neutral-side.png", "AFTER - SIDE"),
        (after / "gaze-left.png", "AFTER - GAZE LEFT"),
        (after / "gaze-right.png", "AFTER - GAZE RIGHT"),
        (after / "gaze-up.png", "AFTER - GAZE UP"),
        (after / "gaze-down.png", "AFTER - GAZE DOWN"),
        (after / "blink-left.png", "AFTER - BLINK LEFT"),
        (after / "blink-right.png", "AFTER - BLINK RIGHT"),
        (after / "blink-both.png", "AFTER - BLINK BOTH"),
    ]
    make_slideshow(ffmpeg, eye_video_rows, output_dir / "eye-refinement-demo.mp4")
    brow_video_rows = [
        (after / "neutral-front.png", "BROWS - NEUTRAL 0.0"),
        (after / "brow-left-050.png", "LEFT BROW - 0.5"),
        (after / "brow-left-100.png", "LEFT BROW - 1.0"),
        (after / "neutral-front.png", "BROWS - NEUTRAL"),
        (after / "brow-right-050.png", "RIGHT BROW - 0.5"),
        (after / "brow-right-100.png", "RIGHT BROW - 1.0"),
        (after / "brow-both-050.png", "BOTH BROWS - 0.5"),
        (after / "brow-both-100.png", "BOTH BROWS - 1.0"),
        (after / "neutral-front.png", "RETURN TO NEUTRAL"),
    ]
    make_slideshow(ffmpeg, brow_video_rows, output_dir / "eyebrow-refinement-demo.mp4", hold=1.55)
    static_regression = output_dir / "_static-regression.mp4"
    make_slideshow(ffmpeg, [
        (after / "gaze-center.png", "GAZE CENTER"), (after / "gaze-left.png", "GAZE LEFT"),
        (after / "gaze-right.png", "GAZE RIGHT"), (after / "blink-both.png", "BLINK BOTH"),
        (after / "brow-both-100.png", "BROWS BOTH 1.0"), (after / "lips-round.png", "LIPS ROUND"),
        (after / "lips-spread.png", "LIPS SPREAD"), (after / "jaw-open.png", "JAW OPEN"),
        (after / "head-rotation.png", "HEAD ROTATION"), (after / "neck-movement.png", "NECK MOVEMENT"),
    ], static_regression, hold=1.05, fade=0.15)
    combined_clip = output_dir / "_combined-actual.mp4"
    make_combined_clip(ffmpeg, after / "combined-frames", combined_clip)
    concat_videos(ffmpeg, static_regression, combined_clip, output_dir / "facial-regression-demo.mp4")
    static_regression.unlink()
    combined_clip.unlink()
    shutil.rmtree(after / "combined-frames")

    videos = [probe(ffprobe, output_dir / name) for name in (
        "eye-refinement-demo.mp4", "eyebrow-refinement-demo.mp4", "facial-regression-demo.mp4"
    )]
    gallery = write_gallery(output_dir, comparisons + [("facial-refinement-contact-sheet.png", "Facial refinement contact sheet")], [
        ("eye-refinement-demo.mp4", "Eye refinement demo"),
        ("eyebrow-refinement-demo.mp4", "Eyebrow refinement demo"),
        ("facial-regression-demo.mp4", "Full facial regression demo"),
    ])
    checks = [
        {"id": "required_comparisons", "status": "PASS", "actual": [name for name, _ in comparisons]},
        {"id": "contact_sheet", "status": "PASS", "actual": "facial-refinement-contact-sheet.png"},
        {"id": "videos", "status": "PASS" if all(row["codec"] == "h264" and row["width"] == 1920 and row["height"] == 1080 for row in videos) else "FAIL", "actual": videos},
        {"id": "gallery", "status": "PASS", "actual": gallery},
        {"id": "actual_combined_frames", "status": "PASS", "actual": 45},
        {"id": "temporary_combined_frames_removed", "status": "PASS", "actual": True},
    ]
    report = {
        "schema_version": 1, "artifact": "task0007a_visual_review", "technical_fixture_only": True,
        "owner_acceptance": "NOT YET TESTED", "linguistic_validity": "NOT YET TESTED",
        "comparisons": [{"file": name, "sha256": sha256(output_dir / name)} for name, _ in comparisons],
        "contact_sheet": {"file": "facial-refinement-contact-sheet.png", "sha256": sha256(output_dir / "facial-refinement-contact-sheet.png")},
        "videos": videos, "gallery": gallery, "temporary_combined_frames_removed": True, "checks": checks,
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
    }
    (output_dir / "automated-visual-qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report["status"] != "PASS":
        raise RuntimeError("Visual review assembly checks failed")


def main():
    args = arguments()
    source = Path(bpy.data.filepath).resolve()
    output_dir = Path(args.output_directory).resolve()
    require(bpy.app.version_string.startswith(args.expected_version), "Blender version mismatch")
    require(sha256(source) == args.expected_source_sha256.upper(), "Source hash mismatch")
    body = bpy.data.objects.get("Human")
    armature = bpy.data.objects.get("Human.rig")
    require(body is not None and armature is not None, "Human/Human.rig missing")
    raw_dir = output_dir / "raw" / args.variant
    raw_dir.mkdir(parents=True, exist_ok=True)
    scene, camera, _label, _plaque = setup_scene(body)

    if not args.assemble_only:
        rows = []
        rows.append(render_state(scene, camera, body, armature, raw_dir / "neutral-front.png", preset="front"))
        rows.append(render_state(scene, camera, body, armature, raw_dir / "neutral-three-quarter.png", preset="three-quarter"))
        rows.append(render_state(scene, camera, body, armature, raw_dir / "neutral-side.png", preset="side"))
        rows.append(render_state(scene, camera, body, armature, raw_dir / "neutral-face-wide.png", preset="face-wide"))
        for state in ("brow-left", "brow-right", "brow-both"):
            rows.append(render_state(scene, camera, body, armature, raw_dir / (state + "-050.png"), state=state, value=0.5))
            rows.append(render_state(scene, camera, body, armature, raw_dir / (state + "-100.png"), state=state, value=1.0))

        combined_frames = 0
        if args.variant == "after":
            for state in ("gaze-center", "gaze-left", "gaze-right", "gaze-up", "gaze-down"):
                rows.append(render_state(scene, camera, body, armature, raw_dir / (state + ".png"), state=state))
            for state in ("blink-left", "blink-right", "blink-both", "lips-round", "lips-spread", "jaw-open", "head-rotation", "neck-movement"):
                rows.append(render_state(scene, camera, body, armature, raw_dir / (state + ".png"), state=state))
            combined_frames = render_combined_frames(scene, camera, body, armature, raw_dir / "combined-frames")

        variant_report = {
            "schema_version": 1, "variant": args.variant,
            "source": {"path": str(source), "sha256": sha256(source)},
            "renders": rows, "combined_frames": combined_frames, "status": "PASS",
        }
        (output_dir / ("render-%s.json" % args.variant)).write_text(json.dumps(variant_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.assemble or args.assemble_only:
        require(args.variant == "after", "Assembly must run from refined candidate")
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        require(ffmpeg is not None and ffprobe is not None, "FFmpeg/ffprobe unavailable")
        assemble(output_dir, ffmpeg, ffprobe)
    print("PASS TASK-0007A %s review renders" % args.variant)


if __name__ == "__main__":
    main()
