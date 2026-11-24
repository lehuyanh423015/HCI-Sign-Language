# TASK-0011A — Phân tích tham chiếu và bản dựng có kiểm soát S001 “Xin chào”

- Ngày/Timezone: 2026-11-23, Asia/Saigon
- Branch: `feat/task-0011a-s001-xin-chao`
- Base commit: `54a1cc376764495e633c3eca85ce5c8fecf90a26` (`docs: record TASK-0010 publication`)
- Active worktree: `E:\University\Semester_7\HCI\BTL-worktrees\TASK-0011A`
- Scope: chỉ S001 “Xin chào”, biến thể Hà Nội; phân tích nguồn, motion spec, technical draft, GLB và local Three.js staging
- Overall status: **PASS cho technical draft; owner visual acceptance NOT YET TESTED; linguistic review NOT YET TESTED; WAITING_FOR_OWNER_REVIEW**

## 1. Executive summary

Video cục bộ do chủ dự án cung cấp đủ rõ để nhận diện cấu trúc chuyển động chính và tạo một **technical draft có kiểm soát**, nhưng không đủ để tự cấp phê duyệt ngôn ngữ. Quyết định chính thức:

`SUFFICIENT_FOR_TECHNICAL_DRAFT_NOT_LINGUISTIC_APPROVAL`

Đã tạo `S001_MAIN` dài 60 frame/2 giây ở 30 FPS, working `.blend`, GLB staging, preview MP4, contact sheet và route Three.js cục bộ. Draft được gắn nhãn `SIGN_PRODUCTION_CANDIDATE_TECHNICAL_DRAFT`; technical owner review và linguistic review đều còn `NOT YET TESTED`. Không đưa asset vào catalog bài học đã duyệt.

## 2. Initial repository status và bảo toàn user changes

Worktree chính `E:\University\Semester_7\HCI\BTL` có thay đổi người dùng không liên quan tại thời điểm bắt đầu:

- `README.md`
- `blender/master/avatar_master_neutral_candidate.blend`
- `docs/reports/artifacts/TASK-0004-browser-runtime.json`
- `docs/reports/artifacts/TASK-0004-browser-runtime.png`
- `docs/reports/_local-review/` chưa track
- `video/` chưa track, chứa `xin_chao.mp4`

Không reset, clean, stash, overwrite, stage hoặc commit các thay đổi này. TASK-0011A dùng external sibling worktree nêu trên. Không tạo worktree trong `node_modules`, `dist`, `build` hoặc thư mục generated khác.

Base được chọn từ local TASK-0010 commit `54a1cc376764495e633c3eca85ce5c8fecf90a26` vì đó là phiên bản có pose-authoring pipeline cần tái sử dụng. Remote vẫn là `https://github.com/lehuyanh423015/HCI-Sign-Language.git`; không có remote-tracking branch `origin/feat/task-0011a-s001-xin-chao` trong local refs khi kiểm tra.

## 3. Environment và dependency

| Thành phần | Phiên bản/trạng thái |
|---|---|
| Blender | `5.2.4 LTS`, build 2026-11-10 |
| MPFB baseline | `2.0.18` |
| Master Avatar | `1.0.0` |
| Node.js | `v24.14.1` |
| npm | `11.12.1` |
| Git | `2.45.1.windows.1` |
| Web stack | React 19.3.1, Three.js 0.187.0, Vite 8.3.8 |

Canonical master `blender/master/avatar_master.blend` giữ nguyên:

- Size: 2,393,258 bytes
- SHA-256: `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC`
- Rig validation: 137 bones, hierarchy/binding canonical, đủ sáu core NMM targets

## 4. Source reference và kết quả access/extraction

- Nguồn do owner chỉ định: `https://www.youtube.com/watch?v=4avGnxaLmb0`
- Timestamp nguồn: `00:04–00:08`
- File owner cung cấp: `E:\University\Semester_7\HCI\BTL\video\xin_chao.mp4`
- Quyền dùng: owner xác nhận dùng cho internal production workflow
- Bản lưu repository: `blender/working/signs/S001/references/xin_chao-owner-provided.mp4`
- SHA-256: `5A84E354C54EBD8446032ACC4C62FD9098E67063DFDAA76EE83B36D11A9100FB`
- Media: H.264, 2560×1440, 60 FPS, duration 5.760 giây, 5,602,484 bytes

