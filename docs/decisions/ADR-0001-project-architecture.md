# ADR-0001: Kiến trúc nền tảng dự án

- Trạng thái: Accepted; Blender baseline clause superseded by ADR-0002
- Ngày: 2026-11-17

## Bối cảnh

Nhóm bốn người có 15 ngày, cần phối hợp binary Blender và web, không cần backend. Rủi ro lớn nhất là rig không đồng nhất, asset binary xung đột, metadata bị nhân bản và nội dung chưa xác minh được hiển thị như tài liệu học.

## Quyết định

1. Dùng một Git repository và npm workspaces, duy nhất một React app.
2. Pin exact npm dependency versions và commit `package-lock.json`; cài bằng `npm ci`.
3. Node baseline là major 24 hoặc 26 LTS. File `.nvmrc` khuyến nghị 24.22.2; máy bootstrap được kiểm tra bằng 24.14.1.
4. Giữ Blender baseline 4.5.16 + MPFB tách khỏi Node/System Python. Không upgrade Blender trong task này.
5. Release đầu dùng một self-contained GLB/sign. Không retarget/shared-skeleton runtime.
6. `data/` là canonical; public JSON là generated artifact qua script có validation.
7. LocalStorage lưu adaptive history theo demo user và schema version; không authentication/backend.
8. CI chạy web/data/assets structural checks nhưng không tuyên bố visual/educational approval.

## Hệ quả

- Dễ clone và làm độc lập, ít dependency conflict.
- GLB lớn hơn do lặp model nhưng giảm rủi ro tích hợp trong ba tuần.
- Binary vẫn cần ownership lock và có thể cần Git LFS.
- Blender 4.5.16/MPFB và browser playback phải được xác minh ở task tiếp theo; máy bootstrap hiện chỉ phát hiện Blender 5.2.4 LTS nên 3D baseline đang `FAIL`.
