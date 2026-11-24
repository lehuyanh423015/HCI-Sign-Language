# TASK-0011 — Bản nháp hoạt ảnh S004–S006 từ video tham chiếu

- Ngày/Timezone: 2026-11-22, Asia/Ho_Chi_Minh
- Branch/base commit: `feat/task-0011-mien-signs-s004-s006` từ `main` tại `b030fcd7d63ee564354ba3d5b20ed479dd2b4b39`
- Scope: dựng bản nháp kỹ thuật cho ba ký hiệu được giao cho Lê Quang Miền trên Master Avatar v1.0.0: S004 "giúp đỡ", S005 "yêu", S006 "ăn"
- Overall status: PARTIAL. Technical pipeline PASS; reference, technical review của 3D Lead và linguistic review chưa thực hiện

## Executive summary

Ba ký hiệu có Action `Snnn_MAIN`, `.blend` làm việc, GLB, ảnh khung hình chính, video góc thẳng và góc nghiêng, cùng evidence JSON. Cả ba qua `validate_sign_animation.py`, xuất GLB qua `export_sign_animation.py`, GLB qua Khronos validator với 0 lỗi và 0 cảnh báo, và phát được bằng `GLTFLoader` của three.js 0.187.

Chuyển động được dựng tự động từ điểm mốc MediaPipe Holistic của video từ điển QIPEDC, bằng script mới `blender/scripts/retarget_landmarks_to_sign.py`, thay cho keyframe tay từ tư thế trống. Ở bản 0.2.0-draft, hình dạng bốn ngón tay được đặt theo mẫu gập ngón, vì MediaPipe đoán thiếu độ gập khi ngón bị che: nắm tay cho S004 và S005, chụm ngón cho S006. Đây là **bản nháp kỹ thuật**, chưa phải Ngôn ngữ Ký hiệu Việt Nam đã xác minh. Trạng thái metadata giữ `REFERENCE_PENDING` vì quyền sử dụng video và việc chọn biến thể chưa được Thảo hoặc người thành thạo xác nhận.

## Initial repository status

- Clone mới từ `https://github.com/lehuyanh423015/HCI-Sign-Language.git`, `main` tại `b030fcd`, working tree sạch.
- `blender/master/avatar_master.blend` SHA-256 `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC`, khớp manifest.
- S004–S006 ở trạng thái `REFERENCE_PENDING`, toàn bộ trường reference và production là `null`.
- Nhánh `origin/feat/task-0010-first-sign-animation-pilot` có pipeline pose authoring theo motion spec nhưng chưa merge vào `main`; task này không dựa vào nhánh đó.

## Environment and dependencies

| Thành phần | Phiên bản | Ghi chú |
|---|---|---|
| Blender | 5.2.4 LTS, hash `cd5dc428cce1` | Bản zip chính thức, SHA-256 `bbd78f8931dc940444da4ff2983374930f9f5c092ae0e330588e9760bb9d967c` khớp tệp `.sha256` của blender.org; chạy từ thư mục ngoài repo |
| MPFB | Không cài | Các script dùng trong task không gọi MPFB; rig MPFB đã có sẵn trong Master |
| Node.js | 24.16.0 | `.nvmrc` yêu cầu 24.22.2; `npm ci` và các validator chạy bình thường |
| three.js | 0.187.0 | Từ `node_modules` sau `npm ci` |
| Trích điểm mốc | MediaPipe tasks-vision 1.2.3, HolisticLandmarker, chế độ VIDEO, GPU | Chạy bằng studio của dự án cá nhân `vsl-learn`, ngoài repo này; xem mục Known issues |
| Chrome | Bản cài trên máy, headless, GPU Intel UHD | Dùng cho trích điểm mốc và kiểm tra three.js |

## Implemented changes

