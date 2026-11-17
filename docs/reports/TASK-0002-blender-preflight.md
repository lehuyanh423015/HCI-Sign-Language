# TASK-0002 — Blender Environment & MPFB Rig Preflight

- Ngày kiểm tra: 2026-11-17 (Asia/Saigon)
- Nhánh: `chore/task-0002-blender-preflight`
- Phạm vi: diagnostic/read-only; không save, không pose, không tạo animation
- Master candidate: `blender/avatar_master.blend`
- SHA-256 trước/sau: `E15142798E8C573AA80243DE6D6F24B48CC517BBC5DD410DC1262AD1432480FA` — **PASS, không đổi**

## 1. Kết luận

- **Project baseline Blender 4.5.16: FAIL/UNAVAILABLE.** Không tìm thấy executable hoặc profile 4.5 trên máy.
- **Diagnostic executable:** Blender 5.2.4 LTS chạy background/Python thành công, chỉ dùng read-only trên bản sao tạm. Không thay baseline và không được dùng để save master.
- **MPFB 5.2 profile: PASS.** MPFB 2.0.18 được cài, enabled và runtime initialization thành công. **MPFB 4.5 profile: NOT YET TESTED** vì profile/executable 4.5 không tồn tại.
- **Rig structure: PASS với cảnh báo.** Có một mesh và một armature liên kết đúng; 137 deform bones; hai tay có đủ 5 chuỗi ngón × 3 bones, rotation không lock và vertex weights thật.
- **Animation readiness: FAIL cần xử lý ở task sau.** Scene đang 24 FPS thay vì 30; armature object có rotation không identity; rig không có control bones/constraints/IK; controlled Pose Mode test chưa chạy.

Evidence JSON:

- [`artifacts/TASK-0002-environment.json`](artifacts/TASK-0002-environment.json)
- [`artifacts/TASK-0002-rig-inventory.json`](artifacts/TASK-0002-rig-inventory.json) — full 137-bone inventory, hierarchy, constraints, vertex groups và object data.

## 2. Environment discovery

Đã kiểm tra PATH, `BLENDER_EXECUTABLE`, legacy `BLENDER_PATH`, `.env*`, Program Files, LocalAppData, Downloads/Desktop/Documents, ổ E, Windows App Paths và Uninstall registry.

| Executable | Version thực tế | Background | `bpy` | Kết quả |
|---|---|---:|---:|---|
| `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` | Blender 5.2.4 LTS, hash `cd5dc428cce1` | PASS | PASS; embedded Python 3.13.13 | Chỉ diagnostic |
| Blender 4.5.16 | Không tìm thấy | SKIPPED | SKIPPED | **Critical blocker** |

5.2 được Windows registry ghi là installation duy nhất. Không có `blender` trên PATH. Không có biến executable được set trước task. `--version`, factory background Python và user-profile background Python đều exit 0.

### Baseline decision

Giữ **4.5.16** là production baseline vì contract/team đã chọn và owner nói đã từng dùng nó. Không silently đổi sang 5.2. Chọn 5.2 chỉ để đọc bản sao vì đây là executable duy nhất và nó load file thành công mà không save; environment preflight vẫn cố ý trả exit code 2 cho `blender_baseline` mismatch.

## 3. MPFB

| Thuộc tính | Bằng chứng | Trạng thái |
|---|---|---|
| Profile | `%APPDATA%\Blender Foundation\Blender\5.2` | PASS cho 5.2 |
| Module | `bl_ext.user_default.mpfb` | PASS |
| Version | 2.0.18 | PASS |
| Build info | 20261010 | PASS |
| Manifest minimum | Blender 4.2.0 | PASS về declared minimum |
| Activation | Có trong `bpy.context.preferences.addons` | PASS |
| Runtime | Log `MPFB initialization has finished` | PASS |
| MakeHuman user data link | Không có explicit path/auto-discovery | SKIPPED; không chặn đọc rig hiện tại |
| Profile 4.5 | Không có config/profile | NOT YET TESTED |

Declared minimum không thay thế kiểm thử thực tế 4.5. Cần mở đúng Blender 4.5.16, kiểm tra `Edit > Preferences > Get Extensions/Add-ons`, tìm MPFB 2.0.18, xác nhận enabled và chạy `inspect_environment.py`.

## 4. Scene, character và rig objects

