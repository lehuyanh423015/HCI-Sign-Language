# Tổng quan kiến trúc

## Mục tiêu

Kiến trúc tối thiểu cho demo 15 ngày: một repository, một React web app, file JSON và LocalStorage, cùng pipeline Blender → GLB → Three.js. Không backend, database, Docker, authentication, camera recognition hoặc machine learning.

## Luồng chính

1. Thao cập nhật nguồn canonical trong `data/` và evidence; schema chặn trạng thái `approved` thiếu thông tin.
2. Huy Anh/Mien tạo animation từ cùng master rig, xuất một GLB tự chứa cho mỗi sign và preview front/side.
3. Script kiểm tra cấu trúc GLB, clip, mesh/skin và skeleton signature; kiểm tra hình ảnh vẫn bắt buộc bằng mắt/browser.
4. Nhat tích hợp GLB qua boundary `components/viewer/`, chỉ hiển thị giáo dục khi metadata là `approved`.
5. Adaptive module đọc/ghi lịch sử từng demo user trong LocalStorage và áp dụng pure rules AD-01–AD-04.

## Quyết định đơn giản hóa

- npm workspaces với một app `apps/web`; dependency và lockfile ở repository root.
- Một GLB tự chứa cho mỗi sign trong release đầu, tránh runtime skeleton retargeting.
- `data/` là nguồn sự thật; `npm run sync:data` tạo web copy.
- CI không phụ thuộc Blender hoặc MPFB; 3D preflight chạy riêng trên máy 3D.
- Asset binary không merge. Git LFS chỉ bật sau khi cả nhóm xác nhận đã cài.

Chi tiết quyết định tại [ADR-0001](../decisions/ADR-0001-project-architecture.md).
