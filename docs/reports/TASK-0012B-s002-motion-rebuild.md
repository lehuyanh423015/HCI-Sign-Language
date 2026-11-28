# TASK-0012B — S002 “Cảm ơn” Motion Rebuild

## 1. Trạng thái

- Kết quả kỹ thuật: **PASS**.
- Xác nhận ngôn ngữ học: **NOT YET TESTED**.
- Cổng quy trình: **WAITING_FOR_OWNER_REVIEW**.
- Không thực hiện `git add`, `git commit`, `git push`, PR, merge, rebase, reset hoặc clean.
- Source of truth là file báo cáo này trong worktree `active-3d`; bản dưới repository chính `_local-review/` chỉ dùng để owner đọc local và không được stage.

## 2. Phạm vi và đầu vào

- Worktree: `E:\University\Semester_7\HCI\BTL-worktrees\active-3d`.
- Nhánh: `feat/s002-cam-on`.
- HEAD nền: `be1062331cddd6b58dfbabe9abf8e453bbf07c00`.
- Tham chiếu riêng tư: `blender/working/signs/S002/references/cam_on-owner-provided.mp4`.
- SHA-256 tham chiếu: `AE763E5A7780C952396E2DF164BF5FD8DB7C1F6C1A27D54C1BF1B04B5041D807`.
- File tham chiếu được `.gitignore` bảo vệ và không nằm trong danh sách commit.

Hai lượt thực hiện được dùng đồng thời:

- Take 1: khoảng `00:01.40–00:02.55`.
- Take 2: khoảng `00:04.20–00:05.55`.

## 3. Phân tích tham chiếu

### OBSERVED — nhất quán ở cả hai take

- Hai tay hoạt động gần đối xứng.
- Bắt đầu ở vùng giữa/ngực trên; cẳng tay đi lên và vào trong.
- Hai bàn tay khép lỏng, đến vùng gần miệng/má dưới rồi mở dần.
- Pha giải phóng đi ra trước và xuống vùng thân trên; mỗi take chỉ có một lượt thực hiện.

### TAKE_VARIATION

- Take 2 có endpoint thấp hơn nhẹ và giữ lâu hơn take 1.

### UNKNOWN / NEEDS_CONFIRMATION

- Video chính diện không xác định chắc chắn độ sâu và pháp tuyến lòng bàn tay.
- Cấu hình ngón cái bị che một phần ở vùng gần mặt.
- Nụ cười, khẩu hình và nghiêng thân quan sát được chưa được chứng minh là NMM ngôn ngữ học.

Phân loại máy đọc được: `blender/working/signs/S002/evidence/reference-take-analysis-task0012b.json`.

## 4. Quyết định rebuild

Draft TASK-0012A bị loại khỏi chuỗi chuyển động chính vì đường tay rộng/thấp, không đưa cả hai tay đến vùng gần mặt và endpoint thiếu cân đối. TASK-0012B xây lại các nghiệm vai–cánh tay từ tham chiếu, không tinh chỉnh trực tiếp action bị loại.

Chuỗi mới gồm 9 pose, 66 frame ở 30 fps:

- Frame 1–6: thiết lập kỹ thuật.
- Frame 10: bắt đầu có nghĩa ở vùng giữa/ngực trên.
- Frame 17: cẳng tay nâng vào trong.
- Frame 23: landmark gần mặt với bàn tay khép lỏng.
- Frame 31: mở ngón dần khi đi ra trước/xuống.
- Frame 40: endpoint tay mở ở thân trên.
- Frame 50: giữ kỹ thuật; frame 66: hồi về neutral.

Mặt, đầu, hàm và sáu core NMM được giữ trung tính. Thành công kỹ thuật không đồng nghĩa S002 đã được chuyên gia xác nhận là Ngôn ngữ Ký hiệu Việt Nam.

## 4A. Revision theo owner ngày 2026-11-25

- Giữ nguyên `S002_MAIN`, rig Master Avatar v1, pipeline build/export/Three.js và cấu trúc 66 frame.
- Đưa hai tay hội tụ vào vùng miệng/má dưới tại frame 23; khuỷu tay vẫn gập và ở gần thân.
- Thay handshape gần mặt bằng cấu hình cong mềm/khum nhẹ, không khóa ngón cái và không đọc như nắm đấm.
- Nội suy độ mở ngón theo chuỗi frame 17 → 23 → 31 → 40, bắt đầu mở khi tay còn gần mặt thay vì đổi đột ngột.
- Xoay cổ tay cuối để lòng bàn tay đọc hướng lên và hơi ra trước; tâm cổ tay vẫn nằm trước thân trên, các ngón mở theo hướng ngang gần hai take tham chiếu.
- Đối chiếu trực quan cả hai take bằng frame tạm ngoài repository; không giữ lại still/contact sheet. Artifact review duy nhất là MP4 1280×720 bên dưới.
- Trạng thái ngôn ngữ học sau revision vẫn là **NOT YET TESTED** và cần owner duyệt trực quan.

## 4B. Orientation correction ngày 2026-11-26

> Ghi chú lịch sử: yêu cầu bảo toàn trajectory trong revision này đã bị owner thu hồi bởi motion-path correction ở mục 4C. Các số đo orientation vẫn được dùng làm mục tiêu kỹ thuật, không dùng để giữ đường tay cũ.

