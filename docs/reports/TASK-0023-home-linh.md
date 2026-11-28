# TASK-0023 — Thay ảnh trang chủ bằng Linh

Ngày 28/11/2026 theo Asia/Saigon. Trạng thái PASS. Nhánh `nhatdoankhanh/task-0023-home-linh` từ `ac9054d`. Ban đầu chỉ có `.agents/` chưa được Git theo dõi.

## Phạm vi và môi trường

Thay ảnh minh họa ở khối chính của trang chủ. Dùng Chrome headless, Three.js và Node 24. Ảnh được kết xuất trực tiếp từ GLB của Linh ở thời điểm 1,13 giây của clip S001, với camera gần chính diện và nền trong suốt.

## Tệp thay đổi

- `apps/web/public/images/linh-preview.webp` là ảnh 640 × 640, 20.434 byte. SHA-256 `5CE15C05BFF71630A2C195E37537D9E5A12027C4D44F4385C956643765FDDE4D`.
- `LessonPage.tsx` dùng ảnh mới, văn bản thay thế và nhãn Linh. `learning.css` điều chỉnh ảnh trên màn hình hẹp.
- GLB Linh nguồn có SHA-256 `F1B2766B3AD09DC3AD59AE7BFE49090257F4C68D04DF4934A7196056B0070341`. Ảnh cũ có SHA-256 `430B7F4C26986792A7D1E3239B6E060E892087AC340A1621756C7FA92667FA2C`.

## Lệnh đã chạy

```powershell
node assets/previews/TASK-0023-home-linh/render.mjs
node assets/previews/TASK-0023-home-linh/render.mjs --verify
npm run build
git diff --cached --check
```

## Kiểm tra và bằng chứng

| Kiểm tra | Kết quả | Trạng thái |
|---|---|---|
| Tải ảnh trang chủ | URL đúng, ảnh giải mã, alt có tên Linh | PASS |
| Bố cục 1280px và 375px | Quan sát ảnh chụp Chrome. Có ảnh Linh và không tràn ngang. Lần đầu ở 375px bị cắt ảnh, đã sửa kích thước và chạy lại | PASS |
| Build web | Vite và TypeScript hoàn tất | PASS |

Ảnh kiểm tra trong `assets/previews/TASK-0023-home-linh/`. Không có blocker. Hash commit trong phản hồi cuối.

## Nghiệm thu thủ công

- [ ] Mở trang chủ ở máy tính và điện thoại, xác nhận hình Linh đang vẫy tay.
