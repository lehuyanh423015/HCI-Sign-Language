# Agent instructions

Mọi coding Agent làm việc trong repository này phải đọc và tuân thủ `docs/workflows/AGENT_TASK_PROTOCOL.md`.

Yêu cầu bắt buộc:

- Bảo toàn user changes và binary source; không reset/clean/merge/push nếu task không cho phép.
- Baseline 3D là Blender 5.2.4 LTS + MPFB 2.0.18; không yêu cầu Blender 4.5.16.
- Không gọi technical fixture hoặc nội dung chưa duyệt là Ngôn ngữ Ký hiệu Việt Nam đã xác minh.
- Mỗi task từ TASK-0003 phải tạo/cập nhật `docs/reports/TASK-XXXX-short-description.md` bằng tiếng Việt trước final commit.
- Chỉ ghi `PASS` cho check đã thực sự chạy; dùng `FAIL`, `SKIPPED`, `NOT YET TESTED` chính xác.
- Dùng template `docs/reports/TASK_REPORT_TEMPLATE.md`; report phải độc lập, có commands, evidence, Git info, blockers và manual acceptance.