- Giữ nguyên `S002_MAIN`, 66 frame, shoulder/elbow/lowerarm01 rotations, near-face landmark và toàn bộ shoulder/elbow/wrist trajectory đã chấp nhận.
- Xác định `lowerarm02.L/R` là twist bone MPFB nối `lowerarm01` với `wrist`; phân bổ supination tại bone này và chỉ dùng `wrist` để căn cuối, thay vì tạo palm-up bằng wrist flexion đơn độc.
- Diagnostic frame 23/31/40 dùng wrist, index-base và little-base để tính palm plane; quy ước palmar normal theo handedness MPFB là `R = raw`, `L = -raw`.
- So sánh frame 17–40 trước/sau cho thấy max shift của shoulder, elbow và wrist ở cả hai bên đều `0,00000000 m`.
- Frame 23: trục dọc lòng bàn tay gần hướng lên (`Z = 0,985/0,984`); palm plane gần đứng và hướng vào signing space.
- Frame 31: palm normal chuyển dần sang up+forward (`world_up = 0,483/0,525`; `toward_camera = 0,717/0,739`).
- Frame 40: hai palm normal gần đối xứng, hướng lên rõ và hơi ra trước (`world_up = 0,864/0,861`; `toward_camera = 0,488/0,510`).
- Continuity số học không có flip: bước normal lớn nhất giữa hai frame liên tiếp là `10,111°` bên trái và `15,464°` bên phải.
- Computer Use helper lỗi khởi tạo hai lần, vì vậy playback trực tiếp ở 1× trong lượt này là **NOT YET TESTED**; không được thay thế bằng screenshot/contact sheet. Owner phải xem MP4 duy nhất trước acceptance.

## 4C. Motion-path correction theo owner ngày 2026-11-26

- Không đổi task, worktree, branch, rig Master Avatar v1, `S002_MAIN`, 66 frame/30 fps, neutral NMM hoặc pipeline build/export/Three.js.
- Tái tác giả `shoulder01`, `upperarm01`, `lowerarm01`, `lowerarm02` và `wrist` trong interval có nghĩa; không giữ trajectory đã bị owner từ chối.
- Frame 10 bắt đầu thấp và hẹp; frame 17 đi lên/vào trong; frame 23 hai tay đến vùng miệng/má dưới gần như đồng thời; frame 31–40 đi chủ yếu ra trước/xuống với độ tách ngang nhỏ.
- Screen-space palm center tại frame 23 là `x=0,562/0,441`, `y=0,593/0,594`; endpoint frame 40 hạ xuống và thu vào `x=0,629/0,373`, `y=0,378/0,364`.
- Wrist world-space endpoint là khoảng `(+0,100; -0,337; 1,150)` và `(-0,102; -0,335; 1,148)`; elbow cùng lúc ở khoảng `(+0,127; -0,106; 1,101)` và `(-0,127; -0,103; 1,096)`, giữ gần thân hơn candidate bị từ chối.
- Palm normal endpoint hướng lên và hơi ra trước: `world_up Z=0,864/0,948`, `toward_camera=0,488/0,325`. Handshape cong mềm và mở dần frame 17 → 23 → 31 → 40 được giữ nguyên.
- Continuity số học frame 10–40 không có discontinuity dữ liệu, nhưng bước palm-normal lớn nhất là `14,092°/frame` bên trái và `26,657°/frame` bên phải; đây là giới hạn trực quan chính cần owner xem ở 1×.
- Chỉ tạo lại một MP4 1280×720 tại path hiện có; không tạo still, contact sheet hoặc video bổ sung. Computer Use tiếp tục lỗi khởi tạo `helper_unknown_error`, vì vậy playback trực tiếp 1× là **NOT YET TESTED** và không được thay bằng ảnh chụp.

## 5. Output chính thức

- Motion spec: `blender/animation-specs/S002_MAIN.json`.
- Motion spec SHA-256: `10626903C3CA600DF71982182B10BD1028C06FD7A1A9202B53B8E9662E1E114C`.
- Blender: `blender/working/signs/S002/S002.blend` — SHA-256 `9C82C82E9FD8E93846ED51D219622968FB214C8440E066F6E4142F2898DEAF1C`.
- Base Blender: `blender/working/signs/S002/S002_base.blend` — SHA-256 `2C517D2ADB4679976C13D47E168816B60BFD3E87DA51D2336C9C8FEF82F68B2C`.
- Staging GLB: `assets/exports/signs/staging/S002-technical-draft.glb` — SHA-256 `5B040A1CFA5C630DC373B9FA7314EDE854A3F79B8BE8C0F31C43B9718C646A4A`.
- Viewer GLB đồng bộ: `apps/web/public/models/technical/s002-cam-on-technical-draft.glb` — cùng SHA-256 `5B040A1CFA5C630DC373B9FA7314EDE854A3F79B8BE8C0F31C43B9718C646A4A`.
- Palm diagnostic: `blender/working/signs/S002/evidence/palm-orientation-task0012b.json` — SHA-256 `468382666BB6EA019A40CF7D8426C91D6F190EB09DAFD48FE019152D3FF89F89`.
- Owner preview duy nhất: `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4` — SHA-256 `2A3E228A830655AE7AD4B95B693498B68FBCF931A2E5D80D61DC0B39358AA20E`.
- MP4: 1280×720, 30 fps, 66 frame, 2,20 giây.
- Bản TASK-0012A bị loại được giữ nội bộ dưới `blender/animation-specs/versions/`, `blender/working/signs/S002/versions/task-0012a/` và `assets/exports/signs/versions/`; không phải staging source of truth.

## 6. Commands và kiểm chứng

