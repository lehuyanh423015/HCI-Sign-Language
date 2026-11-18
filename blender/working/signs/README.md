# Sign production workspaces

`S001`–`S006` là mã kỹ thuật, chưa phải tên hay ý nghĩa ký hiệu. Mỗi thư mục chứa metadata canonical và các thư mục `references/`, `evidence/`, `exports/`, `previews/`. Không commit nội dung reference khi chưa có quyền sử dụng; ghi nguồn và quyền truy cập trong `sign.json`.

Không tạo `animation.blend` thủ công bằng cách save đè master. Dùng lệnh trong `docs/contracts/sign-animation-production-contract.md`.
