# TASK-0014 — Tài khoản người học và quản trị học liệu

- Ngày và múi giờ: 28/11/2026, Asia/Saigon.
- Nhánh và base: codex/task-0014-account-admin / dd26c76.
- Phạm vi: đăng ký, phiên đăng nhập, phân quyền, học liệu quản trị và lưu tiến độ trong SQLite. Trình diễn trên máy cục bộ.
- Tổng thể: PASS cho triển khai và kiểm tra tự động. Nghiệm thu vận hành thực tế đang chờ.

## Tóm tắt

Người học đăng ký bằng email, đăng nhập và được cấp phiên riêng. Backend kiểm tra quyền quản trị, chấm câu trả lời và lưu lịch ôn theo tài khoản. Khu quản trị ghi bản cập nhật trong SQLite, dùng dữ liệu JSON phiên bản Git làm nền. Bản cập nhật đồng thời bị chặn nếu mục đã thay đổi so với lúc mở. Hồ sơ A/B phục vụ mô phỏng cục bộ.

## Repo ban đầu

Nhánh codex/task-0013-viewer-controls ở dd26c76. Remote origin https://github.com/lehuyanh423015/HCI-Sign-Language.git. Thư mục .agents/ do người dùng cài, chưa track. Không có thay đổi source khác.

## Môi trường

Windows, Node 24.21.0 với node:sqlite, npm 11.19.0, React 19.3.1, Vite 8.3.8. Baseline 3D Blender 5.2.4 LTS + MPFB 2.0.18. Master SHA-256 trước và sau: DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC.

## Thay đổi và tệp

- apps/server/{api.mjs,api.d.mts,store.mjs,create-admin.mjs}: API cùng origin, SQLite, phiên HttpOnly, băm mật khẩu scrypt, hạn chế lượt thử và CLI cấp quản trị.
- apps/web/src/app/{Account,App,AppRoutes,LearningState}.tsx, src/main.tsx, src/services/api.ts, src/features/{admin/AdminPage,quiz/QuizPage}.tsx, src/features/lessons/catalog.ts và src/styles/learning.css: biểu mẫu, phân quyền giao diện, đồng bộ tiến độ và UI quản trị.
- apps/web/vite.config.ts và package.json hai cấp: tích hợp API với dev và preview. .gitignore bảo vệ dữ liệu SQLite mặc định khỏi Git. README.md hướng dẫn cấp quản trị.
- tools/{inspect-glb,validate-assets}.mjs dùng chung kiểm tra clip GLB. tools/tests/accounts.test.mjs và apps/web/tests/App.test.tsx kiểm tra API và route.

## Lệnh đã chạy

~~~text
git status -sb
git remote -v
git switch -c codex/task-0014-account-admin
node -v
npm.cmd -v
Get-FileHash blender/master/avatar_master.blend
npm.cmd run build
npm.cmd run dev
npm.cmd run admin:create
npm.cmd run check
node --test tools/tests/accounts.test.mjs
node "$env:TEMP/hci-account-browser-check.mjs"
git diff --check
~~~

## Ma trận kiểm tra

| Kiểm tra | Bằng chứng | Trạng thái |
|---|---|---|
| Quality gate | Build, lint, test và validator tài sản | PASS |
| Phiên và vai trò | HTTP 401/403, chống cấp vai trò qua đăng ký, từ chối origin khác, hết hạn và thu hồi cookie | PASS |
| Gate xuất bản | Từ chối thiếu minh chứng/GLB, câu hỏi biến mất khi ký hiệu về bản nháp, từ chối bản ghi lỗi thời | PASS |
| Tiến độ hai tài khoản và retry | Kiểm thử API, gửi lại cùng attempt giữ nguyên streak | PASS |
| Luồng Chrome | Đăng ký, từ chối người học ở /admin, đăng xuất, quản trị đăng nhập, lưu và tải lại bản nháp, viewport 375 px | PASS |
| Triển khai HTTPS và học liệu giáo dục thật | Chờ cấu hình môi trường và phê duyệt chuyên môn | NOT YET TESTED |

## Bằng chứng

Kiểm thử tích hợp HTTP chạy database trong bộ nhớ và dùng GLB tổng hợp ở thư mục tạm. Tài khoản Chrome QA được cấp trên database tạm, tách khỏi dữ liệu bàn giao. Không bổ sung minh chứng hoặc nhãn duyệt cho S001. Các tệp Blender và GLB nguồn không có trong diff.

## Giới hạn và blocker

Bản giao dùng qua Vite trên máy cục bộ. Chưa có luồng email xác minh hoặc đặt lại mật khẩu. Lịch sử A/B vẫn là dữ liệu mô phỏng trên trình duyệt. Người sở hữu cần tạo admin thật bằng mật khẩu riêng. Dùng cơ sở dữ liệu riêng và cấu hình HTTPS cho môi trường dùng chung. Nội dung giáo dục vẫn chờ kiểm chứng.

## Git và commit

Report viết trước commit. Hash bàn giao ghi trong phản hồi. Không merge hoặc push.

## Checklist nghiệm thu thủ công

- [ ] Tạo admin bằng CLI, đăng nhập và lưu thử bản nháp.
- [ ] Đăng ký hai tài khoản người học và đối chiếu tiến độ.
- [ ] Mở /admin trực tiếp với tài khoản người học để kiểm tra màn hình từ chối.

## Bước bàn giao tiếp theo

Nghiệm thu trên môi trường sử dụng thực tế và xuất bản học liệu khi có phiếu kiểm chứng.