| Check | Kết quả | Evidence |
|---|---|---|
| `node tools/validate-sign-motion-spec.mjs ...` | PASS | `artifacts/TASK-0012B/motion-spec-validation.json` |
| `build_sign_animation.py` bằng Blender 5.2.4 LTS | PASS | `animation-build-task0012b.json` |
| `validate_sign_animation.py` | PASS kỹ thuật; linguistic NOT YET TESTED | `blender-validation-task0012b.json` |
| `export_sign_animation.py` | PASS | `glb-export-task0012b.json` |
| `node tools/validate-sign-draft.mjs ...` | PASS 10/10 | `artifacts/TASK-0012B/glb-validation.json` |
| Render owner preview | PASS | `artifacts/TASK-0012B/visual-review.json` |
| Palm-normal diagnostic frame 23/31/40 | MEASURED; tiêu chí hướng kỹ thuật đạt | `palm-orientation-task0012b.json` |
| Motion-path landmarks frame 10/17/23/31/40 | MEASURED; đạt cấu trúc hẹp → gần mặt → xuống/thấp-giữa | `palm-orientation-task0012b.json` |
| Playback trực tiếp preview ở 1× | NOT YET TESTED | Computer Use helper không khởi tạo; owner review bắt buộc |
| `npm run sync:technical-assets:check` | PASS | Hash viewer khớp staging GLB |
| `npm run check` | PASS | Typecheck, lint, unit tests, build và asset validators |
| Browser smoke với dev server cục bộ | PASS 8/8 | `artifacts/TASK-0012B/browser-smoke.json` |

Một lượt `npm run test:sign-preview` được gọi trước khi dev server chạy và timeout readiness; lượt này không hợp lệ, không được ghi là PASS/FAIL của artifact. Browser smoke hiện tại được chạy lại với Vite tại `127.0.0.1:4173` và đạt 8/8 check của validator hiện có.

## 7. Manual acceptance bắt buộc

Owner cần xem toàn bộ MP4 và xác nhận:

- hai tay đi từ vùng thân trên đến gần mặt trong một chuyển động liên tục;
- bàn tay không thành claw cứng và mở dần trong pha đi ra trước/xuống;
- endpoint, độ sâu và hướng lòng bàn tay đủ gần hai take tham chiếu;
- tại frame khoảng 40 có thể nhận diện rõ palm side của cả hai tay, không chủ yếu thấy mu bàn tay;
- cổ tay không rũ xuống, không trông gãy và orientation đổi liên tục từ gần mặt đến endpoint;
- không có xuyên mesh hoặc chuyển động gây hiểu sai đáng kể;
- chấp nhận hoặc yêu cầu chỉnh tiếp trước bất kỳ push nào.

Uncertainty chính: độ sâu/hướng lòng bàn tay và mức chính xác của landmark gần miệng do tham chiếu chính diện. Linguistic review vẫn **NOT YET TESTED**.

## 8. Git và handoff

- Staging area: trống.
- Commit hiện tại: `be1062331cddd6b58dfbabe9abf8e453bbf07c00`.
- Không tạo commit mới theo hạn chế của TASK-0012B.
- Không push, không tạo PR, không merge.
- Các thay đổi TASK-0012A có sẵn trong worktree được bảo toàn; không reset/clean/stash/overwrite.

## 9. Final hand symmetry correction — 2026-11-27

- Chỉ chỉnh bất đối xứng tay trong cùng `TASK-0012B`, worktree và branch; giữ `S002_MAIN`, 66 frame/30 fps, Master Avatar v1, neutral NMM, pipeline build/export/Three.js và staging path hiện có.
- Dùng tay trái của model làm chuẩn. Tay phải được giải thành counterpart mirror theo landmark cổ tay, palm center, palm normal, trục dọc bàn tay và hướng ngón giữa; không sao chép Euler giữa hai bên. Các continuity anchor bảo toàn finger curl/mở dần giống nhau ở hai tay.
- Trong meaningful interval frame 10–40: sai số mirror palm-normal trung bình `2,00°`, lớn nhất `8,06°` tại frame 19; sai số mirror cổ tay lớn nhất `24,9 mm` tại frame 32. Không còn frame vượt ngưỡng audit nội bộ `10°` hoặc `25 mm`.
- Preview duy nhất đã cập nhật: `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4`; `1280×720`, `30 fps`, `66 frame`, `2,20 giây`. Không giữ still, contact sheet hoặc PNG frame.
- Validator: motion spec PASS (`26` key pose, `66` frame); Blender PASS kỹ thuật và linguistic `NOT YET TESTED`; GLB PASS `10/10`; asset sync PASS; `npm run check` PASS; browser smoke PASS `8/8`.
- Playback trực tiếp 1× và đối chiếu trực quan hai take vẫn **NOT YET TESTED** vì Computer Use lỗi `helper_unknown_error` sau retry/reset. Owner phải xem MP4 trước acceptance; technical metrics không thay thế linguistic/visual approval.
- SHA-256 hiện tại: motion spec `CA91EFEA7BEC764829072544C0BDD0F3B8A000AEB8C7974C329DEB1BCBB17782`; Blender `470413295F5CB75B4B90CCAB23DF52628DC0CDD6AF9BB2FEE65A6998F89A4B05`; staging/viewer GLB `2DB9DA7B53AE240D7AC41115176FC7BE7DEB163516961C1CBEF9D79A9A8CA1E3`; palm diagnostic `3D9CE6D7AFC3CB0943E537C35AA34096912F087174490F33AEA00CCE5A9D094E`; MP4 `83F1A2BF5E7EA4038C45615F63432D58E4E5CA2541DD9A796C5CDAF72CC21B23`.
- Không chạy `git add`, commit, push, merge, rebase, reset hoặc clean trong revision này.

`WAITING_FOR_OWNER_REVIEW`

## 10. Motion polish / smoothing pass — 2026-11-27