Clip cục bộ đã là đoạn S001 độc lập và chứa hai lượt thực hiện:

- Take 1: xấp xỉ local `00:00.35–00:02.00`
- Take 2: xấp xỉ local `00:03.05–00:05.00`, được chọn để authoring

Bản cắt Take 2:

- `blender/working/signs/S001/references/s001-take2-analysis-03.05-05.00.mp4`
- SHA-256: `43FE1A0F6466BDE5CFE1F9F8B14030197F82C0E2AFFBFD7555B67F462385EE3D`

Không tải video thay thế và không phân tích S002/S003.

## 5. Phân tích chuyển động S001

| Hạng mục | Kết quả | Mức tin cậy |
|---|---|---|
| Hướng performer | Chính diện camera | OBSERVED |
| Tay chủ đạo | Hai tay hoạt động gần đối xứng | OBSERVED; metadata dùng `BOTH` |
| Pose đầu | Hai tay thấp ở vùng thân dưới/trước bụng | OBSERVED |
| Handshape | Hai bàn tay mở, năm ngón duỗi và xòe, ngón cái dạng | OBSERVED |
| Palm orientation | Lòng bàn tay nhìn rộng về phía camera ở vùng ký hiệu chính | OBSERVED từ góc chính diện |
| Arm/elbow | Hai tay nâng ra ngoài; khuỷu thấp hơn bàn tay; bàn tay lên cạnh vai/mặt | OBSERVED |
| Motion path | Từ thấp đi ra ngoài và lên trên, giữ vùng cạnh vai/mặt, sau đó hạ về | OBSERVED |
| Repetition | Có dao động/đổi tilt hai cổ tay-bàn tay qua lại | OBSERVED; exact linguistic cycle count NEEDS_CONFIRMATION |
| Contact | Không thấy tiếp xúc cơ thể | OBSERVED |
| Speed | Nâng tương đối nhanh, dao động đều, recovery xuống | OBSERVED |
| Head/gaze | Đầu nhìn chung thẳng, gaze về camera | OBSERVED |
| Face/NMM | Có nụ cười và khẩu hình giống lời nói | OBSERVED; chức năng ngôn ngữ UNKNOWN |

Chi tiết đã tách rõ trong `reference-analysis.json` và `reference-analysis.md` thành `OBSERVED`, `INFERRED`, `UNKNOWN`, `NEEDS_CONFIRMATION`; không chuyển giả định Euler kỹ thuật thành khẳng định ngôn ngữ.

## 6. Key pose analysis

Take 2 được ánh xạ sang draft 60 frame:

| Frame | Nhãn | Ý nghĩa kỹ thuật |
|---:|---|---|
| 1 | `neutral_pre_sign` | neutral kỹ thuật trước vùng có nghĩa |
| 8 | `bilateral_outward_lift` | hai tay bắt đầu đi ra ngoài/lên |
| 15 | `initial_open_raised` | hai tay mở ở vùng vai/mặt |
| 21 | `wrist_oscillation_a` | tilt A |
| 27 | `wrist_oscillation_b` | tilt B |
| 33 | `wrist_oscillation_a2` | tilt A lặp |
| 39 | `wrist_oscillation_b2` | tilt B lặp |
| 45 | `final_open_raised` | kết thúc vùng có nghĩa, vẫn mở |
| 60 | `neutral_recovery` | recovery kỹ thuật |

Iteration trực quan đầu phát hiện tay dang ngang/quá thấp. Calibration rig xác định local lower-arm Z cho gập khuỷu và wrist Y cho xoắn lòng bàn tay. Vòng 3 đưa khuỷu thấp hơn tay, bàn tay lên cạnh vai/mặt và lòng bàn tay hướng camera. Các góc Euler vẫn được ghi là `ASSUMED_TECHNICAL` vì nguồn chỉ có một camera chính diện.