- Scene: `Scene`, metric, frames 1–250, **24 FPS** (contract yêu cầu 30).
- Objects: `Human` (MESH) và `Human.rig` (ARMATURE); không có object khác.
- Mesh `Human`: 19,158 vertices, 37,364 edges, 18,486 polygons, 11 shape keys, 269 vertex groups.
- Mesh parent: `Human.rig`; Armature modifier target: `Human.rig`; vertex groups enabled, bone envelopes disabled. Association **PASS**.
- Armature `Human.rig`: 137 bones, tất cả `use_deform=true`; 0 non-deform/control candidates, 0 custom-shape controls, 0 pose constraints, 0 IK/Spline IK.
- Actions: 0. Task không tạo action/keyframe.
- Mesh object transform identity. Armature location/scale identity nhưng rotation Euler là `(-0.05504546, 0.00296584, -0.24486382)` rad, vi phạm contract identity transform và phải được điều tra—not apply/fix—ở TASK-0003.

## 5. Bone inventory và mapping

Full inventory 137 dòng gồm `name`, `parent`, `children`, deform flag, head/tail, locks, custom shape và constraints nằm trong JSON artifact.

### Upper limb candidates

| Vai trò | Left | Right | Ghi chú |
|---|---|---|---|
| Clavicle/shoulder | `clavicle.L`, `shoulder01.L` | `.R` equivalents | Deform bones, không phải dedicated control |
| Upper arm | `upperarm01.L`, `upperarm02.L` | `.R` equivalents | Chuỗi deform |
| Elbow/forearm | `lowerarm01.L`, `lowerarm02.L` | `.R` equivalents | Không có elbow control/pole/IK riêng |
| Wrist | `wrist.L` | `wrist.R` | Pose bone riêng, rotation unlocked, có weights |

### Finger mapping

Mapping được xác nhận bằng ba nguồn cùng khớp: hierarchy trong file, vertex groups thực tế và bảng MPFB OpenPose constants cục bộ (có nhãn Thumb/Index/Middle/Ring/Little).

| Ngón | Left chain | Right chain | Metacarpal |
|---|---|---|---|
| Thumb | `finger1-1.L → finger1-2.L → finger1-3.L` | `.R` | Không có metacarpal riêng; root trực tiếp từ wrist |
| Index | `finger2-1.L → finger2-2.L → finger2-3.L` | `.R` | `metacarpal1.L/.R` |
| Middle | `finger3-1.L → finger3-2.L → finger3-3.L` | `.R` | `metacarpal2.L/.R` |
| Ring | `finger4-1.L → finger4-2.L → finger4-3.L` | `.R` | `metacarpal3.L/.R` |
| Little | `finger5-1.L → finger5-2.L → finger5-3.L` | `.R` | `metacarpal4.L/.R` |

Mỗi bone ngón có nonzero weighted vertices (khoảng 115–252 vertices theo group), parent chain tách biệt, pose rotation không khóa và không có constraint liên kết. Vì vậy **independent controllability về cấu trúc: PASS**. Việc xoay từng bone có cho deformation đúng và gesture-friendly hay không vẫn **NOT YET TESTED**, vì task này không được thao tác rig.

## 6. Constraints và hạn chế

- Không có constraint hoặc IK nào để làm cả character xoay khi chọn một pose bone.
- Không có dedicated control rig: animator thao tác trực tiếp deform bones. Điều này vẫn cho phép pose, nhưng kém an toàn/tiện dụng và dễ chọn nhầm object/root.
- Hai segment upper/lower arm có thể cần quy ước bone nào animator được phép pose.
- Facial bones và 11 shape keys tồn tại nhưng facial sign capability chưa được kiểm tra.
- Scene 24 FPS và armature non-identity rotation là blocker trước export/animation contract.
- File load được bằng 5.2 không chứng minh save/export compatibility với 4.5.

## 7. Phân tích lỗi “nhấn R xoay toàn bộ nhân vật”

Saved-state evidence từ bản sao:

```text
mode = OBJECT
active_object = Human.rig
selected_objects = [Human.rig]
active_bone = null
```

| Giả thuyết | Kết luận | Bằng chứng |
|---|---|---|
| Object Mode thay vì Pose Mode | **CONFIRMED** | File mở ở `OBJECT`; `Human.rig` active |
| Armature object được chọn | **CONFIRMED** | selected object duy nhất là `Human.rig` |
| Parent-child propagation | **CONFIRMED mechanism** | `Human` parent + Armature modifier đều trỏ rig; xoay rig object kéo mesh |
| Root bone được chọn | Ruled out trong saved state | Không active bone; đang Object Mode |
| Nhiều bones được chọn | Ruled out trong saved state | Không ở Pose Mode/không active bone; 5.2 không expose old bone select flag trong Object Mode |
| IK/constraint kéo cả rig | Ruled out | 0 constraints, 0 IK |
| Rig không có finger bones | Ruled out | 30 finger bones + weights |
| Rig hoàn toàn phù hợp animation ký hiệu | Chưa xác nhận | Không có control rig; chưa controlled pose/deformation test |