- Giữ `S002_MAIN`, 66 frame/30 FPS và meaningful interval 10–40. Không tăng tổng frame hoặc làm chậm sign; thêm một breakdown frame 42, nên số key pose tăng từ 26 lên 27. Không đổi đường vai, khuỷu, cổ tay, near-face landmark, endpoint, palm orientation hoặc neutral NMM.
- Frame 27: chỉnh rất nhẹ `finger_overrides` của cả hai tay giống nhau để ngón bắt đầu duỗi sớm và chuyển tiếp mềm hơn. Frame 42: hai tay cùng có follow-through mở ngón dưới 0,2° rồi trở về open-hand endpoint tại frame 50. Đây là tinh chỉnh handshape, không phải diễn giải chuyển động mới.
- Đã thử giãn timing và đổi F-curve handles, nhưng số đo mirror xấu đi; hai candidate thử nghiệm bị loại và không được dùng để xuất/render. Interpolation `BEZIER`/`AUTO_CLAMPED` của bản được chấp nhận được giữ nguyên.
- Diagnostic 66 frame xác nhận wrist path frame 10–40 không đổi so với trước polish (`max shift = 0 mm`); mirror wrist lớn nhất `24,9 mm` tại frame 32 và mirror palm-normal lớn nhất `8,06°` tại frame 19, bằng bản trước. Finger timing hai bên dùng cùng override; tác động cảm nhận ở 1× còn cần owner xác nhận.
- Commands đã chạy trên bản cuối: `node tools/validate-sign-motion-spec.mjs --spec blender/animation-specs/S002_MAIN.json ...` PASS (`27` poses, `66` frame); Blender `build_sign_animation.py` PASS; `validate_sign_animation.py` PASS kỹ thuật, linguistic `NOT YET TESTED`; `export_sign_animation.py` PASS; `node tools/validate-sign-draft.mjs ...` PASS `10/10`; `npm run sync:technical-assets` PASS; `npm run check` PASS; `ffprobe` PASS (`1280×720`, `30 fps`, `66` frame, `2,20 s`). Browser smoke riêng của polish: SKIPPED vì không cần ảnh chụp bổ sung.
- Một MP4 owner-review được cập nhật tại `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4`; 0 still/contact sheet. Playback trực tiếp và so khớp hai take bằng mắt: **NOT YET TESTED**, Computer Use helper lỗi `helper_unknown_error`. Mesh deformation/độ tự nhiên khi phát 1× cần owner review; validator cấu trúc không xác nhận những điều này.
- SHA-256 hiện tại: spec `D0473DD894ED73DB2F0F5DC85EDE0E70F36519E14D5EDBE00607D6B3B41804DB`; `.blend` `DD378569369487DB8412955BD26DF11BDCA6D50F81108D5EBE6CE97B0CD9B120`; staging GLB `87A66BFD5032F5619FE4F9DD36D146161EF8201E8BC45235D198DB29768D4A06`; diagnostic `2ED981AC7F6BD09E2143DE2D49D540F3A7210AAFAD06CFA394395403CCAD0874`; MP4 `498CBC48A1909564DF4B6892FA44D1ADF9CFB0E7E1CC076B107DF2C39E013EBB`.
- Worktree `E:\University\Semester_7\HCI\BTL-worktrees\active-3d`; branch `feat/s002-cam-on`; HEAD `be1062331cddd6b58dfbabe9abf8e453bbf07c00`; staging trống. Không chạy `git add`, commit, push, merge, rebase, reset hoặc clean.

`WAITING_FOR_OWNER_REVIEW`

## 11. Elbow Stabilization Revision — cập nhật 2026-11-28

- Giữ worktree `E:\University\Semester_7\HCI\BTL-worktrees\active-3d`, branch `feat/s002-cam-on`, HEAD `be1062331cddd6b58dfbabe9abf8e453bbf07c00`; Master Avatar v1, `S002_MAIN`, 66 frame/30 fps, frame 23 gần miệng và neutral NMM không đổi. Giữ `shoulder01` và `upperarm01` ở hướng frame 23 trong pha thả; cho `lowerarm01`, `lowerarm02` và cổ tay quay quanh khuỷu. Thêm một breakdown ở frame 30 để làm đều tốc độ cung cổ tay; còn lại timing/handshape trước đó giữ nguyên, ngón tay hai bên dùng cùng nội suy mở.
- World-space frame 23–40: khuỷu tối đa **L 7,02 → 0,00 mm, R 4,11 → 0,00 mm** so với revision ngay trước; vai **L 0,55 → 0,00 mm, R 1,62 → 0,00 mm** (độ chính xác diagnostic 0,001 mm). So với bản trước khi bắt đầu ổn định khuỷu là **73,48/83,41 mm**. Cẳng tay quét khoảng **70,87°/70,47°**. Bước cổ tay lớn nhất **60,13/58,41 mm mỗi frame**, không còn đột biến frame 30–31; mirror cổ tay tối đa **7,31 mm**. Mirror palm-normal lớn nhất **9,64° ở frame 38**, tăng từ 5,71°; endpoint vẫn palm-up. Cổ tay cuối dịch **4,25/3,73 mm** so với revision ngay trước do khóa upper arm. Các góc twist/cổ tay phải gần giới hạn schema ở đoạn cuối, nên owner cần đánh giá độ tự nhiên. Bằng chứng từng frame: `blender/working/signs/S002/evidence/elbow-stabilization-task0012b.json`.
- QA hình ảnh đã xem trực tiếp từ MP4 hiện có ở frame **23, 27, 29, 30, 31, 33, 36, 40** mà không lưu ảnh mới. Trong các frame này, khuỷu/vai áo không còn trôi hoặc kéo rộng như bản trước, hai tay hạ gần đồng thời và ngón mở dần; vẫn có vùng áo/vai màu sáng, dáng sleeve thô đã hiện diện ở tư thế gần mặt. Playback liên tục ở 1×, so khớp hai take tham chiếu và đánh giá mọi frame về clipping/mesh deformation: **NOT YET TESTED**; owner phải xem MP4 trước acceptance. Không gọi bản kỹ thuật này là ký hiệu đã xác minh; linguistic review **NOT YET TESTED**.
- Checks thực chạy trên bản cuối: `validate-sign-motion-spec.mjs` **PASS** (28 poses/66 frame); Blender 5.2.4 `build_sign_animation.py` **PASS** (candidate binary được đối chiếu SHA khi đưa vào worktree), `validate_sign_animation.py` **PASS** kỹ thuật; `export_sign_animation.py` **PASS**; `validate-sign-draft.mjs` **PASS 10/10**; `npm run sync:technical-assets` và `npm run sync:technical-assets:check` **PASS**; `npm run check` **PASS**; `ffprobe` **PASS** (1280×720, 30 fps, 66 frame/2,20 s). Browser smoke riêng: **SKIPPED** để tránh ảnh bổ sung.
- Một preview cuối: `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4` (SHA-256 `A588E82B5A03D8075562E16605C0F69FDE71AAD27EAFC0C7FEB21F332A717482`). Không còn PNG/contact sheet ở artifact directory. SHA-256: spec `C58C33C3EC8507342CC5A8A0D0BD4E960DD75C44C3A252CD40E187920008AFAA`; `.blend` `DAF362B3E6052780D1C513A2D8464F46F9AAAE33990C80AA11AB40E75D850CF9`; staging/viewer GLB `080AC38407BE90782A1D259D67EA88748590715D6898C9ED02161AC47A3369AD`; elbow diagnostic `22FF45E380EEB9636828305170016E1987963B90385D0FB6F93EFD0125A2882F`. Hash trong các revision trước là lịch sử.
- Owner acceptance: xem MP4 ở 1×, xác nhận vai/khuỷu ổn định, cẳng tay hạ tự nhiên, hai tay đồng bộ, ngón mở dần, cổ tay không gãy, và chấp nhận hoặc yêu cầu sửa phần áo/vai cùng palm mirror ở frame 38. Staging trống; không chạy `git add`, commit, push, merge, rebase, reset hoặc clean. Trạng thái **WAITING_FOR_OWNER_REVIEW**.
## 12. Forearm Trajectory & Hand Alignment — 2026-11-28