## 7. Sufficiency decision và thông tin còn thiếu

Reference đủ cho technical draft vì nhìn thấy rõ bilateral handshape mở, vùng không gian ký hiệu, đường nâng/hạ, dao động và không có body contact. Reference **không đủ cho linguistic approval** vì còn các điểm sau:

- exact 3D depth và local Euler của vai/khuỷu/cổ tay;
- exact linguistic repetition count;
- chi tiết khớp ngón ở motion blur nhanh;
- vai trò từ vựng/ngữ pháp của nụ cười và khẩu hình;
- xác nhận từ reviewer có chuyên môn cho biến thể Hà Nội.

Do đó không đánh dấu `APPROVED`, không ghi linguistic `PASS`, không đưa vào lesson catalog.

## 8. Motion specification và draft animation

Motion spec: `blender/animation-specs/S001_MAIN.json`.

- Classification: `SIGN_PRODUCTION_CANDIDATE`
- Sign/label/variant: `S001` / `Xin chào` / `Hà Nội`
- Action: `S001_MAIN`
- FPS/frame range: 30 FPS, frame 1–60
- Meaningful interval: frame 8–45
- Key poses: 9
- Interpolation: BEZIER
- NMM authored: không; sáu core target được giữ neutral
- Reference status: `REFERENCE_READY`
- Technical status: `NOT YET TESTED` cho owner acceptance
- Linguistic status: `NOT YET TESTED`

Blender outputs:

- Base: `blender/working/signs/S001/S001_base.blend`, SHA-256 `B69B3435819C327AECEA3F72EA8503EEAD6C783674E813C095C4562E2D51D135`
- Final technical draft: `blender/working/signs/S001/S001.blend`, SHA-256 `207CE81CC6A6CDFA66E37B41899F530F1CE625388450D80FEA49F545FBA0A5D7`
- Action build: 117 bone curves, 6 morph curves
- Source validation: PASS cho Blender/master/sign ID/rig/bindings/FPS/timeline/neutral/action/range; linguistic `NOT YET TESTED`

GLB staging:

- `assets/exports/signs/S001.glb`
- Size: 2,338,800 bytes
- SHA-256: `7EC4FEB67058E6EAA37147F27BF74F222B82FD94B6254B126995D6A5604271B3`
- glTF 2.0, 9+ meshes, 1 skin, 137 joints, đúng một clip `S001_MAIN`, positive duration
- Bilateral arm/wrist nodes và sáu NMM targets tồn tại
- Khronos glTF Validator: 0 errors

Blender exporter có warning source vertices >4 joint influences và tự giữ bốn weight cao nhất/normalize. GLB validator vẫn PASS; cần owner quan sát deformation.

## 9. Local Three.js staging

Route `/technical-sign-preview` được chuyển sang asset `s001-xin-chao-technical-draft.glb`, clip `S001_MAIN` và hiển thị rõ:

- `TECHNICAL DRAFT — NOT LINGUISTICALLY APPROVED`
- `Technical: NOT YET TESTED — owner review required`
- `Linguistic: NOT YET TESTED`
- `Publication: LOCAL STAGING ONLY`

Asset không được thêm vào catalog bài học. Browser automation PASS cho GLB/canvas ready, animation progresses, pause/resume/replay, loop, speed và camera controls; runtime screenshot đã được kiểm tra trực quan.

## 10. Files created/modified chính

- `blender/working/signs/S001/reference-analysis.{md,json}`
- `blender/working/signs/S001/references/*.mp4`
- `blender/animation-specs/S001_MAIN.json`
- `blender/working/signs/S001/S001_base.blend`
- `blender/working/signs/S001/S001.blend`
- `blender/working/signs/S001/sign.json`
- `assets/exports/signs/S001.glb`
- `tools/validate-sign-draft.mjs`
- `blender/scripts/generate_pose_authoring_review.py` được parameterize, giữ defaults TASK-0010
- `docs/contracts/sign-motion-spec.schema.json` thêm optional label/variant/timestamp, backward-compatible
- Three.js staging page/test, technical asset sync và package command
- `docs/reports/artifacts/TASK-0011A/` chứa reference, draft và browser evidence

