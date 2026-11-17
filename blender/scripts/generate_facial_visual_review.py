"""Generate the TASK-0007 owner-friendly facial visual review package."""

from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rig_control_utils import establish_neutral_pose, sha256


CANONICAL_SHA256 = "A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232"
CANDIDATE_SHA256 = "4F4BA651A8E15B356FBA18625826E5A0EBF29CBF631746A6B295DA667B27A982"
TARGETS = (
    "NMM_BROW_RAISE_L", "NMM_BROW_RAISE_R", "NMM_EYE_BLINK_L",
    "NMM_EYE_BLINK_R", "NMM_LIPS_ROUND", "NMM_LIPS_SPREAD",
)
EYE_OBJECTS = (
    "NMM_Eyeball.L", "NMM_Iris.L", "NMM_Pupil.L",
    "NMM_Eyeball.R", "NMM_Iris.R", "NMM_Pupil.R",
)
CLIPS = ("NMM_BLINK_TEST", "NMM_BROW_TEST", "NMM_MOUTH_TEST", "TECH_HAND_FACE_TEST")


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--review-blend", required=True)
    parser.add_argument("--expected-version", default="5.2.4")
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(args)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def emission_material(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Emission Color"].default_value = color
    principled.inputs["Emission Strength"].default_value = 0.8
    principled.inputs["Roughness"].default_value = 1.0
    return material


def create_overlay(camera):
    plaque_mesh = bpy.data.meshes.new("TASK0007_LabelPlaqueMesh")
    plaque_mesh.from_pydata(
        [(-0.103, -0.012, 0.0), (0.103, -0.012, 0.0), (0.103, 0.012, 0.0), (-0.103, 0.012, 0.0)],
        [], [(0, 1, 2, 3)],
    )
    plaque = bpy.data.objects.new("TASK0007_LabelPlaque", plaque_mesh)
    bpy.context.scene.collection.objects.link(plaque)
    plaque.parent = camera
    plaque.matrix_parent_inverse = Matrix.Identity(4)
    plaque.location = (0.0, -0.051, -0.42)
    plaque.data.materials.append(emission_material("TASK0007_LabelPlaqueMaterial", (0.02, 0.035, 0.03, 1.0)))

    curve = bpy.data.curves.new("TASK0007_LabelTextCurve", "FONT")
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 0.0105
    curve.extrude = 0.0
    label = bpy.data.objects.new("TASK0007_LabelText", curve)
    bpy.context.scene.collection.objects.link(label)
    label.parent = camera
    label.matrix_parent_inverse = Matrix.Identity(4)
    label.location = (0.0, -0.051, -0.417)
    label.data.materials.append(emission_material("TASK0007_LabelTextMaterial", (0.88, 0.98, 0.94, 1.0)))
    # Keep the overlay objects in the handoff scene, but do not bake them over
    # facial features. Labels are composited at the lower edge after rendering.
    plaque.hide_render = True
    label.hide_render = True
    return label, plaque


def setup_scene(body):
    scene = bpy.context.scene
    for obj in list(scene.objects):
        if obj.type in {"CAMERA", "LIGHT"} or obj.name.startswith(("TASK0005_", "TASK0006_", "TASK0007_")):
            obj.hide_render = True
    armature = bpy.data.objects["Human.rig"]
    armature.hide_render = True
    armature.show_in_front = False

    camera_data = bpy.data.cameras.new("TASK0007_ReviewCameraData")
    camera = bpy.data.objects.new("TASK0007_ReviewCamera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.lens = 72
    camera_data.clip_start = 0.01
    scene.camera = camera

    target = body.matrix_world @ Vector((0.0, -0.125, 1.555))
    for name, energy, position, size in (
        ("Key", 330, Vector((-0.48, -0.52, 1.98)), 0.85),
        ("Fill", 135, Vector((0.48, -0.34, 1.74)), 0.75),
        ("Rim", 210, Vector((0.0, 0.18, 1.92)), 0.65),
    ):
        data = bpy.data.lights.new("TASK0007_%sLightData" % name, "AREA")
        data.energy = energy
        data.size = size
        light = bpy.data.objects.new("TASK0007_%sLight" % name, data)
        scene.collection.objects.link(light)
        light.location = body.matrix_world @ position
        look_at(light, target)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.025, 0.035, 0.033)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -2.2
    scene.render.fps = 30
    label, plaque = create_overlay(camera)
    return scene, camera, label, plaque


def camera_preset(camera, body, preset):
    target = body.matrix_world @ Vector((0.0, -0.125, 1.555))
    if preset == "front":
        camera.location = body.matrix_world @ Vector((0.0, -0.58, 1.57))
        camera.data.lens = 72
    elif preset == "three-quarter":
        camera.location = body.matrix_world @ Vector((0.34, -0.53, 1.60))
        camera.data.lens = 76
    elif preset == "side":
        camera.location = body.matrix_world @ Vector((0.54, -0.16, 1.58))
        camera.data.lens = 78
    elif preset == "upper-body":
        camera.location = body.matrix_world @ Vector((0.0, -2.25, 1.38))
        camera.data.lens = 55
        target = body.matrix_world @ Vector((0.0, -0.05, 1.30))
    elif preset == "full-body":
        camera.location = body.matrix_world @ Vector((0.0, -3.20, 1.16))
        camera.data.lens = 52
        target = body.matrix_world @ Vector((0.0, -0.05, 1.05))
    else:
        raise RuntimeError("Unknown camera preset %s" % preset)
    look_at(camera, target)


def reset_state(scene, body, armature):
    if armature.animation_data:
        armature.animation_data.action = None
    shape_keys = body.data.shape_keys
    if shape_keys.animation_data:
        shape_keys.animation_data.action = None
    scene.frame_set(1)
    establish_neutral_pose(armature)
    for bone_name in ("eye.L", "eye.R"):
        armature.pose.bones[bone_name].scale = (1.0, 1.0, 1.0)
    for name in TARGETS:
        shape_keys.key_blocks[name].value = 0.0
    for object_name in EYE_OBJECTS:
        obj = bpy.data.objects[object_name]
        if obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                if key.name.startswith("NMM_"):
                    key.value = 0.0
    bpy.context.view_layer.update()


def set_blink(body, side, value):
    name = "NMM_EYE_BLINK_%s" % side
    body.data.shape_keys.key_blocks[name].value = value
    for object_name in EYE_OBJECTS:
        if object_name.endswith(".%s" % side):
            bpy.data.objects[object_name].data.shape_keys.key_blocks[name].value = value


def set_gaze(armature, horizontal=0.0, vertical=0.0):
    for name in ("eye.L", "eye.R"):
        bone = armature.pose.bones[name]
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (math.radians(vertical), 0.0, math.radians(horizontal))


def apply_state(name, body, armature):
    keys = body.data.shape_keys.key_blocks
    if name == "brow-left":
        keys["NMM_BROW_RAISE_L"].value = 1.0
    elif name == "brow-right":
        keys["NMM_BROW_RAISE_R"].value = 1.0
    elif name == "brow-both":
        keys["NMM_BROW_RAISE_L"].value = keys["NMM_BROW_RAISE_R"].value = 1.0
    elif name == "blink-left":
        set_blink(body, "L", 1.0)
    elif name == "blink-right":
        set_blink(body, "R", 1.0)
    elif name == "blink-both":
        set_blink(body, "L", 1.0)
        set_blink(body, "R", 1.0)
    elif name == "lips-round":
        keys["NMM_LIPS_ROUND"].value = 1.0
    elif name == "lips-spread":
        keys["NMM_LIPS_SPREAD"].value = 1.0
    elif name == "gaze-left":
        set_gaze(armature, horizontal=7.0)
    elif name == "gaze-right":
        set_gaze(armature, horizontal=-7.0)
    elif name == "gaze-up":
        set_gaze(armature, vertical=-5.0)
    elif name == "gaze-down":
        set_gaze(armature, vertical=5.0)
    elif name == "jaw-open":
        armature.pose.bones["jaw"].rotation_mode = "XYZ"
        armature.pose.bones["jaw"].rotation_euler.x = math.radians(8.0)
    elif name == "head-rotation":
        armature.pose.bones["head"].rotation_mode = "XYZ"
        armature.pose.bones["head"].rotation_euler.z = math.radians(8.0)
    elif name == "neck-movement":
        armature.pose.bones["neck02"].rotation_mode = "XYZ"
        armature.pose.bones["neck02"].rotation_euler = (0.0, math.radians(5.0), math.radians(-4.0))
    elif name == "combined":
        keys["NMM_BROW_RAISE_L"].value = 0.45
        keys["NMM_BROW_RAISE_R"].value = 0.72
        set_blink(body, "L", 0.55)
        set_blink(body, "R", 0.35)
        keys["NMM_LIPS_ROUND"].value = 0.82
        armature.pose.bones["jaw"].rotation_mode = "XYZ"
        armature.pose.bones["jaw"].rotation_euler.x = math.radians(4.5)
        armature.pose.bones["head"].rotation_mode = "XYZ"
        armature.pose.bones["head"].rotation_euler.z = math.radians(4.0)
        armature.pose.bones["neck02"].rotation_mode = "XYZ"
        armature.pose.bones["neck02"].rotation_euler.y = math.radians(2.0)
        set_gaze(armature, horizontal=4.0)
    elif name not in {"neutral", "gaze-center"}:
        raise RuntimeError("Unknown review state %s" % name)
    bpy.context.view_layer.update()


def overlay_label(ffmpeg, image_path, title):
    safe_title = title.replace("·", "-").replace("Â", "")
    safe_title = " ".join(safe_title.encode("ascii", "ignore").decode("ascii").split())
    escaped_title = safe_title.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    temporary = image_path.with_name(image_path.stem + ".labeled.png")
    filter_expression = (
        "drawbox=x=24:y=ih-76:w=iw-48:h=52:color=0x10201c@0.82:t=fill,"
        "drawtext=text='%s':fontcolor=white:fontsize=24:x=(W-text_w)/2:y=H-65" % escaped_title
    )
    run([ffmpeg, "-y", "-i", str(image_path), "-vf", filter_expression, "-frames:v", "1", str(temporary)])
    image_path.unlink()
    temporary.replace(image_path)
    return safe_title


def render_still(scene, camera, label, body, armature, output, state, title, ffmpeg, preset="front"):
    reset_state(scene, body, armature)
    apply_state(state, body, armature)
    camera_preset(camera, body, preset)
    label.data.body = title
    scene.render.resolution_x = 960
    scene.render.resolution_y = 960
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    safe_title = overlay_label(ffmpeg, output, title)
    return {"file": output.name, "state": state, "label": safe_title, "camera": preset, "sha256": sha256(output), "size_bytes": output.stat().st_size}


def create_contact_sheet(paths, output, columns, thumb_size=360):
    rows = math.ceil(len(paths) / columns)
    width = columns * thumb_size
    height = rows * thumb_size
    canvas = array("f", [0.025, 0.035, 0.033, 1.0]) * (width * height)
    for index, image_path in enumerate(paths):
        image = bpy.data.images.load(str(image_path), check_existing=False)
        image.scale(thumb_size, thumb_size)
        pixels = array("f", [0.0]) * (thumb_size * thumb_size * 4)
        image.pixels.foreach_get(pixels)
        row = index // columns
        column = index % columns
        target_y_base = (rows - 1 - row) * thumb_size
        target_x_base = column * thumb_size
        for y in range(thumb_size):
            source_start = y * thumb_size * 4
            target_start = ((target_y_base + y) * width + target_x_base) * 4
            canvas[target_start:target_start + thumb_size * 4] = pixels[source_start:source_start + thumb_size * 4]
        bpy.data.images.remove(image)
    result = bpy.data.images.new(output.stem, width=width, height=height, alpha=False, float_buffer=False)
    result.pixels.foreach_set(canvas)
    result.filepath_raw = str(output)
    result.file_format = "PNG"
    result.save()
    bpy.data.images.remove(result)
    return {"file": output.name, "columns": columns, "rows": rows, "width": width, "height": height, "sha256": sha256(output)}


def run(command):
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError("Command failed (%d): %s\n%s" % (completed.returncode, " ".join(command), completed.stderr[-3000:]))
    return {"command": command, "stdout_tail": completed.stdout[-1200:], "stderr_tail": completed.stderr[-1200:]}


def make_facial_video(ffmpeg, preview_dir, output):
    names = [
        "01-neutral-front.png", "04-brow-left.png", "05-brow-right.png", "06-brow-both.png",
        "07-blink-left.png", "08-blink-right.png", "09-blink-both.png", "10-lips-round.png",
        "11-lips-spread.png", "17-jaw-open.png", "13-gaze-left.png", "14-gaze-right.png",
        "18-head-rotation.png", "19-neck-movement.png", "01-neutral-front.png",
    ]
    command = [ffmpeg, "-y"]
    for name in names:
        command.extend(["-loop", "1", "-t", "1.8", "-i", str(preview_dir / name)])
    filters = []
    for index in range(len(names)):
        filters.append("[%d:v]scale=1080:1080:flags=lanczos,pad=1920:1080:420:0:color=0x16231f,setsar=1,format=yuv420p[v%d]" % (index, index))
    previous = "v0"
    offset = 1.5
    for index in range(1, len(names)):
        output_label = "x%d" % index
        filters.append("[%s][v%d]xfade=transition=fade:duration=0.30:offset=%.2f[%s]" % (previous, index, offset, output_label))
        previous = output_label
        offset += 1.5
    command.extend([
        "-filter_complex", ";".join(filters), "-map", "[%s]" % previous,
        "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output),
    ])
    return run(command)


def assign_combined_action(body, armature):
    action = bpy.data.actions["TECH_HAND_FACE_TEST"]
    armature.animation_data_create().action = action
    armature.animation_data.action_slot = next(slot for slot in action.slots if slot.target_id_type == "OBJECT")
    body.data.shape_keys.animation_data_create().action = action
    body.data.shape_keys.animation_data.action_slot = next(slot for slot in action.slots if slot.target_id_type == "KEY")


def render_combined_frames(scene, camera, label, body, armature, frame_dir):
    frame_dir.mkdir(parents=True, exist_ok=True)
    reset_state(scene, body, armature)
    assign_combined_action(body, armature)
    camera_preset(camera, body, "upper-body")
    label.data.body = "TECH_HAND_FACE_TEST · TECHNICAL INTEGRATION"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    rows = []
    for frame in range(1, 46):
        scene.frame_set(frame)
        output = frame_dir / ("frame_%04d.png" % frame)
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        rows.append(output)
    return rows


def make_combined_video(ffmpeg, frame_dir, output):
    first = frame_dir / "frame_0001.png"
    last = frame_dir / "frame_0045.png"
    sequence = frame_dir / "frame_%04d.png"
    command = [
        ffmpeg, "-y", "-loop", "1", "-t", "1.5", "-i", str(first),
        "-framerate", "30", "-start_number", "1", "-i", str(sequence),
        "-loop", "1", "-t", "1.5", "-i", str(last),
        "-filter_complex",
        "[0:v]scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p[intro];"
        "[1:v]scale=1920:1080:flags=lanczos,setpts=6*PTS,setsar=1,format=yuv420p[anim];"
        "[2:v]scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p[outro];"
        "[intro][anim][outro]concat=n=3:v=1:a=0[joined];"
        "[joined]drawbox=x=48:y=ih-96:w=iw-96:h=64:color=0x10201c@0.82:t=fill,"
        "drawtext=text='TECH_HAND_FACE_TEST - TECHNICAL INTEGRATION':fontcolor=white:fontsize=30:"
        "x=(W-text_w)/2:y=H-80[v]",
        "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(output),
    ]
    return run(command)


def probe_video(ffprobe, path):
    completed = subprocess.run([
        ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,duration",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    data = json.loads(completed.stdout)
    stream = data["streams"][0]
    return {
        "file": path.name, "sha256": sha256(path), "size_bytes": path.stat().st_size,
        "codec": stream.get("codec_name"), "width": stream.get("width"), "height": stream.get("height"),
        "fps": stream.get("r_frame_rate"), "duration_seconds": float(stream.get("duration", 0.0)),
    }


def write_gallery(output_dir, previews, contact_sheets, videos):
    cards = "\n".join(
        '<figure><a href="previews/{0}"><img src="previews/{0}" alt="{1}"></a><figcaption>{1}</figcaption></figure>'.format(row["file"], row["label"])
        for row in previews
    )
    html = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TASK-0007 Facial Visual Review</title><style>
:root{color-scheme:dark;font-family:Inter,system-ui,sans-serif;background:#101916;color:#eaf6f0}body{margin:0}main{width:min(1480px,calc(100% - 32px));margin:auto;padding:36px 0 64px}h1,h2{margin:.2em 0}.warning{display:inline-block;padding:8px 12px;border:1px solid #d99a47;border-radius:9px;color:#ffd69a;background:#332715}.lead{max-width:900px;color:#b9cec7}.videos,.sheets{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:20px}video,img{display:block;width:100%;border-radius:12px;background:#16231f}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}figure{margin:0;padding:10px;border:1px solid #334b43;border-radius:14px;background:#16231f}figcaption{padding:8px 2px 2px;color:#b9cec7}.note{padding:16px;border-left:4px solid #66b9a0;background:#16231f}a{color:#8fe0c7}section{margin-top:34px}</style></head><body><main>
<p>TASK-0007 · OWNER VISUAL REVIEW</p><h1>Facial &amp; Hand–Face Technical Demo</h1>
<p class="warning">TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE</p>
<p class="lead">Mở hai video trước, sau đó xem contact sheet để so sánh. Toàn bộ hình ảnh được render tự động từ TASK-0006 facial candidate; không phải nội dung bài học đã duyệt.</p>
<section><h2>1. Demo videos</h2><div class="videos">
<figure><video controls preload="metadata" src="facial-expressions-demo.mp4"></video><figcaption>Facial expressions demo</figcaption></figure>
<figure><video controls preload="metadata" src="hand-face-integration-demo.mp4"></video><figcaption>TECH_HAND_FACE_TEST integration demo</figcaption></figure>
</div></section>
<section><h2>2. Contact sheets</h2><div class="sheets">
<figure><a href="facial-contact-sheet.png"><img src="facial-contact-sheet.png" alt="Facial contact sheet"></a><figcaption>20-state facial comparison</figcaption></figure>
<figure><a href="eye-gaze-contact-sheet.png"><img src="eye-gaze-contact-sheet.png" alt="Eye gaze contact sheet"></a><figcaption>Center / left / right / up / down</figcaption></figure>
</div></section>
<section><h2>3. Individual previews</h2><div class="grid">__PREVIEW_CARDS__</div></section>
<section class="note"><h2>Known limitations</h2><ul><li>Blink dùng companion eye morph vì eyelid topology còn hạn chế.</li><li>Brow và lip deformation còn nhẹ, chưa được subjective polish.</li><li>Visible eye depth/scale vẫn cần owner review từ front, three-quarter và side.</li><li>Owner acceptance và linguistic validity: NOT YET TESTED.</li></ul><p>Xem <a href="owner-acceptance-checklist.md">owner checklist</a> và report TASK-0007 để ghi quyết định.</p></section>
</main></body></html>""".replace("__PREVIEW_CARDS__", cards)
    path = output_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return {"file": path.name, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def write_owner_checklist(output_dir):
    text = """# Owner Acceptance Checklist — TASK-0007

Mở theo thứ tự:

1. `facial-expressions-demo.mp4`
2. `hand-face-integration-demo.mp4`
3. `facial-contact-sheet.png`
4. `eye-gaze-contact-sheet.png`
5. `index.html` nếu muốn duyệt toàn bộ trong một trang

## Checklist

- [ ] Neutral front/three-quarter/side phù hợp cho prototype giáo dục.
- [ ] Eye depth, scale và material chấp nhận được; không thấy floating/intersection nghiêm trọng.
- [ ] Center/left/right/up/down gaze đọc được và không quá mức.
- [ ] Left/right/both blink đọc được; limitation companion morph được chấp nhận tạm thời.
- [ ] Left/right/both brow raise đọc được dù deformation còn nhẹ.
- [ ] Lips round/spread và jaw open phân biệt được.
- [ ] Head/neck movement không làm whole character xoay ngoài ý muốn.
- [ ] `TECH_HAND_FACE_TEST` cho thấy tay, mắt, hàm, đầu/cổ và facial weight cùng hoạt động.
- [ ] Chấp nhận candidate tạm thời cho bước polish tiếp theo.
- [ ] Không coi technical demo là Vietnamese Sign Language đã xác minh.

Owner decision: **NOT YET TESTED**

Không cần mở Blender để hoàn thành checklist này.
"""
    path = output_dir / "owner-acceptance-checklist.md"
    path.write_text(text, encoding="utf-8")
    return {"file": path.name, "sha256": sha256(path), "size_bytes": path.stat().st_size}


def main():
    args = arguments()
    require(bpy.app.version_string.startswith(args.expected_version), "Expected Blender %s, got %s" % (args.expected_version, bpy.app.version_string))
    source_path = Path(bpy.data.filepath).resolve()
    require(sha256(source_path) == CANDIDATE_SHA256, "Facial candidate hash mismatch")
    root = Path(__file__).resolve().parents[2]
    canonical = root / "blender" / "master" / "avatar_master.blend"
    require(sha256(canonical) == CANONICAL_SHA256, "Canonical master hash mismatch")
    output_dir = Path(args.output_directory).resolve()
    review_blend = Path(args.review_blend).resolve()
    require(output_dir != source_path.parent and review_blend != source_path, "Review output must be separate from candidate")
    preview_dir = output_dir / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)

    body = bpy.data.objects.get("Human")
    armature = bpy.data.objects.get("Human.rig")
    require(body is not None and armature is not None, "Human/Human.rig missing")
    require(len(armature.data.bones) == 137, "Expected 137 bones")
    require(body.data.shape_keys is not None and all(name in body.data.shape_keys.key_blocks for name in TARGETS), "Required NMM targets missing")
    require(all(bpy.data.objects.get(name) is not None for name in EYE_OBJECTS), "Eye geometry missing")
    require(all(bpy.data.actions.get(name) is not None for name in CLIPS), "Required clips missing")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    require(ffmpeg is not None and ffprobe is not None, "FFmpeg/ffprobe not available")

    scene, camera, label, plaque = setup_scene(body)
    definitions = [
        ("01-neutral-front.png", "neutral", "NEUTRAL · FRONT", "front"),
        ("02-neutral-three-quarter.png", "neutral", "NEUTRAL · THREE-QUARTER", "three-quarter"),
        ("03-neutral-side.png", "neutral", "NEUTRAL · SIDE", "side"),
        ("04-brow-left.png", "brow-left", "BROW RAISE · LEFT", "front"),
        ("05-brow-right.png", "brow-right", "BROW RAISE · RIGHT", "front"),
        ("06-brow-both.png", "brow-both", "BROW RAISE · BOTH", "front"),
        ("07-blink-left.png", "blink-left", "EYE BLINK · LEFT", "front"),
        ("08-blink-right.png", "blink-right", "EYE BLINK · RIGHT", "front"),
        ("09-blink-both.png", "blink-both", "EYE BLINK · BOTH", "front"),
        ("10-lips-round.png", "lips-round", "LIPS · ROUND", "front"),
        ("11-lips-spread.png", "lips-spread", "LIPS · SPREAD", "front"),
        ("12-gaze-center.png", "gaze-center", "GAZE · CENTER", "front"),
        ("13-gaze-left.png", "gaze-left", "GAZE · LEFT", "front"),
        ("14-gaze-right.png", "gaze-right", "GAZE · RIGHT", "front"),
        ("15-gaze-up.png", "gaze-up", "GAZE · UP", "front"),
        ("16-gaze-down.png", "gaze-down", "GAZE · DOWN", "front"),
        ("17-jaw-open.png", "jaw-open", "JAW · OPEN", "front"),
        ("18-head-rotation.png", "head-rotation", "HEAD · ROTATION", "front"),
        ("19-neck-movement.png", "neck-movement", "NECK · MOVEMENT", "front"),
        ("20-combined-facial-expression.png", "combined", "COMBINED FACIAL EXPRESSION", "front"),
    ]
    previews = [render_still(scene, camera, label, body, armature, preview_dir / filename, state, title, ffmpeg, preset) for filename, state, title, preset in definitions]
    contact = create_contact_sheet([preview_dir / row[0] for row in definitions], output_dir / "facial-contact-sheet.png", columns=4, thumb_size=360)
    gaze_names = ["12-gaze-center.png", "13-gaze-left.png", "14-gaze-right.png", "15-gaze-up.png", "16-gaze-down.png"]
    gaze_contact = create_contact_sheet([preview_dir / name for name in gaze_names], output_dir / "eye-gaze-contact-sheet.png", columns=5, thumb_size=320)

    facial_video = output_dir / "facial-expressions-demo.mp4"
    facial_command = make_facial_video(ffmpeg, preview_dir, facial_video)
    frame_dir = output_dir / "_hand_face_frames"
    combined_frames = render_combined_frames(scene, camera, label, body, armature, frame_dir)
    combined_video = output_dir / "hand-face-integration-demo.mp4"
    combined_command = make_combined_video(ffmpeg, frame_dir, combined_video)

    reset_state(scene, body, armature)
    camera_preset(camera, body, "front")
    label.data.body = "TASK-0007 · AUTOMATED REVIEW SCENE"
    review_blend.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(review_blend), check_existing=False)

    videos = [probe_video(ffprobe, facial_video), probe_video(ffprobe, combined_video)]
    gallery = write_gallery(output_dir, previews, [contact, gaze_contact], videos)
    checklist = write_owner_checklist(output_dir)
    shutil.rmtree(frame_dir)

    checks = [
        {"id": "canonical_hash", "status": "PASS", "actual": sha256(canonical)},
        {"id": "candidate_hash", "status": "PASS", "actual": CANDIDATE_SHA256},
        {"id": "required_objects", "status": "PASS", "actual": {"body": body.name, "armature": armature.name, "eyes": list(EYE_OBJECTS)}},
        {"id": "required_targets", "status": "PASS", "actual": list(TARGETS)},
        {"id": "required_clips", "status": "PASS", "actual": list(CLIPS)},
        {"id": "preview_count", "status": "PASS" if len(previews) == 20 else "FAIL", "actual": len(previews)},
        {"id": "contact_sheets", "status": "PASS" if all((output_dir / name).exists() for name in ("facial-contact-sheet.png", "eye-gaze-contact-sheet.png")) else "FAIL", "actual": [contact, gaze_contact]},
        {"id": "videos", "status": "PASS" if all(row["codec"] == "h264" and row["duration_seconds"] > 0 for row in videos) else "FAIL", "actual": videos},
        {"id": "review_scene_separate", "status": "PASS" if review_blend != source_path else "FAIL", "actual": str(review_blend)},
        {"id": "html_gallery", "status": "PASS" if (output_dir / "index.html").exists() else "FAIL", "actual": gallery},
    ]
    result = {
        "schema_version": 1,
        "artifact": "task0007_automated_facial_visual_review",
        "technical_fixture_only": True,
        "owner_acceptance": "NOT YET TESTED",
        "linguistic_validity": "NOT YET TESTED",
        "blender_version": bpy.app.version_string,
        "source": {"candidate": str(source_path), "candidate_sha256": CANDIDATE_SHA256, "canonical_sha256": CANONICAL_SHA256},
        "review_scene": {"path": str(review_blend), "sha256": sha256(review_blend), "size_bytes": review_blend.stat().st_size},
        "previews": previews,
        "contact_sheets": [contact, gaze_contact],
        "videos": videos,
        "gallery": gallery,
        "owner_checklist": checklist,
        "ffmpeg": {"path": ffmpeg, "facial_demo": facial_command, "combined_demo": combined_command},
        "combined_frames_rendered": len(combined_frames),
        "temporary_frame_sequence_removed": not frame_dir.exists(),
        "checks": checks,
        "status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
    }
    report_path = output_dir / "automated-visual-qa.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("[%s] TASK-0007 visual review: %s" % (result["status"], output_dir))
    print("Previews: %d; videos: %d; review scene: %s" % (len(previews), len(videos), review_blend))
    if result["status"] != "PASS":
        raise RuntimeError("TASK-0007 automated visual review checks failed")


if __name__ == "__main__":
    main()