1. **`blender/scripts/retarget_landmarks_to_sign.py`** mới. Đọc tệp `vsl-raw-landmarks` v1, chọn một đoạn thời gian, giải góc khớp trong không gian riêng của armature và ghi một Action có slot `OBJECT`:
   - Cánh tay: IK hai đoạn giữ **vị trí cổ tay** so với vai, quy đổi theo chiều dài tay của avatar; hướng gập khuỷu lấy từ video. Gần mặt, vị trí cổ tay được neo theo miệng avatar. Khi ảnh 2D cho thấy đầu ngón chạm miệng, cổ tay được đặt sao cho đầu ngón avatar chạm môi.
   - Cổ tay: khung lòng bàn tay từ cổ tay tới gốc ngón giữa và từ gốc ngón út tới gốc ngón trỏ; một nửa độ xoắn chuyển sang `lowerarm02` để giảm méo da.
   - Ngón: mỗi đốt quay từ hướng nghỉ đo trên rig tới hướng trong điểm mốc bàn tay.
   - Hình dạng tay: tham số `--handshape SIDE:SHAPE[:START:END]` thay hướng của bốn ngón trỏ, giữa, áp út, út bằng mẫu gập ngón trên một khoảng thời gian; hướng lòng bàn tay và ngón cái vẫn theo video. Ba mẫu kỹ thuật: `fist` gập 95/105/70 độ ở ba khớp, `flat` 4/4/2 độ, `bunched` 48/38/22 độ với các ngón kéo song song. Các mẫu này là khối dựng kỹ thuật, chưa phải bộ hình dạng tay VSL đã duyệt.
   - Đầu: từ điểm mốc khuôn mặt, hệ số 0,7. Cột sống và vai giữ nguyên.
   - Khung thiếu được nội suy; làm mượt cửa sổ tam giác bán kính 2.
   - Timeline: frame 1 neutral, 8 frame chuyển vào, đoạn video, rồi trở về neutral qua tư thế nghỉ đầu đoạn để tay không quét qua mặt.
   - Tham số `--depth-scale` và `--hand-depth-scale` nén độ sâu MediaPipe vốn hay bị phóng đại; giá trị dùng cho từng ký hiệu được ghi trong `evidence/retarget.json`.
   - Bảo vệ: kiểm tra Blender 5.2.4, `sign_id` và hash Master của working copy; từ chối ghi đè output hoặc Action đã có; so sánh `inventory()` trước và sau, chỉ cho phép thêm đúng một Action; kiểm tra frame 1 neutral.
2. **`blender/scripts/render_sign_review.py`** mới. Render Workbench góc thẳng và góc nghiêng theo hệ trục của `Human`, ghép bảng khung hình chính bằng numpy, và xuất MP4 H.264 bằng FFmpeg có sẵn trong Blender, không cần `ffmpeg.exe`. Tùy chọn `--focus-bone` đặt camera bám theo một xương để chụp cận bàn tay. Không lưu `.blend`.
3. Ba working copy tạo bằng `create_sign_working_copy.py`, ba `.blend` hoạt ảnh, ba GLB, preview và evidence.
4. `sign.json` của S004–S006: điền tên hiển thị, gloss, nguồn tham chiếu, đường dẫn sản xuất, ghi chú NMM; giữ `REFERENCE_PENDING`, mọi review `NOT YET TESTED`.

### Tham chiếu và đoạn sử dụng

| Sign | Từ | Video QIPEDC | Đoạn | Tham số | Mức chắc chắn |
|---|---|---|---|---|---|
| S004 | giúp đỡ | W01497B "giúp đỡ" | 0,15–2,20 giây | depth 0,5; hand depth 1,0; tay phải `fist` | Đúng từ; chưa xác nhận biến thể |
| S005 | yêu | W03373B "thương yêu" | 1,00–3,10 giây | depth 0,5; hand depth 1,0; hai tay `fist` | Gần nghĩa; cần chọn biến thể cho "yêu" |
| S006 | ăn | W00042 "ăn uống", phần đầu | 1,50–2,30 giây | depth 0,5; hand depth 0,3; lead-out 16; tay phải `bunched` | Một phần của từ ghép; "đồ ăn" D0444 có cùng động tác mở đầu |

Video lấy qua bản sao Hugging Face `Lakeserl/SignConnect`. Video và tệp điểm mốc **không** đưa vào repo vì chưa rõ quyền sử dụng.

## Created and modified files

- Mới: `blender/scripts/retarget_landmarks_to_sign.py`, `blender/scripts/render_sign_review.py`
- Mới, mỗi `Snnn` trong S004, S005, S006:
  - `blender/working/signs/Snnn/Snnn.blend`
  - `blender/working/signs/Snnn/evidence/{working-copy,retarget,blender-validation,glb-export}.json`
  - `blender/working/signs/Snnn/previews/{Snnn-key-poses.png,Snnn-front-side.mp4,review.json}`, cùng ảnh cận bàn tay `S004-hands.png`, `S005-hands-left.png`, `S005-hands-right.png`, `S006-hands.png`
  - `assets/exports/signs/Snnn.glb`