## 11. Commands actually executed

Các lệnh chính đã chạy thực tế, rút gọn đường dẫn tuyệt đối nhưng không thay đổi outcome:

```text
git status --short
git branch --show-current
git rev-parse HEAD
Get-FileHash -Algorithm SHA256 blender/master/avatar_master.blend
ffprobe ... video/xin_chao.mp4
ffmpeg ... reference frames/contact sheets/take2 clip

node tools/validate-sign-motion-spec.mjs --spec blender/animation-specs/S001_MAIN.json ...
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background ... --python blender/scripts/create_sign_working_copy.py -- ...
"...\blender.exe" --background S001_base.blend --python blender/scripts/build_sign_animation.py -- ...
"...\blender.exe" --background S001.blend --python blender/scripts/validate_sign_animation.py -- ...
"...\blender.exe" --background S001.blend --python blender/scripts/export_sign_animation.py -- --clip S001_MAIN ...
node tools/validate-sign-draft.mjs --sign-id S001 --clip S001_MAIN ...
"...\blender.exe" --background S001.blend --python blender/scripts/generate_pose_authoring_review.py -- ...

npm run sync:technical-assets
npm run sync:technical-assets:check
npm run validate:sign-packages
npm run test --workspace @hci-sign/web
npm run typecheck
npm run lint
npm run build
npm run test:sign-preview
npm run check
git diff --check
```

Các lượt không thành công đã được ghi nhận, không gọi PASS:

- gọi sai tên `validate-motion-spec.mjs`: FAIL do file không tồn tại; chạy lại đúng `validate-sign-motion-spec.mjs` PASS;
- motion spec vòng 2 có góc lower-arm 92/95 vượt schema ±90: FAIL; clamp về ±90 và validation PASS;
- React static markup test đầu thiếu visible asset filename: 1 FAIL/4 PASS; thêm trường Asset và chạy lại 5/5 PASS;
- draft visual vòng 1 không đạt nội bộ vì tay dang ngang/quá thấp; vòng 2 sửa arm location, vòng 3 sửa palm orientation và được chọn làm final technical draft.

## 12. Test/validation matrix

| Check | Evidence | Status |
|---|---|---|
| Canonical Master hash | SHA-256 nêu trên, `npm run verify:master` | PASS |
| Reference access/provenance/permission | local owner clip + task authorization | PASS |
| S001 segment isolation | Take 2 clip và ffprobe | PASS |
| Reference/key-pose visual package | annotated/contact/close-up sheets inspected | PASS |
| Motion spec schema/semantic checks | `motion-spec-validation.json` (final v3 result) | PASS |
| Blender 5.2.4 build | `animation-build.json` (final v3 result) | PASS |
| Blender source contract | `blender-validation.json` (final v3 result) | PASS |
| GLB/Khronos | `glb-validation.json` | PASS |
| Preview MP4 generation | `draft-visual-review-v3.json` | PASS |
| MP4 codec/frame/duration | H.264, 640×640, 30 FPS, 60 frames, 2.000s | PASS |
| Technical draft internal visual sanity | final contact sheet/hand close-ups inspected | PASS |
| Owner visual/anatomical/timing acceptance | checklist bên dưới | NOT YET TESTED |
| Qualified linguistic review | chưa có reviewer evidence | NOT YET TESTED |
| Three.js runtime | `sign-preview-browser.json` + screenshot | PASS |
| React tests | 5/5 | PASS |
| Node tests | 7/7 trong `npm run check` | PASS |
| Typecheck/lint/build/full project check | `npm run check` | PASS |
| S002/S003 work | ngoài scope | SKIPPED |
| Push/PR/merge | bị policy cấm | SKIPPED |

## 13. Evidence và hashes chính