- Giữ worktree `E:\University\Semester_7\HCI\BTL-worktrees\active-3d`, branch `feat/s002-cam-on`, HEAD `be1062331cddd6b58dfbabe9abf8e453bbf07c00`; Master Avatar v1, `S002_MAIN`, 30 FPS/66 frame, frame 23 gần miệng, neutral NMM và pipeline GLB/Three.js. Sửa `lowerarm01`, forearm twist và wrist trong pha thả 23–40; thêm breakdown frame 26, tổng 29 key pose. Giữ upper arm/vai và các mốc mở ngón hiện có, thêm nội suy ngón tại frame 26. Không đổi master hoặc trang phục.
- Đối chiếu hai take riêng tư tại mốc gần mặt, giữa và cuối bằng landmark vai/khuỷu/cổ tay/tâm lòng bàn tay chuẩn hóa theo bề rộng vai; số đo 2D chỉ xấp xỉ (sai số 15–25 px), không suy diễn độ sâu. Bằng chứng: `blender/working/signs/S002/evidence/forearm-reference-landmarks-task0012b.json`. Không đưa video tham chiếu vào Git.
- World-space frame 23→40, trái/phải: khuỷu tối đa `0/0 mm`; dịch ngang cổ tay từ `+16,74/-19,55` còn `+9,35/-9,70 mm`; dịch xuống từ `220,28/218,71` còn `147,47/147,51 mm`, tiến về trước `152,87/152,18 mm`. Bước cổ tay lớn nhất từ `60,13/58,41` còn `19,90/19,85 mm/frame`. Góc trục bàn tay–cẳng tay ở frame 40 từ `90,61/90,30°` còn `54,87/54,37°`; đã cải thiện nhưng vẫn cần owner đánh giá độ tự nhiên. Palm-normal endpoint có thành phần world-up `+0,856` ở cả hai tay. Sai số mirror cổ tay tối đa từ `7,31` còn `1,61 mm`; palm-normal từ `9,64°` còn `2,40°`. Dữ liệu từng frame: `blender/working/signs/S002/evidence/forearm-trajectory-alignment-task0012b.json`.
- Một preview được ghi đè đúng đường dẫn `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4`: `1280×720`, `30 fps`, 66 frame, 2,20 giây; SHA-256 `AF7E8CBC588B3B2F4848D1EEAB9BCA881FA47F75141BF643825533933E2C068C`. Không tạo contact sheet hoặc giữ PNG. Đã xem trực tiếp các khung 23, 26, 31, 35, 40 trong bộ nhớ và so với khung 31/40 bản trước; đường cổ tay gọn hơn, mở ngón và palm-up còn thấy rõ. Áo/vai/sleeve vẫn có mép thô và biến dạng ở tư thế nâng tay, đã có trong bản trước; các khung đã xem không cho thấy clipping mới nghiêm trọng. Kiểm tra giải mã toàn video theo nhịp 1× **PASS**; xem bằng trình phát trực quan liên tục 1× **NOT YET TESTED** vì Computer Use lỗi `helper_unknown_error`.
- Checks bản cuối: `validate-sign-motion-spec.mjs` **PASS** (29 poses/66 frame); Blender 5.2.4 `build_sign_animation.py` **PASS** với SHA promoted khớp, `validate_sign_animation.py` **PASS** kỹ thuật; `export_sign_animation.py` **PASS**; `validate-sign-draft.mjs` **PASS 10/10**; `npm run sync:technical-assets` và `npm run sync:technical-assets:check` **PASS**; `npm run check` **PASS**; `ffprobe` **PASS**. Browser smoke riêng **SKIPPED** vì task chỉ yêu cầu một video. Linguistic review **NOT YET TESTED**; đây là candidate kỹ thuật, chưa xác minh ngôn ngữ ký hiệu.
- SHA-256: spec `6E837424B2661B9FFFBB50273D5277EA112AF9CCAFB0846BA28C78CC10026243`; `.blend` `AAA7CE70C950A73E8707DEC41628FD891DDDD34B25F6E97BDE770D110E8FDA48`; staging/viewer GLB `937952B8EC71A62EAA989B9DB7EEE13157A4140895CA77C1B3FD7D388F74CBF7`; diagnostic `FB690E9E81FE41449E620A81DA091E3EF2C33C5872151FE7A115B0EEE9F66DE3`.
- Owner cần xem MP4 ở 1×, đối chiếu cả hai take, xác nhận góc bàn tay/cẳng tay, palm-up, cung thả và giới hạn sleeve. Staging Git trống; không chạy `git add`, commit, push, merge, rebase, reset hoặc clean. **WAITING_FOR_OWNER_REVIEW**.
## 13. Final Near-Mouth Handshape and Palm Orientation Polish — 2026-11-28