- Sửa: `blender/working/signs/S004/sign.json`, `S005/sign.json`, `S006/sign.json`
- Mới: `docs/reports/artifacts/TASK-0011/` gồm kết quả validator và kiểm tra three.js; báo cáo này
- Không đưa vào commit: `blender/working/signs/Snnn/Snnn_base.blend`, là working copy trung gian, tạo lại được bằng lệnh ở mục dưới

## Commands actually executed

Chạy từ root repo, `B` là đường dẫn `blender.exe` 5.2.4. `RAW` là thư mục chứa `Snnn.raw.json`.

```text
certutil -hashfile blender/master/avatar_master.blend SHA256
%B% -b blender/master/avatar_master.blend --python blender/scripts/create_sign_working_copy.py -- --sign-id S004 --output blender/working/signs/S004/S004_base.blend --report blender/working/signs/S004/evidence/working-copy.json
  (tương tự S005, S006)

# Trích điểm mốc, ngoài repo, bằng studio của vsl-learn:
npm run eval -w studio -- <thư mục chứa S004.mp4, S005.mp4, S006.mp4> <eval.json>   với RAW_DIR=<RAW>

%B% -b blender/working/signs/S004/S004_base.blend --python blender/scripts/retarget_landmarks_to_sign.py -- --raw %RAW%/S004.raw.json --sign-id S004 --start 0.15 --end 2.2 --handshape R:fist --output-blend blender/working/signs/S004/S004.blend --report blender/working/signs/S004/evidence/retarget.json
%B% -b blender/working/signs/S005/S005_base.blend --python blender/scripts/retarget_landmarks_to_sign.py -- --raw %RAW%/S005.raw.json --sign-id S005 --start 1.0 --end 3.1 --handshape L:fist --handshape R:fist --output-blend blender/working/signs/S005/S005.blend --report blender/working/signs/S005/evidence/retarget.json
%B% -b blender/working/signs/S006/S006_base.blend --python blender/scripts/retarget_landmarks_to_sign.py -- --raw %RAW%/S006.raw.json --sign-id S006 --start 1.5 --end 2.3 --hand-depth-scale 0.3 --lead-out 16 --handshape R:bunched --output-blend blender/working/signs/S006/S006.blend --report blender/working/signs/S006/evidence/retarget.json

%B% -b blender/working/signs/S004/S004.blend --python blender/scripts/validate_sign_animation.py -- --sign-id S004 --expected-clip S004_MAIN --output blender/working/signs/S004/evidence/blender-validation.json
%B% -b blender/working/signs/S004/S004.blend --python blender/scripts/export_sign_animation.py -- --clip S004_MAIN --output assets/exports/signs/S004.glb --report blender/working/signs/S004/evidence/glb-export.json
%B% -b blender/working/signs/S004/S004.blend --python blender/scripts/render_sign_review.py -- --output-directory blender/working/signs/S004/previews --resolution 360 480 --contact-sheet S004-key-poses.png --video S004-front-side.mp4 --frames 1 20 30 40 50 60 82
  (tương tự S005 với frames 1 15 25 35 45 55 65 84; S006 với frames 1 16 22 28 34 40 49)
%B% -b blender/working/signs/S004/S004.blend --python blender/scripts/render_sign_review.py -- --output-directory blender/working/signs/S004/previews --views front side --focus-bone finger3-1.R --focus-distance 0.5 --resolution 360 360 --contact-sheet S004-hands.png --frames 20 30 40 50
  (tương tự S005 với finger3-1.R và finger3-1.L, frames 25 35 45 55; S006 với finger3-1.R, frames 22 26 30 34)

npm ci
node tools/validate-sign-package.mjs --report docs/reports/artifacts/TASK-0011/sign-package-validation.json --pilot-glb assets/exports/technical/task-0009/technical-sign-pipeline-pilot.glb --pilot-clip TECH_HAND_FACE_TEST
node tools/validate-sign-package.mjs --report docs/reports/artifacts/TASK-0011/S004-glb-validation.json --pilot-glb assets/exports/signs/S004.glb --pilot-clip S004_MAIN
  (tương tự S005, S006)
npm run verify:master
```

Trong quá trình phát triển, script được chạy nhiều lần với các tham số khác vào thư mục tạm ngoài repo để so sánh với video; chỉ lần chạy cuối ở trên được ghi vào repo.

## Test matrix

