# ADR-0002: Blender 5.2.4 LTS là production baseline

- Trạng thái: Accepted
- Ngày: 2026-11-17

## Quyết định

Theo quyết định owner trong TASK-0003, Blender 4.5.16 đã bị loại bỏ vĩnh viễn. Toàn bộ 3D production, automation, Action Slots, glTF export và hướng dẫn dùng Blender 5.2.4 LTS với MPFB 2.0.18. Không tìm, cài hoặc yêu cầu 4.5.16.

## Bằng chứng

5.2.4 background/`bpy`/MPFB runtime PASS; controlled finger tests PASS; Action Slot + 30 FPS technical animation được lưu; `ACTIONS` export mode tạo đúng clip; Khronos validation 0 errors; Three.js runtime được kiểm tra trong TASK-0003.

## Hệ quả

Mọi thành viên 3D dùng cùng exact version. Không mở/save source production bằng version khác. Thay baseline tiếp theo cần ADR và technical regression test.