- Tiếp tục `TASK-0012B` trong worktree `E:\University\Semester_7\HCI\BTL-worktrees\active-3d`, branch `feat/s002-cam-on`, HEAD `be1062331cddd6b58dfbabe9abf8e453bbf07c00`. Đối chiếu take 1 (khoảng 1,90/2,08/2,35 s) và take 2 (4,80/5,02/5,30 s) của video người thật ở mốc gần miệng, thả tay và kết thúc. Video tham chiếu riêng tư vẫn được Git ignore. Không thêm thân nghiêng vì độ lớn và vai trò của chuyển động này chưa rõ từ góc quay chính diện.
- Giữ Master Avatar v1, `S002_MAIN`, 66 frame/30 FPS, quỹ đạo cổ tay đi xuống/trước, khuỷu/vai ổn định, vị trí tay cuối và neutral NMM. Chỉnh riêng độ cuộn ngón trong các pose tiếp cận/gần miệng và `lowerarm02` twist + wrist theo trục MPFB tại các breakdown 20–31; giữ 29 key pose. Tại frame 23, tổng góc cuộn ba đốt ngón trỏ từ `60°` còn `33°`; ngón giữa hướng lên rõ hơn (thành phần world-up `0,81 → 0,92`). Không thêm động tác hoặc đổi góc camera.
- Với đích miệng 3D **ước lượng** `(0; -0,085; 1,43) m`, tích vô hướng palm-normal hướng về miệng ở frame 23 tăng `0,506/0,505 → 1,000/1,000` (trái/phải); thành phần palm-normal theo +Y từ khoảng `-0,52` sang `+0,46`, nên mặt lòng bàn tay hướng về vùng mặt thay vì hướng về camera. Đây chỉ là hướng dẫn hình học; độ sâu thật của video chính diện chưa xác định. Ở frame 31, palm-normal world-up `+0,404/+0,383`; frame 40 giữ `+0,856/+0,856` và tư thế cuối cũ. Góc bàn tay–cẳng tay tại frame 23 khoảng `11,3°/11,5°`. Sai số mirror palm-normal lớn nhất trong frame 23–40 là `1,65°`; bước xoay palm-normal lớn nhất frame 17–40 là `17,41°` tại frame 20 tay phải.
- Khoảng cách nhỏ nhất giữa các đầu ngón hai tay ở frame 23 tăng `17,77 → 33,91 mm`; các đầu ngón giữa vẫn nằm hai phía của đường giữa cơ thể. So với bản trước, khuỷu và cổ tay tại các mốc đo lệch tối đa `0,00 mm`. Bằng chứng: `blender/working/signs/S002/evidence/final-handshape-palm-polish-task0012b.json` (SHA-256 `42910FE295FC230683FDF59F6D3C62D4AB2B7CA4B713104E7A0BA72905B84997`) và `palm-orientation-task0012b.json`. Số đo không thay thế QA hình ảnh hay linguistic review.
- Đã tạo đúng **một** MP4 tại `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4` (SHA-256 `B382F5A3B29AAB12843DB1F41E73C6237548B3F58BD4FFE9F0B57FD97166D1FA`): `1280×720`, 30 FPS, 66 frame/2,20 s; 0 PNG/contact sheet. Đã xem trực tiếp các frame 20, 23, 26, 31, 40 trong bộ nhớ, so với cả hai take. Tại frame 23, tay không còn chồng ngang trước môi, ngón cuộn nhẹ và hướng lên. Endpoint vẫn palm-up. Vùng sleeve/vai có mesh thô/đứt hình như bản trước; ở các frame đã xem không phát hiện clipping mới nghiêm trọng. Palm-up trong phần giữa của avatar vẫn xuất hiện muộn hơn người mẫu; owner cần đánh giá độ tự nhiên ở 1×. Giải mã toàn video theo nhịp 1× **PASS**; xem trực quan liên tục bằng trình phát 1× **NOT YET TESTED** vì Computer Use bị lỗi kernel khi mở giao diện.
- Các lệnh đã chạy trên bản cuối: `node tools/validate-sign-motion-spec.mjs --spec blender/animation-specs/S002_MAIN.json ...` **PASS** (29 pose/66 frame); Blender 5.2.4 `build_sign_animation.py` **PASS** với SHA binary khi đưa vào worktree khớp, `validate_sign_animation.py` **PASS** kỹ thuật; `export_sign_animation.py` **PASS**; `node tools/validate-sign-draft.mjs ...` **PASS 10/10**; `npm run sync:technical-assets`, `npm run sync:technical-assets:check`, `npm run check` **PASS**; `ffprobe` **PASS**. Browser smoke riêng **SKIPPED** để không tạo ảnh bổ sung. Linguistic review **NOT YET TESTED**.
- SHA-256 hiện tại: spec `2BF8F8B46BAFAEE767D7A5CC7B7F878C7392AE4BC8A078A8F4E3D4D981E084A4`; `.blend` `1342549E12687A9506E34684EC4B8175DA7B83B659118E3F42A9ED6BED4A6747`; staging/viewer GLB `948FA5FD7567FE9B6E447D095CDA39A24602E5E880B7D73D5202B0843360229C`. Các hash ở section trước là lịch sử.
- Owner acceptance: xem MP4 ở 1×, đối chiếu ngón và lòng bàn tay gần miệng với cả hai take, kiểm tra thời điểm palm-up ở giữa động tác, góc nối cổ tay/cẳng tay và giới hạn sleeve. Không chạy `git add`, commit, push, merge, rebase, reset hoặc clean. **WAITING_FOR_OWNER_REVIEW**.
## 14. Final Small Correction — 2026-11-28

