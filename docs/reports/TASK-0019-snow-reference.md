# TASK-0019 — Hiệu chỉnh đường vẫy tay theo tham chiếu S001

Ngày 28/11/2026, Asia/Saigon. Trạng thái kỹ thuật PASS. Phạm vi là bản xem trước S001 trên Snow.

## Tóm tắt và nguồn

Mục từ “chào” vùng Bình Dương mô tả một tay giơ ngang đầu, lòng bàn tay hướng ra trước và vẫy nhẹ. S001 của dự án dùng hai tay. Quỹ đạo được hiệu chỉnh theo năm mốc cổ tay trong `blender/working/signs/S001/refinements/task-0011b/reference-landmark-estimates.json` đã đo từ video của dự án. Không mở lại được video gốc trực tuyến trong lần này. [Mô tả của từ điển](https://tudienngonngukyhieu.com/tu-ngu/chao-2470) · [Video tham chiếu dự án](https://www.youtube.com/watch?v=4avGnxaLmb0)

## Trạng thái ban đầu, môi trường và Git

Base `578800b`, nhánh mới `nhatdoankhanh/task-0019-snow-reference`, thư mục người dùng `.agents/` ngoài Git. Blender 5.2.4 LTS Windows, Node và Chrome headless. Dùng bản sao Snow. Hash commit cuối ghi trong phản hồi.

## Thay đổi và tệp

`blender/scripts/export_snow_s001.py` chuyển thời gian trong video sang frame, quy đổi khoảng cách ngang theo bề rộng vai Snow và điều chỉnh hướng cẳng tay. Nội suy giữa năm mốc giúp cổ tay đi từ ngoài vào gần thân rồi trở ra. Bản GLB mới ở `assets/exports/signs/staging/S001-snow.glb`, SHA-256 `162ebb9fa525dbe134cc61d8a466070576019e6b616a35792fa5dd8b963a7544`. Bản trước có SHA-256 `60cb08e2a5b1a021c302bed0cdb003b294a1a5dd705734d4238a26938eb78e0f`.

## Lệnh đã chạy

```powershell
& "$env:TEMP/hci-snow-blender-524/blender-5.2.4-windows-x64/blender.exe" -b assets/previews/TASK-0016-snow/input/snow_v4.2.blend --disable-autoexec --python-exit-code 1 --python blender/scripts/export_snow_s001.py -- --source blender/working/signs/S001/refinements/task-0011b/S001_refined.blend --working-copy assets/previews/TASK-0019-snow/S001-snow.blend --output assets/previews/TASK-0019-snow/S001-snow.glb
Copy-Item assets/previews/TASK-0019-snow/S001-snow.glb assets/exports/signs/staging/S001-snow.glb
npm run sync:technical-assets
npm run sync:technical-assets:check
node tools/test-technical-viewer.mjs --url http://127.0.0.1:4173/technical-sign-preview --report assets/previews/TASK-0019-snow/browser.json --screenshot assets/previews/TASK-0019-snow/hand.png --full-screenshot assets/previews/TASK-0019-snow/web.png
```

## Kiểm tra, bằng chứng và giới hạn

| Kiểm tra | Kết quả | Trạng thái |
|---|---|---|
| Sai lệch ngang trung bình, hai tay ở năm mốc | Giảm từ 0,116 xuống 0,012 lần bề rộng vai. Các mốc tham chiếu có độ bất định khoảng ±0,10 | PASS |
| Giao nhau bên trong mỗi tay | 2.409 tam giác mỗi bên, 119 mẫu, 0 cặp giao nhau | PASS |
| GLB, đồng bộ và viewer | 0 lỗi Khronos, 11 cảnh báo, 11/11 kiểm tra Chrome đạt | PASS |
| Người dùng đánh giá độ tự nhiên, chuyên gia xác minh ký hiệu | Đang chờ | NOT YET TESTED |

Bằng chứng cục bộ trong `assets/previews/TASK-0019-snow/` gồm bản Blender, GLB, `snow-motion-review.json`, `browser.json` và ảnh viewer. Mốc chính diện chỉ mô tả vị trí ngang. Không có blocker kỹ thuật.

## Nghiệm thu thủ công

- [ ] Xem ở 1× để đánh giá nhịp vẫy và hạ tay.
- [ ] Đối chiếu với người thực hiện trước khi duyệt ngôn ngữ.
