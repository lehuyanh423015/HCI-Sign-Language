# TASK-0017 — Tích hợp avatar Snow cho bản xem trước S001

- Ngày và múi giờ — 28/11/2026, Asia/Saigon
- Nhánh và base — `nhatdoankhanh/task-0017-snow-avatar` từ `fb91e56`
- Phạm vi — Thay avatar đang phát clip `S001_MAIN` ở `/technical-sign-preview`, lối vào từ **Bản mẫu ký hiệu** và nút xem bản mẫu trên trang chủ.
- Trạng thái tổng thể — PASS cho bản xem trước kỹ thuật. Phát hành học liệu và thay canonical master là ngoài phạm vi.

## Tóm tắt

Trang xem trước S001 dùng Snow v4.2 và clip hai giây chuyển từ bản dựng S001 v4. Ở frame 5, ngón trỏ và ngón giữa được điều chỉnh theo hình học Snow để bỏ giao nhau trong vùng được kiểm tra. Trang hiển thị credit Snow và trạng thái chờ xác minh ngôn ngữ.

## Trạng thái kho ban đầu

Nhánh `nhatdoankhanh/task-0016-snow-pilot` tại `fb91e56`. Thư mục `.agents/` của người dùng chưa được theo dõi. Remote `origin` trỏ đến `https://github.com/lehuyanh423015/HCI-Sign-Language.git`.

## Môi trường và phụ thuộc

