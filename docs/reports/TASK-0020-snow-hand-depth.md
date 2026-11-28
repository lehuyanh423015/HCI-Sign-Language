# TASK-0020 — Chỉnh tay Snow ngả về sau trong S001

Ngày 28/11/2026, Asia/Saigon. Trạng thái kỹ thuật PASS. Base `0cd1c34`, nhánh `nhatdoankhanh/task-0020-snow-hand-depth`. Ban đầu chỉ có `.agents/` ngoài Git.

## Phạm vi và thay đổi

Chỉnh góc nâng cánh tay, cẳng tay và hướng trục cổ tay đến gốc ngón trong `blender/scripts/export_snow_s001.py`. Độ chỉnh tăng dần khi giơ tay và giảm khi hạ tay. Hướng trước của Snow là -Y. Mức nghiêng nhẹ ra trước là lựa chọn diễn hoạt theo phản hồi người dùng. Xuất lại `assets/exports/signs/staging/S001-snow.glb` bằng Blender 5.2.4 LTS, SHA-256 `0298f023675d1fe45056d82d761cf513be7acd54de55e77ac61365497aac8fdd`.

## Lệnh đã chạy

```powershell
& "$env:TEMP/hci-snow-blender-524/blender-5.2.4-windows-x64/blender.exe" -b assets/previews/TASK-0016-snow/input/snow_v4.2.blend --disable-autoexec --python-exit-code 1 --python blender/scripts/export_snow_s001.py -- --source blender/working/signs/S001/refinements/task-0011b/S001_refined.blend --working-copy assets/previews/TASK-0020-snow/S001-snow.blend --output assets/previews/TASK-0020-snow/S001-snow.glb
Copy-Item assets/previews/TASK-0020-snow/S001-snow.glb assets/exports/signs/staging/S001-snow.glb
npm run sync:technical-assets
npm run sync:technical-assets:check
node tools/test-technical-viewer.mjs --url http://127.0.0.1:4173/technical-sign-preview --report assets/previews/TASK-0020-snow/browser.json --screenshot assets/previews/TASK-0020-snow/hand.png
```

## Kiểm tra và bằng chứng

| Kiểm tra | Kết quả | Trạng thái |
|---|---|---|
| Góc nghiêng nhìn từ bên | Đo hướng từ cổ tay đến trung điểm hai gốc ngón trỏ và út ở frame 16, 24, 32, 41, 47. Frame 32 trước đây ngả sau 31,9° trái và 33,2° phải. Bản mới nghiêng trước 5,9° và 5,7°. Cổ tay ở trước mặt phẳng vai tại cả năm mốc | PASS |
| Render cùng góc tại frame 32 | Hai ảnh `side-frame32.png` trong thư mục preview TASK-0019 và TASK-0020 | PASS |
| GLB và phát web | 0 lỗi Khronos, 11 cảnh báo. Hash web khớp staging. Chrome đạt 11/11 | PASS |
| Xác minh ngôn ngữ | Chờ người đánh giá | NOT YET TESTED |

## Giới hạn và nghiệm thu

Tư liệu chính diện chưa cho góc sâu chuẩn. Không có blocker cho bản xem trước. Hash commit trong phản hồi cuối.

- [ ] Xem S001 từ bên và từ phía trước ở tốc độ 1× để duyệt độ nghiêng.