- Đối chiếu take 1 ở khoảng 1,75–1,90 s và take 2 ở 4,75–4,90 s cho pha gần miệng; xem thêm mốc thả tay 2,08/5,02 s. Giữ video người thật trong thư mục ignored. Chỉ tăng nhẹ gập khớp giữa ngón 2–5 tại frame 17–27 (tối đa 2,5–3° ở frame 23), không đổi ngón cái, vị trí vai/khuỷu/cổ tay, 66 frame/30 FPS, NMM, Master Avatar v1 hoặc tư thế cuối. Đầu ngón hướng về vùng môi và không giao nhau ở các khung đã xem; bề ngang đầu ngón 2–5 của tay trái tại frame 23 từ 28,57 còn 28,29 mm, khoảng cách đầu ngón giữa hai tay từ 33,91 còn 32,27 mm. Thay đổi cố ý rất nhỏ vì pipeline hiện chỉ có flex, không có điều khiển adduction riêng.
- Chỉnh forearm twist và wrist tại các pose 26–35 để lòng bàn tay bắt đầu ngửa sớm hơn: thành phần palm-normal theo world-up tại frame 26 từ -0,009/+0,007 thành +0,062/+0,066; frame 31 từ +0,404/+0,383 thành +0,500/+0,496; frame 33 từ +0,257/+0,257 thành +0,465/+0,465 (trái/phải). Frame 40 giữ +0,856/+0,856. Bước xoay palm-normal lớn nhất trong pha thả 23–40 từ 14,54 còn 14,09°/frame; sai số mirror lớn nhất từ 1,65 còn 1,29°. Khuỷu và cổ tay ở các mốc đo lệch 0,00 mm so với bản trước. Bằng chứng: `blender/working/signs/S002/evidence/final-small-correction-task0012b.json` (SHA-256 `771CDAC39D30597AEAA32ACB535D0AB2461622316B989DD027B16888B58E2A09`).
- Một preview duy nhất được cập nhật tại `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4` (SHA-256 `FF9364DC82394C90CF8607B72CB762CED5D686844A5D39CFA384A400B9293BE5`): 1280×720, 30 FPS, 66 frame/2,20 s, 0 PNG/contact sheet. Đã xem các frame 23, 27, 30, 33, 35, 40 trong bộ nhớ và so với hai take; không thấy giao tay hoặc clipping mới nghiêm trọng. Áo/vai vẫn có mép mesh thô từ trước. Người mẫu ngửa lòng bàn tay sớm hơn avatar ở một phần pha giữa; owner cần đánh giá bằng mắt ở tốc độ 1×. Giải mã toàn video ở nhịp 1× **PASS**; xem liên tục bằng trình phát trực quan **NOT YET TESTED**.
- Checks đã chạy: `validate-sign-motion-spec.mjs` **PASS** (29 pose/66 frame), Blender 5.2.4 `build_sign_animation.py` và `validate_sign_animation.py` **PASS** kỹ thuật, `export_sign_animation.py` **PASS**, `validate-sign-draft.mjs` **PASS 10/10**, `npm run sync:technical-assets`, `npm run sync:technical-assets:check`, `npm run check`, `ffprobe` **PASS**. Browser smoke riêng **SKIPPED** vì không cần ảnh bổ sung; linguistic review **NOT YET TESTED**. SHA-256: spec `8304D89FC8449C336B524BD3FC56EE4079C5BDBD7D7412DD48F144C212DBE3A6`; `.blend` `D62F214D49B4206F7B3FD9D2972D1162DF3EC9B3ABA2ADCFB1E53BDAC6D01DFF`; staging/viewer GLB `24D281A9EEC70ABE88E01890C553D86FE850929C748FFFF5458BA34778C7E3BC`.
- Worktree `E:\University\Semester_7\HCI\BTL-worktrees\active-3d`, branch `feat/s002-cam-on`, HEAD `be1062331cddd6b58dfbabe9abf8e453bbf07c00`. Owner cần xem video 1× và xác nhận độ khép ngón, thời điểm palm-up cùng giới hạn áo/vai. Không chạy `git add`, commit, push, merge, reset hoặc clean. **WAITING_FOR_OWNER_REVIEW**.

## 15. Last focused handshape correction — 2026-11-28

