# TASK-0015 — Dashboard quản trị

- Ngày và múi giờ: 28/11/2026, Asia/Saigon.
- Nhánh và base: codex/task-0015-admin-dashboard từ 104b434.
- Phạm vi: theo dõi bài học, câu hỏi và hoạt động người học trong khu quản trị.

## Tóm tắt

/admin hiển thị tổng số bài học và câu hỏi, số đang xuất bản, số ký hiệu chờ kiểm chứng và tổng tài khoản người học. Bảng có tìm email và phân trang. Một bài đã luyện tương ứng với ký hiệu có tiến độ trả lời trong SQLite. Thời điểm trả lời gần nhất hiển thị theo giờ Việt Nam. /admin/catalog mở trình quản lý học liệu.

## Trạng thái ban đầu và môi trường

Repo ở codex/task-0014-account-admin, remote origin https://github.com/lehuyanh423015/HCI-Sign-Language.git. Thư mục .agents/ chưa track thuộc người dùng. Node 24.21.0, npm 11.19.0, Windows, SQLite tích hợp Node, React/Vite hiện có. Baseline 3D Blender 5.2.4 LTS + MPFB 2.0.18.

## Tệp thay đổi

- apps/server/api.mjs thêm dashboard API sau kiểm tra admin, dùng điều kiện xuất bản hiện có.
- apps/web/src/features/admin/{AdminDashboard,AdminPage}.tsx và apps/web/src/app/{App,AppRoutes}.tsx thiết lập hai màn hình quản trị.
- apps/web/src/styles/learning.css bố trí thẻ số liệu và bảng cuộn trong vùng riêng trên mobile.
- tools/tests/accounts.test.mjs kiểm tra quyền, số liệu, người học chưa hoạt động, lọc và giới hạn trang.
- Báo cáo này ghi trước commit. Hash commit cuối được cung cấp khi bàn giao.

## Lệnh đã thực hiện

~~~powershell
git status -sb
git remote -v
git switch -c codex/task-0015-admin-dashboard
node -v
npm.cmd -v
npm.cmd run lint
npm.cmd run build
npm.cmd test
node "$env:TEMP/hci-dashboard-browser-check.mjs"
Get-FileHash blender/master/avatar_master.blend
git diff --check
~~~

## Ma trận kiểm tra

| Hạng mục | Bằng chứng | Trạng thái |
|---|---|---|
| API và build | Node/Vitest, lint, TypeScript/Vite | PASS |
| Quyền và số liệu | Test API xác minh khách nhận 401, người học nhận 403, loại admin khỏi thống kê, hiển thị đúng tiến độ | PASS |
| Trình duyệt | Chrome thử quyền, tìm email, điều hướng học liệu và kiểm tra tràn ngang ở 375 px | PASS |
| Nghiệm thu trực tiếp với tài khoản thật | Owner thực hiện trên dữ liệu đang sử dụng | NOT YET TESTED |

## Bằng chứng, giới hạn và blocker

Master SHA-256 trước/sau DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC. Chrome sử dụng cơ sở dữ liệu kiểm thử riêng. Danh sách chỉ đếm hoạt động của tài khoản người học lưu trên máy chủ; mô phỏng A/B lưu trong trình duyệt. Chưa có blocker kỹ thuật để dùng trên máy cục bộ.

## Nghiệm thu thủ công và bước bàn giao

- [ ] Đăng nhập bằng admin thật và mở /admin.
- [ ] Tìm email một người học, đối chiếu tiến độ với hoạt động đã thực hiện.
- [ ] Mở Quản lý học liệu từ dashboard.
