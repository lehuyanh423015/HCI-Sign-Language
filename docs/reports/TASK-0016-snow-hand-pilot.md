# TASK-0016 — Thử tư thế bàn tay trên rig Snow

- Ngày và múi giờ — 28/11/2026, Asia/Saigon
- Branch và base commit — `nhatdoankhanh/task-0016-snow-pilot` từ `main` tại `a7d9c29`
- Phạm vi — Thử nắm tay, gập ngón trỏ, gập ngón cái trên hai tay của bản sao Snow v4.2. Clip S001, GLB và tích hợp ứng dụng nằm ngoài lần thử này.
- Trạng thái tổng thể — PARTIAL

## Tóm tắt

30 điều khiển FK của Snow nhận keyframe và làm biến dạng mesh `GEO-snow-body`. Gập riêng ngón trỏ và ngón cái di chuyển đúng đầu ngón mục tiêu trên hai tay. Phép dò giao nhau phát hiện 325 cặp tam giác ở tư thế nắm tay và 14 cặp ở tư thế gập ngón cái trên mỗi tay. Các tư thế này là dữ liệu thử kỹ thuật. Việc xác minh Ngôn ngữ Ký hiệu Việt Nam nằm ngoài phạm vi.

## Trạng thái kho ban đầu

`main` ở `a7d9c29`. Có thư mục chưa theo dõi `.agents/` của người dùng. Remote `origin` là `https://github.com/lehuyanh423015/HCI-Sign-Language.git`.

## Môi trường và phụ thuộc