Chẩn đoán rất phù hợp với hành vi báo cáo: trong Object Mode, `R` xoay armature object, không xoay finger pose bone. **Không tuyên bố đã sửa**, vì chưa chuyển mode/chọn bone/xoay/undo trong controlled test; thao tác đó thuộc TASK-0003.

## 8. Automation đã tạo

- `blender/scripts/inspect_environment.py`: Blender/Python/profile/repos/MPFB manifest, activation và runtime; JSON + human summary; critical mismatch trả exception.
- `blender/scripts/inspect_rig.py`: scene/object/mesh/modifier/vertex groups/full armature hierarchy/constraints/selection state; read-only fingerprint; JSON + summary.
- `blender/tests/test_preflight.py`: 4 Blender-side tests cho vocabulary, side parser, real inventory/read-only state và forbidden mutating calls.
- `tools/doctor.mjs`: hỗ trợ `BLENDER_EXECUTABLE`, `.env.local`, legacy fallback và install ngoài default path.

## 9. Commands thực sự đã chạy

```cmd
git switch -c chore/task-0002-blender-preflight
Get-FileHash blender\avatar_master.blend -Algorithm SHA256
where blender
REM Program Files, user folders, registry và Blender profile discovery
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --version
"...\blender.exe" --background --factory-startup --python-expr "...import bpy..."
"...\blender.exe" --background --python-expr "...preferences.addons..."
copy blender\avatar_master.blend %TEMP%\hci-task0002-preflight-20261117\avatar_master_preflight.blend
"...\blender.exe" --background --python-exit-code 2 --python blender\scripts\inspect_environment.py -- --output ... --expected-version 4.5.16 --require-mpfb
"...\blender.exe" %TEMP%\...\avatar_master_preflight.blend --background --python-exit-code 3 --python blender\scripts\inspect_rig.py -- --output ... --expected-version 4.5.16 --expected-fps 30
"...\blender.exe" %TEMP%\...\avatar_master_preflight.blend --background --python-exit-code 4 --python blender\tests\test_preflight.py -- --inspect-rig blender\scripts\inspect_rig.py
npm run doctor
npm run check
Get-FileHash blender\avatar_master.blend -Algorithm SHA256
```

Không chạy Blender save/export/install/enable operations. Không pip/npm dependency mới.

## 10. Test results

| Check | Kết quả |
|---|---|
| Blender 5.2 `--version` | PASS |
| Background launch | PASS |
| Embedded Python/`bpy` | PASS |
| MPFB 2.0.18 install/activation/runtime trong 5.2 | PASS |
| Project Blender 4.5.16 baseline | **FAIL**, environment script exit 2 |
| Temporary copy load | PASS |
| Mesh + armature + association | PASS |
| 10 numbered finger chains × 3 bones, unlocked | PASS structural |
| Semantic mapping source evidence | PASS |
| Controlled Pose Mode/deformation test | NOT YET TESTED |
| Scene FPS 30 | **FAIL**; actual 24 |
| Armature identity transforms | **FAIL**; nonzero rotation |
| Blender-side tests | PASS, 4/4 |
| Read-only state fingerprint | PASS |
| Original SHA-256 unchanged | PASS; trước/sau cùng `E151...0FA` |
| Temporary copy SHA-256 unchanged | PASS; khớp source gốc |
| `npm run check` | PASS; exit 0 |

Final verification cũng xác nhận: 0 actions, không rig hierarchy change, không source asset deletion, không dependency/lockfile change và không remote push. `README.md` có một thay đổi user-owned tồn tại trước task và không thuộc commit TASK-0002.

## 11. Remaining blockers

1. Khôi phục/xác định executable Blender 4.5.16 và xác minh MPFB trong đúng profile.
2. Controlled test trên disposable working copy: Pose Mode, chọn đúng `fingerN-M`, xoay nhỏ, quan sát deformation, undo; ghi screen evidence.
3. Quyết định cách chuẩn hóa 24 → 30 FPS và non-identity armature rotation mà không phá rig/skin; không apply transform mù quáng.
4. Đánh giá có cần thêm control rig/IK hay direct deform-bone posing đủ cho 6 signs.
5. Facial/hand visibility và GLB export/browser playback chưa kiểm tra.

## 12. TASK-0003 đề xuất

`Controlled pose and 3D-to-GLB smoke test`: chạy bằng Blender 4.5.16 đã xác minh; trên working copy, test từng wrist/finger chain ở Pose Mode với rotate nhỏ + undo, kiểm tra deformation/clipping; thống nhất FPS/transform repair plan; tạo **technical placeholder** action `S001_MAIN` không mang nội dung ký hiệu; export một self-contained GLB; validate clip/skin/skeleton và kiểm tra Three.js play/pause/replay/loop/speed/reset. Không sửa master trước khi review kết quả.