- Windows x64, Blender 5.2.4 LTS portable, build `cd5dc428cce1`. Baseline MPFB 2.0.18. Lần xuất dùng rig và animation có sẵn nên chạy headless với `--disable-autoexec` và không nạp MPFB.
- Node v24.21.0, Vite 8.3.8, Three.js 0.187.0, Chrome headless với WebGL.
- Snow Rig (CC) Blender Foundation | studio.blender.org. [Trang Snow v4](https://studio.blender.org/characters/snow/v4/)

## Nội dung thực hiện

- Đọc action S001 hiện có và lấy mẫu 60 frame. Chuyển hai cánh tay, cổ tay, hướng lòng bàn tay và 30 điều khiển ngón sang rig FK của Snow. Tỉ lệ ngón trỏ và ngón giữa ở frame 5 là 0,78 so với độ xoay chuyển từ nguồn.
- Lưu bản Blender làm việc và xuất GLB tự chứa. Chuyển texture da UDIM thành các vật liệu glTF riêng và giới hạn kích thước texture cho web. Lưới mắt dùng bản render của Snow.
- Đồng bộ GLB staging vào web. Viewer nhận diện các mốc xương Snow cho góc cận tay phải. Khi nhấn **Phát lại**, thanh thời gian về đầu ngay.

## Tệp tạo và sửa

- `blender/scripts/export_snow_s001.py` — Chuyển chuyển động và xuất Snow.
- `assets/exports/signs/staging/S001-snow.glb` — GLB nguồn của trang xem trước.
- `tools/sync-technical-assets.mjs` — Sinh bản web `apps/web/public/models/technical/s001-snow.glb`.
- `apps/web/src/features/technical/SignAnimationPreviewPage.tsx`, `apps/web/src/components/viewer/TechnicalViewer.tsx`, `apps/web/tests/App.test.tsx` — Tích hợp trang, camera, phát lại và cập nhật kiểm tra tuyến.

## Lệnh đã chạy

```powershell
$blender = "$env:TEMP/hci-snow-blender-524/blender-5.2.4-windows-x64/blender.exe"
& $blender -b assets/previews/TASK-0016-snow/input/snow_v4.2.blend --disable-autoexec --python-exit-code 1 --python blender/scripts/export_snow_s001.py -- --source blender/working/signs/S001/refinements/task-0011b/S001_refined.blend --working-copy assets/previews/TASK-0017-snow/S001-snow.blend --output assets/previews/TASK-0017-snow/S001-snow.glb
Copy-Item -LiteralPath assets/previews/TASK-0017-snow/S001-snow.glb -Destination assets/exports/signs/staging/S001-snow.glb
npm run sync:technical-assets
npm run sync:technical-assets:check
npm run validate:assets
python -m py_compile blender/scripts/export_snow_s001.py
npm run typecheck
npm run lint
npm test
npm run build
npm run dev --workspace @hci-sign/web -- --host 127.0.0.1 --port 4173 --strictPort
node tools/test-technical-viewer.mjs --url http://127.0.0.1:4173/technical-sign-preview --report assets/previews/TASK-0017-snow/browser.json --screenshot assets/previews/TASK-0017-snow/hand.png --full-screenshot assets/previews/TASK-0017-snow/web.png
git diff --cached --check
```

Đã chạy thêm `gltf-validator.validateBytes` và `inspectGlb` trực tiếp trên GLB Snow, đo cổ tay trong Blender và đối chiếu SHA-256 của các nguồn. Phép dò giao nhau dùng `BVHTree.FromPolygons` với epsilon bằng 0. Tại mỗi frame và nửa frame, phép dò chọn tam giác mà cả ba đỉnh có trọng số trên 0,5 với xương ngón hoặc cổ tay cùng bên, rồi đếm các cặp giao nhau có đỉnh rời nhau.

## Ma trận kiểm tra

| Kiểm tra | Bằng chứng | Trạng thái |
|---|---|---|
| GLB Snow và action | 15 mesh, 292 khớp, 19 ảnh nhúng, clip `S001_MAIN` 2 giây, 0 lỗi Khronos | PASS |
| Giao nhau trong vùng bàn tay của bản Blender | 119 mẫu, 2.409 tam giác/bên, 0 cặp ở cả hai tay sau hiệu chỉnh | PASS |
| Đồng bộ asset | Web public GLB và bản dist khớp SHA-256 với staging | PASS |
| Chrome và điều khiển viewer | 11 bài kiểm tra gồm nạp GLB, phát, tạm dừng, tiếp tục, phát lại, lặp, tốc độ, tua, xoay/zoom, camera và bố cục mobile | PASS |
| TypeScript, ESLint, test và build | 8 test công cụ, 8 test web, Vite build | PASS |
| Bảo toàn binary nguồn | Hash Snow, master, S001 Blender và GLB cũ khớp trước và sau | PASS |
| Đánh giá ngôn ngữ S001 trên Snow | Chờ người đánh giá | NOT YET TESTED |
| Phát hành học liệu | Ngoài phạm vi bản xem trước | SKIPPED |

## Bằng chứng và tệp sinh ra

Thư mục `assets/previews/TASK-0017-snow/` chứa `S001-snow.blend`, `gltf-review.json`, `snow-motion-review.json`, `browser.json`, `web.png` và `hand.png`. Bản Blender tham chiếu thư mục texture của bản Snow thử tại `assets/previews/TASK-0016-snow/input/`.

| Binary | SHA-256 |
|---|---|
| Snow nguồn | `80FD0A81BCA90F0EFDCDCB98422DF0E198AE57F4A1C239E13FB795922779B1FC` |
| Avatar master | `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC` |
| S001 v4 Blender nguồn | `BD0F3877040257785D0CAA6EB8BA5E7B57F07A74445532D103A93981D9483063` |
| S001 GLB trước tích hợp | `006109E192A82898F0C0997D0DC11F8E31BC08362DA34A517AE3B7A40C19B627` |
| Snow GLB staging | `1321B0F6341469D5EEBFD1A656334C240423FF0949D0318E22F24B4384ABD69C` |

## Giới hạn và vấn đề đã biết

- GLB Snow dùng vật liệu web đơn giản hóa và tập trung vào chuyển động tay. Điều khiển biểu cảm Snow cần quy trình tích hợp riêng nếu một clip yêu cầu biểu cảm.
- Validator ghi 11 cảnh báo `NODE_SKINNED_MESH_NON_ROOT` về cấu trúc node skin. Chrome phát và hiển thị bản GLB này.
- Phép dò bàn tay không đo giao nhau với thân hoặc trang phục. Các tư thế thử độc lập nắm tay và gập ngón cái từ TASK-0016 vẫn cần chỉnh khi dùng trong clip khác.
- Lần chạy test đầu trong sandbox gặp `spawn EPERM` và thành công khi chạy lại với quyền đã cấp. Lần browser smoke đầu trên GLB cuối thấy thanh thời gian còn hiển thị thời điểm cũ ngay sau thao tác phát lại. Viewer đã cập nhật thời gian ngay tại thao tác.

## Thông tin Git

Commit được tạo trên nhánh `nhatdoankhanh/task-0017-snow-avatar`. Hash commit được ghi trong phản hồi cuối.

## Vướng mắc còn lại

S001 cần đánh giá ngôn ngữ và người phụ trách xác nhận trước khi đưa bản Snow vào thư viện bài học. Tuyến kỹ thuật hiển thị trạng thái hiện tại.

## Checklist nghiệm thu thủ công

- [ ] Từ trang chủ, mở **Xem bản mẫu 3D** và xác nhận Snow hiện trong S001.
- [ ] Tua qua động tác vẫy, phát ở 0,5× và mở **Góc nhìn → Cận cảnh tay phải**.
- [ ] So sánh nhịp và hình tay của Snow với bản S001 v4 khi đánh giá kỹ thuật và ngôn ngữ.

## Công việc kế tiếp đề xuất

Đưa bản Snow S001 đi review nội dung trước khi cập nhật học liệu chính thức.