| Check | Evidence | Status |
|---|---|---|
| Master hash và manifest | `npm run verify:master` | PASS |
| Working copy từ Master, frame 1 neutral | `evidence/working-copy.json` × 3 | PASS |
| Retarget không đổi rig, binding, geometry, transform, Morph Target; chỉ thêm một Action | `evidence/retarget.json` × 3, `rig_inventory_unchanged` | PASS |
| Blender 5.2.4, 137 bone, hierarchy, binding, 6 NMM, 30 FPS, timeline, neutral frame 1, Action `Snnn_MAIN` | `evidence/blender-validation.json` × 3 | PASS |
| Linguistic review trong validator | như trên | NOT YET TESTED |
| Xuất GLB | `evidence/glb-export.json` × 3 | PASS |
| glTF 2.0, mesh và skin, clip đúng tên, thời lượng dương, 6 NMM, Khronos 0 lỗi 0 cảnh báo | `artifacts/TASK-0011/Snnn-glb-validation.json` × 3 | PASS |
| Schema metadata S001–S006 và có đủ tệp sản xuất | `artifacts/TASK-0011/sign-package-validation.json` | PASS |
| Phát bằng three.js `GLTFLoader` và `AnimationMixer`, clip đúng, 411 track, 6 NMM, không lỗi trang | `artifacts/TASK-0011/threejs-playback.{json,jpg}` | PASS |
| Trang `/technical-sign-preview` của web | trang đang gắn cứng GLB pilot TASK-0009 | SKIPPED |
| So sánh bằng mắt với video tham chiếu | thực hiện ngoài repo vì ảnh có khung hình QIPEDC; kết luận ở mục Known issues | PASS cho vị trí và quỹ đạo chính; xem hạn chế |
| Technical review của 3D Lead | | NOT YET TESTED |
| Reference verification | | NOT YET TESTED |
| Linguistic review bởi người thành thạo | | NOT YET TESTED |

`npm run check` toàn bộ chưa chạy: SKIPPED. Task không sửa `apps/web`, `data/` hay schema.

## Evidence and generated artifacts

| Tệp | SHA-256 |
|---|---|
| `assets/exports/signs/S004.glb` | `8F96538EF1A419790F3E8F031A3E25029E2048FDD529B71A7320CD7F5238AA81` |
| `assets/exports/signs/S005.glb` | `E9ABBD8A5833E932C705EE664C0883C2787321A003F53FC60AC37EC0A1B78C13` |
| `assets/exports/signs/S006.glb` | `9B38DDD36FE293C9F2B863CAA6A7D4409ECCB2C86550CFCABE26D8E2571237B9` |
| `blender/working/signs/S004/S004.blend` | `ED52D776EF44EBF0DE09D8CEF584D676FEA98502AE5782E80D201F7FDD72E3C7` |
| `blender/working/signs/S005/S005.blend` | `61D021ED961B4E0875F5164A0274A022BAF56F870811BA885AF3299F6345C6D8` |
| `blender/working/signs/S006/S006.blend` | `1DDB272A8F089D491F7A74E6123C05C2A4D021B9D24B4DF07840FA25C84D9825` |
| Điểm mốc S004, ngoài repo | `F831DB5CE90B1E19F1802F6EFA4018861C7C1F9DAEE6815ECDC641AB84566D55` |
| Điểm mốc S005, ngoài repo | `8439F032FE0592F74AA858BD4F3068322C3805BBF62BE5DBC33EA45E86822E2A` |
| Điểm mốc S006, ngoài repo | `7917937C5DACF1FF3850769AE64416373CDBD078FD26C617855DCB331BB3AA7B` |

| Sign | Frame | Thời lượng | Bone có key |
|---|---|---|---|
| S004 | 1–82 | 2,73 giây | 39 |
| S005 | 1–84 | 2,80 giây | 39 |
| S006 | 1–49 | 1,63 giây | 22, chỉ tay phải làm ký hiệu |

## Known issues and limitations

1. **Hình dạng bàn tay đã sửa bằng mẫu, còn cần tinh chỉnh tay.** Bản 0.1.0-draft dựng theo điểm mốc chỉ gập ngón khoảng một nửa. Bản 0.2.0-draft dùng mẫu `fist` và `bunched`; so bằng ảnh cận thì gần video hơn rõ rệt. Còn lại:
   - S004: các ngón gập kín nhưng nhìn thẳng vẫn hơi chĩa ra trước, đốt gốc chưa vuông như nắm tay thật.
   - S006: các ngón đã chụm nhưng đầu ngón chạm cằm và môi dưới, thấp hơn video khoảng 1–2 cm; ngón cái vẫn theo điểm mốc nên chưa chạm hẳn các đầu ngón.
   - Mẫu gập ngón áp dụng cho cả đoạn ký hiệu, nên lúc tay đang đưa lên cũng đã nắm hoặc chụm.