| Artifact | SHA-256 |
|---|---|
| `reference-analysis/s001-annotated-key-pose-sheet.png` | `E23D4908FC0B4813D34356DB4856ACF149EC1FBEA07DAEE98DF45822506BD602` |
| `reference-analysis/s001-hand-closeup-sheet.png` | `4EF874AD2557C021247367130981EF8ADFA989E1F923FAC41CADCA2711768654` |
| `draft-visual-review-v3/key-pose-contact-sheet.png` | `6FFE6F7A92FC8B64B0070F5F51FBEC63E4AA7B1D5E99386142738C89383A623F` |
| `draft-visual-review-v3/s001-main-technical-draft-v3.mp4` | `9AF43F2F84CCA82C534C3D4BF36E9BBB23F074586BEEF2E0595E966623A8ECFE` |
| `sign-preview-browser.png` | `DD279CA8B48E6F5BEEC3494033421C25E5F179F043A4A0EFECFB20AC25ED6056` |

Visual artifact root: `E:\University\Semester_7\HCI\BTL-worktrees\TASK-0011A\docs\reports\artifacts\TASK-0011A`.

## 14. Known issues và limitations

- Chỉ có một góc quay chính diện; depth/Euler là technical approximation.
- Draft giữ mặt/NMM neutral dù nguồn có nụ cười/khẩu hình; không suy diễn chức năng ngôn ngữ.
- Vị trí tay/nhịp dao động cần owner và reviewer đánh giá trực tiếp; internal visual sanity không thay thế acceptance.
- Source master có warning >4 skin influences khi export; GLB/Khronos 0 error.
- Vite build PASS nhưng cảnh báo main chunk >500 kB; code splitting ngoài scope.
- Visual vòng 1/vòng 2 đã được dùng để chẩn đoán rồi loại khỏi package; fixture calibration tạm và binary iteration dư thừa cũng đã xóa sau khi final draft được chốt. Final v3 và reference evidence vẫn được giữ đầy đủ.

## 15. Git branch, commit và publication state

- Branch thực tế: `feat/task-0011a-s001-xin-chao`
- Base/HEAD trước local task commit: `54a1cc376764495e633c3eca85ce5c8fecf90a26`
- Local implementation commit: `eef7bcbcb42efed8bbd0a9a48d0796a0c3c233d4` (`feat: add S001 Xin chao technical draft`).
- Report follow-up commit: hash thực tế được ghi trong final response vì commit không thể tự chứa hash của chính nó.
- Remote publication: **không thực hiện**.
- Pull Request: **không tạo**.
- Merge vào `main`: **không thực hiện**.
- Tag/release: **không thực hiện**.
- Force push/history rewrite: **không thực hiện**.

## 16. Outstanding blockers

Không có blocker kỹ thuật cho local draft. Hai gate còn mở:

1. Owner review về motion, anatomy, timing, camera và độ gần reference.
2. Qualified linguistic review cho S001 biến thể Hà Nội.

Task dừng ở `WAITING_FOR_OWNER_REVIEW` theo Gate A.

## 17. Owner manual acceptance checklist

- [ ] So sánh `reference-analysis/s001-annotated-key-pose-sheet.png` với `draft-visual-review-v3/key-pose-contact-sheet.png`.
- [ ] Xác nhận hai lòng bàn tay hướng trước, ngón mở/xòe và không severe clipping.
- [ ] Xem MP4 2 giây, xác nhận lift, số lần dao động và recovery chấp nhận được.
- [ ] Xem front/three-quarter/hand close-up, xác nhận vai–khuỷu–cổ tay không biến dạng nghiêm trọng.
- [ ] Mở `/technical-sign-preview`, thử play/pause/replay/loop/0.5×/camera.
- [ ] Xác nhận route vẫn là local technical staging và S001 chưa xuất hiện dưới dạng lesson được duyệt.
- [ ] Chỉ sau owner approval mới cho phép push riêng task này; merge cần một authorization tách biệt.

## 18. Next recommended task

Sau owner review, nếu cần, tạo một refinement task riêng cho timing/pose/NMM. Nếu owner chấp nhận local implementation, bước kế tiếp là Gate B: owner cấp quyền push rõ ràng cho đúng branch TASK-0011A. Không tự động push, tạo PR hoặc merge.

**WAITING_FOR_OWNER_REVIEW**
