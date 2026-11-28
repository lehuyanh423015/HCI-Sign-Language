# TASK-0018 — Chỉnh nhịp vẫy tay của Snow trong S001

- Ngày 28/11/2026, Asia/Saigon. Nhánh `nhatdoankhanh/task-0018-snow-wave`, base `c57f753`. Trạng thái kỹ thuật PASS.
- Phạm vi là chuyển động hai tay trong bản xem trước “Xin chào”.

## Tóm tắt

Thu hai tay về gần thân lúc bắt đầu và hạ tay, đưa cẳng tay về trước khi nâng. Làm mượt chuyển hướng qua năm mẫu xoay, cho cổ tay theo sau cánh tay và cho tay trái chậm hơn tay phải 0,75 frame. Đây là lựa chọn diễn hoạt cho bản mẫu hai tay theo ghi chép tham chiếu tại `blender/working/signs/S001/reference-analysis.md`.

## Trạng thái ban đầu và môi trường

Nhánh ban đầu là `nhatdoankhanh/task-0017-snow-avatar`, chỉ có `.agents/` ngoài Git. Remote origin là lehuyanh423015/HCI-Sign-Language. Dùng Blender portable 5.2.4 LTS, build cd5dc428cce1 trên Windows và Chrome headless. Rig Snow có sẵn nên không cần nạp MPFB.

## Thay đổi và tệp

Chỉnh bước retarget ở `blender/scripts/export_snow_s001.py` và thay GLB staging `assets/exports/signs/staging/S001-snow.glb`. Bản cũ có trong Git tại base. SHA-256 trước là `1321b0f6341469d5eebfd1a656334c240423ff0949d0318e22f24b4384abd69c`, sau là `60cb08e2a5b1a021c302bed0cdb003b294a1a5dd705734d4238a26938eb78e0f`.

## Lệnh đã chạy

```powershell
& "$env:TEMP/hci-snow-blender-524/blender-5.2.4-windows-x64/blender.exe" -b assets/previews/TASK-0016-snow/input/snow_v4.2.blend --disable-autoexec --python-exit-code 1 --python blender/scripts/export_snow_s001.py -- --source blender/working/signs/S001/refinements/task-0011b/S001_refined.blend --working-copy assets/previews/TASK-0018-snow/S001-snow.blend --output assets/previews/TASK-0018-snow/S001-snow.glb
Copy-Item assets/previews/TASK-0018-snow/S001-snow.glb assets/exports/signs/staging/S001-snow.glb
npm run sync:technical-assets
npm run sync:technical-assets:check
node tools/test-technical-viewer.mjs --url http://127.0.0.1:4173/technical-sign-preview --report assets/previews/TASK-0018-snow/browser.json --screenshot assets/previews/TASK-0018-snow/hand.png --full-screenshot assets/previews/TASK-0018-snow/web.png
```

## Ma trận kiểm tra và bằng chứng

| Kiểm tra | Kết quả | Trạng thái |
|---|---|---|
| Clip S001_MAIN và schema GLB | inspectGlb đọc được clip, Khronos ghi 0 lỗi và 11 cảnh báo | PASS |
| Vị trí trung tính | Khoảng cách ngang từ cổ tay phải tới trục giữa giảm từ 0,473 xuống 0,361 đơn vị Blender | PASS |
| Giao nhau bên trong mỗi bàn tay | BVH trên 2.409 tam giác mỗi bên tại 119 mẫu từ frame 1 đến 60, không có cặp giao nhau giữa các tam giác rời đỉnh | PASS |
| Đồng bộ web và phát trong Chrome | Hash khớp, 11/11 kiểm tra viewer đạt | PASS |
| Người dùng duyệt cảm giác tự nhiên và chuyên gia duyệt ngôn ngữ | Chờ đánh giá | NOT YET TESTED |

Bằng chứng cục bộ trong `assets/previews/TASK-0018-snow/` gồm bản Blender, GLB, hai ảnh viewer, `browser.json` và `snow-motion-review.json`.

## Giới hạn, Git và nghiệm thu

Phép dò giao nhau chỉ bao phủ bên trong từng bàn tay. Không có blocker kỹ thuật cho bản xem trước. Hash commit ghi trong phản hồi cuối.

- [ ] Xem chuyển tiếp nâng, đổi hướng và hạ tay ở 1×, sau đó xem chậm ở 0,5×.
- [ ] Đối chiếu với video tham chiếu khi duyệt nội dung ngôn ngữ.