2. **Chưa có biểu cảm.** S005 tham chiếu có nhắm mắt và nét mặt trìu mến; chưa dựng `NMM_` cho ký hiệu nào.
3. **Vị trí tay thấp hơn người ký một chút** ở S004 và S005, do tỷ lệ cơ thể của Master khác người trong video. S006 đã neo theo miệng nên chạm đúng.
4. **Độ sâu MediaPipe không đáng tin.** Phải nén độ sâu, và với S006 phải dùng tiếp xúc 2D để đặt tay lên miệng. Tham số chọn theo từng ký hiệu sau khi so với video, ghi trong `retarget.json`.
5. **Hai trong ba ký hiệu dùng video gần nghĩa:** "thương yêu" cho "yêu", phần đầu "ăn uống" cho "ăn".
6. **Công cụ trích điểm mốc nằm ngoài repo**, trong studio của dự án `vsl-learn`. Người khác chưa tự chạy lại được bước này; tệp điểm mốc cũng chưa được đưa vào repo vì chưa rõ quyền sử dụng.
7. **Quan sát về Master, không do task này gây ra:**
   - Object `Human.rig` có phép xoay khoảng 14° quanh trục đứng. Script tính trong không gian armature nên không bị ảnh hưởng, nhưng nhân vật hơi xoay trong viewer.
   - Áo bị hở ở vai khi tay giơ cao, thấy rõ trong preview.
   - Báo Huy Anh xem xét.
8. Báo cáo validator theo từng GLB dùng tham số `--pilot-glb`, nên trường `classification` trong các tệp `Snnn-glb-validation.json` ghi `TECHNICAL_FIXTURE_NOT_A_SIGN`. Nhãn này đến từ validator; các GLB là `SIGN_PRODUCTION_CANDIDATE` theo `glb-export.json`.
9. Node 24.16.0 khác `.nvmrc` 24.22.2.

## Git branch and commit information

- Branch: `feat/task-0011-mien-signs-s004-s006`, base `b030fcd7d63ee564354ba3d5b20ed479dd2b4b39`.
- Commit trên branch, **chưa push**:
  - `d8711b2` feat(blender): add landmark retarget and sign review rendering
  - `02f5bc8` feat(sign): add S004-S006 draft animations from reference video
  - `2886cb1` docs: record TASK-0011 sign drafts S004-S006
  - Commit cập nhật mục này được tạo sau, nên không tự ghi được hash của chính nó.
- `Snnn_base.blend` không đưa vào commit.

## Outstanding blockers

- Thảo xác nhận nguồn và quyền sử dụng video QIPEDC, chọn biến thể cho "yêu" và "ăn"; khi đó mới chuyển `REFERENCE_READY`.
- Chưa có người thành thạo để linguistic review.
- Trang xem trước web chỉ tải GLB pilot; cần Nhật cho phép chọn GLB ký hiệu nếu muốn browser review trong app.

## Owner manual acceptance checklist

- [ ] Xem `Snnn-front-side.mp4` và `Snnn-key-poses.png` của cả ba ký hiệu.
- [ ] Mở `Snnn.blend` trong Blender 5.2.4, phát `Snnn_MAIN`, xem cận hai bàn tay.
- [ ] Xem các ảnh cận `Snnn-hands*.png`; xác nhận nắm tay S004, S005 và bàn tay chụm S006 đạt hay cần tinh chỉnh.
- [ ] S004: chỉnh đốt gốc các ngón cho nắm tay vuông hơn nếu cần; kiểm tra tay trái ngửa phẳng.
- [ ] S006: nâng đầu ngón lên môi khoảng 1–2 cm, cho ngón cái chạm đầu ngón; quyết định có lặp động tác chạm miệng không.
- [ ] Quyết định có dựng biểu cảm cho S005 không.
- [ ] Xác nhận không có xuyên mesh hoặc méo da ở cổ tay và vai.
- [ ] Commit trên branch task khi đã hài lòng.

## Next recommended tasks

- Tinh chỉnh tay trong Blender theo checklist, rồi xuất lại GLB với `animation_version` mới.
- Đưa bước trích điểm mốc vào repo nhóm, nếu nhóm chấp nhận cách dựng từ video.
- Gửi preview cho người thành thạo khi có người kiểm chứng.

Không tự động bắt đầu task kế tiếp.