- Windows x64, Blender portable 5.2.4 LTS, build `cd5dc428cce1`. SHA-256 của gói tải xuống khớp tệp checksum do Blender công bố.
- Baseline của dự án là Blender 5.2.4 LTS và MPFB 2.0.18. Lần thử này xoay các điều khiển có sẵn của Snow nên không nạp MPFB. Blender chạy với `--disable-autoexec`.
- Nguồn — Snow Rig (CC) Blender Foundation | studio.blender.org. [Trang Snow v4](https://studio.blender.org/characters/snow/v4/)

## Nội dung thực hiện

Script xác định 15 điều khiển ngón tay mỗi bên, thử trục cục bộ của từng khớp dựa trên hướng gập về lòng bàn tay và giữ quaternion trung tính của Snow. Script áp dụng góc từ `technical-hand-poses.json` và tạo action `TECH_SNOW_HAND_PILOT`. Các frame 1, 16, 31, 46 và 61 lần lượt tương ứng với tư thế trung tính, nắm tay, gập ngón trỏ, gập ngón cái và trở về trung tính.

## Tệp tạo và sửa

- `blender/scripts/preview_snow_hand_poses.py` tạo bản Blender, số đo JSON và ảnh Workbench tùy chọn.
- `docs/reports/TASK-0016-snow-hand-pilot.md` ghi kết quả thử nghiệm.
- Bản sao Snow, texture và kết quả nằm trong `assets/previews/TASK-0016-snow/`, ngoài Git.

## Lệnh đã chạy

Các lệnh dưới đây dùng đường dẫn tương đối với thư mục gốc repo và biến `$blender` trỏ tới Blender portable.

```powershell
git status --short --branch
git remote -v
$blender = "$env:TEMP/hci-snow-blender-524/blender-5.2.4-windows-x64/blender.exe"
& $blender --version
& $blender -b assets/previews/TASK-0016-snow/input/snow_v4.2.blend --disable-autoexec --python-exit-code 1 --python blender/scripts/preview_snow_hand_poses.py -- --poses blender/poses/technical-hand-poses.json --output assets/previews/TASK-0016-snow/output --render
Get-FileHash -Algorithm SHA256 -LiteralPath "$env:USERPROFILE/Downloads/Snow_v4.2/Snow/snow_v4.2.blend", "blender/master/avatar_master.blend", "assets/previews/TASK-0016-snow/output/snow-hand-pilot.blend"
git diff --cached --check
```

Đã chạy Blender headless trên tệp kết quả với `--python-expr` để kiểm tra các frame đã lưu, đường dẫn texture và giao nhau của mesh. Phép dò dùng `BVHTree.FromPolygons` với epsilon bằng 0 và bỏ qua cặp tam giác dùng chung đỉnh. Vùng lấy mẫu cách gốc ngón trỏ dưới 0,16 đơn vị cục bộ của mesh trên mỗi tay. So sánh kết quả ở frame 16, 31 và 46 với frame trung tính 1.

## Ma trận kiểm tra

| Kiểm tra | Bằng chứng | Trạng thái |
|---|---|---|
| Cấu trúc rig và action đã lưu | 30 điều khiển FK, action mở lại được trong Blender | PASS |
| Biến dạng mesh | Mỗi tay có lần lượt 1.267, 261 và 312 đỉnh dịch chuyển ở ba tư thế. Frame 61 có 0 đỉnh dịch chuyển so với frame 1 | PASS |
| Gập riêng ngón trỏ và ngón cái | Đầu ngón mục tiêu dịch chuyển, các đầu ngón còn lại giữ nguyên trong ngưỡng kiểm tra | PASS |
| Đường dẫn texture khi mở bản thử | Danh sách tệp và ô UDIM thiếu rỗng | PASS |
| Render và xem ảnh tĩnh | 16 ảnh gồm mu tay và lòng bàn tay của hai bên ở bốn frame | PASS |
| Giao nhau tại frame 31 | 0 cặp tam giác trong vùng lấy mẫu trên mỗi tay | PASS |
| Giao nhau tại frame 16 và 46 | Lần lượt 325 và 14 cặp trên mỗi tay, so với 0 ở frame 1 | FAIL |
| Kiểm tra giao nhau trong các frame chuyển tiếp | Chỉ dò tại các frame đã nêu | NOT YET TESTED |
| Clip S001, GLB và ứng dụng | Ngoài phạm vi lần thử | SKIPPED |

## Bằng chứng và tệp sinh ra

Trong `assets/previews/TASK-0016-snow/output/`:

- `snow-hand-pilot.blend` — SHA-256 `4E3C4C3F660F384200BA49EDFFBFBAA96FC1A4C2D16FBBC89E18445EDB31FA25`.
- `snow-hand-pilot.json` — Trục đo được, độ dịch chuyển từng đầu ngón và số đỉnh dịch chuyển ở từng frame.
- `snow-hand-review.jpg` — Bảng ảnh ghép từ 16 góc nhìn xuất ra.

SHA-256 trước và sau của Snow nguồn đều là `80FD0A81BCA90F0EFDCDCB98422DF0E198AE57F4A1C239E13FB795922779B1FC`. Hash của `blender/master/avatar_master.blend` trước và sau đều là `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC`.

## Giới hạn và vấn đề đã biết

Ảnh dùng Blender Workbench để quan sát hình học. Kiểm tra đường dẫn texture chỉ xác nhận khả năng tìm thấy tệp. Số cặp tam giác là số đo trong vùng lấy mẫu và không biểu thị số điểm lỗi độc lập hoặc mức độ nghiêm trọng.

## Thông tin Git

Commit của lần thử nằm trên `nhatdoankhanh/task-0016-snow-pilot`. Hash commit được ghi trong phản hồi sau khi commit.

## Vướng mắc còn lại

Tư thế nắm tay và gập ngón cái cần chỉnh góc theo hình học Snow trước khi dùng các tư thế đó trong clip.

## Checklist nghiệm thu thủ công

- [ ] Mở `snow-hand-pilot.blend` trong Blender 5.2.4 LTS và kiểm tra hai tay ở các frame 1, 16, 31, 46 và 61.
- [ ] Xoay góc nhìn quanh bàn tay ở frame 16 và 46 để đánh giá vị trí xuyên lưới.
- [ ] So sánh cận cảnh các frame với bảng `snow-hand-review.jpg`.

## Công việc kế tiếp đề xuất

Hiệu chỉnh góc nắm tay và ngón cái cho Snow, sau đó kiểm tra lại ở keyframe và trong chuyển động trước khi thử S001.
