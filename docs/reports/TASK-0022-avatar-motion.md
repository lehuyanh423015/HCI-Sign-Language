# TASK-0022 — Tinh chỉnh Linh và bộ chọn nhân vật

Ngày 28/11/2026, Asia/Saigon. Trạng thái kỹ thuật PASS. Nhánh `nhatdoankhanh/task-0022-avatar-motion` từ commit `9cc4db2`. Khi bắt đầu chỉ có `.agents/` chưa được Git theo dõi.

## Phạm vi và môi trường

Chỉnh trang xem trước S001 và clip của nhân vật VRoid. Dùng Node 24, Three.js, Chrome headless. Baseline Blender 5.2.4 LTS + MPFB 2.0.18. Lần này script trực tiếp đọc VRM và xuất GLB.

## Thay đổi

- Đặt tên hiển thị Khang cho Snow và Linh cho VRoid. Bộ chọn là hai thẻ radio có trạng thái chọn, dùng được bằng bàn phím, có bố cục cho màn hình hẹp.
- Làm mượt chuyển động tay của Linh theo quaternion và thêm chuyển động đầu nhẹ. Clip giữ thời lượng hai giây và gồm 37 kênh xoay.
- Thêm hai hoạt ảnh kỹ thuật từ các đoạn của S001 là **Luyện nâng tay** và **Luyện vẫy tay**. Mỗi bài chạy xuôi rồi ngược để nối vòng lặp ở cùng tư thế. Đổi chế độ bắt đầu phát lại từ đầu.
- Tệp sửa gồm `TechnicalViewer.tsx`, `SignAnimationPreviewPage.tsx`, `global.css`, `tools/retarget-s001-vrm.mjs`, `tools/test-technical-viewer.mjs` và GLB staging `S001-vroid.glb`.

## Lệnh đã chạy

```powershell
node tools/retarget-s001-vrm.mjs assets/exports/signs/staging/S001-snow.glb "$env:USERPROFILE/Downloads/8590256991748008892.vrm" assets/exports/signs/staging/S001-vroid.glb
npm run sync:technical-assets
npm run sync:technical-assets:check
npm test
npm run build
npm run lint
node tools/test-technical-viewer.mjs --vroid --url http://127.0.0.1:4173/technical-sign-preview --report assets/previews/TASK-0022-avatar/browser.json --screenshot assets/previews/TASK-0022-avatar/hand.png --full-screenshot assets/previews/TASK-0022-avatar/linh.png
git diff --check
```

## Kiểm tra và bằng chứng

| Kiểm tra | Kết quả | Trạng thái |
|---|---|---|
| GLB Linh | Khronos validator ghi 0 lỗi và 8 cảnh báo. SHA-256 `f1b2766b3ad09dc3ad59ae7bfe49090257f4c68d04df4934a7196056b0070341` | PASS |
| Build, lint, test và đồng bộ GLB | Build gồm kiểm tra TypeScript, 16 bài test đạt, bản web khớp staging | PASS |
| Chrome | 14/14, gồm đổi nhân vật, khởi chạy hai bài luyện và kiểm tra màn hình hẹp | PASS |
| Duyệt độ tự nhiên và nội dung ký hiệu | Chờ đánh giá | NOT YET TESTED |

Ảnh và JSON kiểm tra nằm trong `assets/previews/TASK-0022-avatar/`. Commit ghi trong phản hồi cuối. Không có blocker kỹ thuật cho trang xem trước.

## Nghiệm thu thủ công

- [ ] Đổi giữa Khang và Linh, chọn từng hoạt ảnh trong menu cạnh bộ chọn nhân vật.
- [ ] Xem Linh ở 1× và 0,5× để đánh giá chuyển động đầu và tay.