- Tiếp tục đúng worktree `E:\University\Semester_7\HCI\BTL-worktrees\active-3d`, branch `feat/s002-cam-on`, HEAD `be1062331cddd6b58dfbabe9abf8e453bbf07c00`. Giữ `S002_MAIN`, 29 key pose, 66 frame/30 FPS, Master Avatar v1, neutral NMM, vị trí vai/khuỷu/cổ tay, đường thả cẳng tay và endpoint palm-up. Không sửa rig hay hierarchy. Video tham chiếu riêng tư vẫn được Git ignore.
- Probe xương MPFB thật xác nhận các đốt gốc `finger2-1` đến `finger5-1` gập theo trục X cục bộ; trục Z cục bộ điều khiển khép/xòe. Bổ sung trường tùy chọn `finger_adduction_degrees` vào schema và pose authoring; chỉ dùng tại các mốc 17–29, tăng dần đến frame 23 rồi giảm dần. Frame 23: ngón trỏ/vô danh/út tay trái lần lượt `-6°/+4°/+5°` quanh Z, tay phải đối dấu; ngón giữa làm mốc, ngón cái và góc gập ngón hiện có giữ nguyên. Test Blender xác nhận X-flex và Z-adduction độc lập ở cả hai tay. Đây là **adduction thật**, không thay bằng gập ngón thêm.
- Ở frame 23, khoảng cách đầu ngón 2–3 giảm `36,344 → 30,810 mm`, 3–4 giảm `30,643 → 26,430 mm`; bề ngang các đầu ngón 2–5 tay trái giảm `28,289 → 25,537 mm` (tay phải `28,223 → 25,486 mm`). Khoảng 4–5 gần như không đổi (`30,420 → 30,429 mm`): khép tổng thể có cải thiện nhưng cặp này vẫn là giới hạn nhỏ cần owner xem. Hai tay sai khác khoảng cách kề tối đa `0,001 mm`. Trên frame 17–30, khoảng cách đầu ngón kề nhỏ nhất `26,430 mm`, giữa hai tay nhỏ nhất `34,372 mm`; không thấy giao ngón ở các frame đã xem. Phép đo đầu ngón không chứng minh toàn bộ lưới 3D không giao nhau.
- Xoay `lowerarm02` và wrist nhẹ hơn trong các mốc 26–36 để lòng bàn tay bắt đầu ngửa sớm hơn đồng thời với mở ngón. Thành phần palm-normal hướng lên ở frame 31 tăng `0,500/0,496 → 0,585/0,584`, frame 33 tăng `0,465/0,465 → 0,574/0,574` (trái/phải); frame 40 giữ `0,856/0,856`. Bước xoay lớn nhất trong pha thả 23–40 giảm `14,09° → 13,42°/frame`; vị trí khuỷu và cổ tay lệch tối đa `0,00 mm`. Hai lượt tham chiếu tại ~1,80/4,80 s (gần miệng) và ~2,08/5,02 s (thả tay) đã được so với các frame 23, 26, 31, 35, 40 của MP4 trong bộ nhớ. Ở giữa pha thả, avatar vẫn ngửa lòng bàn tay muộn hơn người thật; cần owner đánh giá trực quan ở 1×. Mép áo/vai thô vốn có vẫn thấy; không thấy clipping mới nghiêm trọng ở các frame đã xem.
- Bằng chứng định lượng: `blender/working/signs/S002/evidence/last-focused-handshape-correction-task0012b.json` (SHA-256 `4C5D370D690FA43C182E692449D786495B37E5F06F01A4C4FF932EB1C7EA9794`). Video duy nhất được cập nhật tại `docs/reports/artifacts/TASK-0012B/s002-cam-on-rebuild-720p.mp4` (SHA-256 `248D99FB7757115EB0600A39F4919DF3BC35C2938A5721A9CE9CA1EA103D19BF`): 1280×720, 30 FPS, 66 frame/2,20 s; **0 ảnh tĩnh/contact sheet**. Đã xem frame trong bộ nhớ; phát liên tục bằng trình xem 1×: **NOT YET TESTED**.
- Kiểm tra thực chạy: `node tools/validate-sign-motion-spec.mjs --spec <candidate> ...` **PASS** (29 pose/66 frame); Blender 5.2.4 `test_sign_pose_utils.py` **PASS** (8 checks), `build_sign_animation.py` **PASS**, `validate_sign_animation.py` **PASS** (14 kỹ thuật; linguistic **NOT YET TESTED**), `export_sign_animation.py` **PASS**, `node tools/validate-sign-draft.mjs ...` **PASS 10/10**, `npm run sync:technical-assets` và `npm run check` **PASS**, `ffprobe` **PASS**. Evidence: `pose-utils-last-focused-task0012b.json`, `animation-build-last-focused-task0012b.json`, `blender-validation-last-focused-task0012b.json`, `glb-export-last-focused-task0012b.json`, cùng `docs/reports/artifacts/TASK-0012B/{motion-spec-validation,glb-validation,visual-review}.json`. Browser smoke riêng **SKIPPED** để không tạo ảnh bổ sung. GLB staging và bản Three.js khớp SHA-256 `E2D56C320A35610BF52AA1A55AFADFB2CA3F1FEC82D3455F97B9BD11F2D63A9E`.
- SHA-256 hiện tại: spec `6C1D9740DD7B6A7A5979CBDDA6B1C6B95C91FDCA760BBB41A04D7708BDA9CFCA`; `.blend` `22C64DCF9CBEB06D5B73A5B74C66951EB196F949C65EE06743DAB299387AD2A2`. Owner cần xem MP4 1× và quyết định độ khép ngón, tốc độ ngửa lòng bàn tay giữa pha thả và giới hạn áo/vai. Linguistic review **NOT YET TESTED**. Không chạy `git add`, commit, push, merge, reset hoặc clean. **WAITING_FOR_OWNER_REVIEW**.
