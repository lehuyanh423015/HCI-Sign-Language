# TASK-0021 — Thêm nhân vật VRoid vào trang xem trước S001

Ngày 28/11/2026 theo Asia/Saigon. Xem trước kỹ thuật đạt PASS. Nhánh `nhatdoankhanh/task-0021-vrm-avatar` từ `05d2894`. Lúc bắt đầu chỉ có `.agents/` chưa được Git theo dõi.

## Phạm vi và môi trường

Trang `/technical-sign-preview` có bộ chọn Snow v4.2 hoặc AvatarSample_A của VRoid Project. Mặc định mở Snow, mỗi lần chuyển nhân vật mở clip từ đầu. Nguồn VRM 0 xuất từ VRoid Studio 1.26.0. Dùng Node 24, Three.js hiện có trong repo và Chrome headless. Baseline Blender 5.2.4 LTS và MPFB 2.0.18. Lần này xử lý trực tiếp GLB và VRM.

## Thay đổi và tệp

- `tools/retarget-s001-vrm.mjs` đọc rig và clip Snow, chuyển động hai tay qua rig VRoid dựa trên hướng các đoạn tay, lòng bàn tay và ngón tay. Ghi 61 mẫu cho 36 xương, dùng clip `S001_MAIN` dài 2 giây.
- `assets/exports/signs/staging/S001-vroid.glb` chứa nhân vật có clip, texture và metadata VRM gốc. Metadata ghi tác giả VRoid Project và cho phép sửa đổi, phân phối lại.
- `tools/sync-technical-assets.mjs` đồng bộ GLB vào web. Bộ chọn và camera dùng `SignAnimationPreviewPage.tsx`, `TechnicalViewer.tsx` và `global.css`. Cập nhật `App.test.tsx` và `test-technical-viewer.mjs` để kiểm tra lựa chọn mới.

## Lệnh đã chạy

```powershell
node tools/retarget-s001-vrm.mjs assets/exports/signs/staging/S001-snow.glb "$env:USERPROFILE/Downloads/8590256991748008892.vrm" assets/exports/signs/staging/S001-vroid.glb
npm run sync:technical-assets
npm run sync:technical-assets:check
npm run typecheck
npm run lint
npm test
npm run build
node tools/test-technical-viewer.mjs --vroid --url http://127.0.0.1:4173/technical-sign-preview --report assets/previews/TASK-0021-vrm/browser.json --screenshot assets/previews/TASK-0021-vrm/hand.png --full-screenshot assets/previews/TASK-0021-vrm/avatar.png
```

## Kiểm tra và bằng chứng

| Kiểm tra | Kết quả | Trạng thái |
|---|---|---|
| GLB VRoid | Khronos validator ghi 0 lỗi và 8 cảnh báo | PASS |
| Chuyển động export | 36 kênh xoay, đều có thay đổi giữa đầu clip và mẫu gần giữa clip | PASS |
| Đồng bộ, TypeScript, lint, test, build | Bản web khớp staging, 16 test qua, build thành công | PASS |
| Chrome | Phát, dừng, tua, đổi tốc độ, camera, bố cục mobile và chuyển qua lại. Đạt 12/12 | PASS |
| Đánh giá độ chính xác ký hiệu | Chờ đánh giá ngôn ngữ | NOT YET TESTED |

Ảnh và kết quả Chrome trong `assets/previews/TASK-0021-vrm/`. SHA-256 VRM đầu vào `2a0ccd84880b03d7b65503d8b6287f7a97f3bb4fab70a5fd0a47b433c97827f5`. SHA-256 Snow `0298f023675d1fe45056d82d761cf513be7acd54de55e77ac61365497aac8fdd`. SHA-256 VRoid GLB `fadb06a3da7e5ed9995d432376a825a3452ef25c13a4b7a385e43c55f6f24f5e`.

## Giới hạn, Git và nghiệm thu

VRoid dùng vật liệu glTF trong viewer và clip chuyển cử động tay. Mô phỏng tóc, quần áo và biểu cảm nằm ngoài phạm vi. Không có blocker kỹ thuật. Hash commit ghi trong phản hồi cuối.

- [ ] Tải lại trang S001, chọn AvatarSample_A (VRoid), xem ở 1× và 0,5× rồi đổi về Snow.
