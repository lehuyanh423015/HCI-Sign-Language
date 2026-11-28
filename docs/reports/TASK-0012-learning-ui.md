# TASK-0012 — Giao diện học và ôn tập bằng avatar 3D

- Ngày: 28/11/2026, Asia/Saigon.
- Nhánh: codex/task-0012-learning-ui. Base: be1062331cddd6b58dfbabe9abf8e453bbf07c00.
- Phạm vi: frontend React, viewer, lưu lịch sử cục bộ, mô phỏng A/B và QA. Mục tiêu là demo chức năng trên localhost.
- Trạng thái triển khai kỹ thuật: PASS. Nghiệm thu với người học: NOT YET TESTED.

## Tóm tắt

Trang chủ ưu tiên xem bản mẫu khi chưa có học liệu đã duyệt. Với dữ liệu approved, ứng dụng hiển thị thư viện, bài học, câu hỏi, kết quả và lịch ôn. S001 nằm ở khu kỹ thuật. Hai hoạt ảnh hình học riêng cho phép thử quiz và bốn luật adaptive trong khi chờ kiểm chứng.

## Trạng thái ban đầu

Nhánh main cùng commit với origin/main trong checkout; origin là https://github.com/lehuyanh423015/HCI-Sign-Language.git. Thư mục .agents/ chưa track thuộc người dùng. Web chạy bằng Vite trên localhost:5173. Dữ liệu canonical có 6 mục theo kế hoạch và 0 câu hỏi.

## Môi trường và phụ thuộc

Windows, Node v24.21.0, npm 11.19.0, Vite 8.3.8. Frontend dùng Tailwind 4.3.5, Lucide React 1.82.0, font Inter tự phục vụ. Baseline nguồn 3D là Blender 5.2.4 LTS + MPFB 2.0.18. Dùng GLB có sẵn.

## Thay đổi và danh sách tệp

- docs/design/TASK-0012-learning-ui.md ghi hệ thống thiết kế trước bước viết frontend.
- apps/web/src/app/{App,AppRoutes,LearningState}.tsx: điều hướng, phục hồi hồ sơ, tải JSON, lọc nội dung và lưu tiến độ.
- apps/web/src/features/lessons/{catalog.ts,LessonPage.tsx}, quiz/QuizPage.tsx, review/ReviewPage.tsx, adaptive/history.ts: luồng học, quiz, mô phỏng và lịch ôn. Khoảng giãn 1/3/7 ngày là cấu hình demo.
- apps/web/src/components/viewer/TechnicalViewer.tsx, features/technical/SignAnimationPreviewPage.tsx: trạng thái tải/lỗi, phát, camera, nút thay thế thao tác kéo và giao diện xem thử.
- apps/web/src/styles/learning.css, src/main.tsx, index.html, package.json, vite.config.ts và package-lock.json: responsive, font, icon và build. apps/web/public/images/avatar-preview.webp trích ảnh avatar từ contact sheet v4 thuộc repo.
- apps/web/tests/{App,adaptive}.test.ts(x), tools/test-technical-viewer.mjs và docs/reports/artifacts/TASK-0012/: kiểm thử route, luật ôn tập, camera và ảnh chụp trình duyệt.

## Lệnh đã chạy

~~~powershell
git status -sb
git remote -v
git rev-parse HEAD
git switch -c codex/task-0012-learning-ui
node -v
npm.cmd -v
Get-FileHash blender/master/avatar_master.blend
npm.cmd install -w @hci-sign/web lucide-react tailwindcss @tailwindcss/vite @fontsource/inter --no-fund --no-audit
npm.cmd run build
npm.cmd run lint
npm.cmd run check
node "$env:TEMP/hci-ui-0012-qa.mjs"
node tools/test-technical-viewer.mjs --url http://localhost:5173/technical-sign-preview --report docs/reports/artifacts/TASK-0012/viewer.json --screenshot docs/reports/artifacts/TASK-0012/viewer.png
git diff --check
~~~

## Ma trận kiểm tra

| Kiểm tra | Bằng chứng | Trạng thái |
|---|---|---|
| Quality gate toàn repo | Typecheck, lint, 7 test Node + 8 test web, build, validators dữ liệu/GLB/master | PASS |
| Trang chủ ở 375/768/1440 CSS px | Chrome headless, kiểm tra tràn ngang và ảnh chụp | PASS |
| Thư viện rỗng khi chưa có học liệu approved | runtime.json | PASS |
| Hai câu mô phỏng, kết quả, lịch sử, tách A/B qua reload | runtime.json | PASS |
| Hoàn tất một lượt ôn bằng bàn phím | Tab, Space, Enter; runtime.json | PASS |
| GLB S001 mobile; playback, lặp, tốc độ và camera trên desktop | runtime.json, viewer.json | PASS |
| Nghiệm thu trực tiếp trên điện thoại thật, xác minh ngôn ngữ, hiệu quả học | Cần người kiểm chứng và người học | NOT YET TESTED |

Lần đầu chạy check trong sandbox gặp spawn EPERM. Chạy lại với quyền tạo tiến trình đã hoàn tất. QA ban đầu phát hiện vấn đề focus, biên khung hình và bài test tự phát khi máy bật giảm chuyển động. Đã chỉnh focus, khung camera, điều kiện mô phỏng media và chạy lại. Viewer tạm dừng khi người dùng chọn giảm chuyển động.

## Bằng chứng và giới hạn

Ảnh home-1440.png, home-768.png, home-375.png, s001-mobile.png, viewer.png và hai tệp JSON trong docs/reports/artifacts/TASK-0012/. SHA-256 avatar_master.blend đối chiếu trước/sau: DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC. Bản build có cảnh báo chunk JS trên 500 kB. Kiểm tra trình duyệt hiện dùng viewport mô phỏng. Luồng giáo dục với ký hiệu được chuyên môn phê duyệt còn phụ thuộc nội dung và câu hỏi canonical. Kết quả mô phỏng chỉ minh chứng chức năng.

## Git và bàn giao

Report được lập trước final commit; hash commit đi kèm trả lời bàn giao. Nhánh local dành cho task; không merge hoặc push.

## Checklist nghiệm thu thủ công của owner

- [ ] Mở trang chủ ở điện thoại thật, kiểm tra mặt và hai tay trong suốt clip, bật lặp và tốc độ 0,5×.
- [ ] Chọn A, làm mô phỏng, tải lại và chuyển sang B để đối chiếu lịch ôn.
- [ ] Chạy thử với học liệu đã duyệt khi có đủ bằng chứng, ghi lỗi thao tác và thời gian thực hiện.

## Task đề xuất tiếp theo

Thu thập bằng chứng kiểm chứng S001 và thử nghiệm với người học khi đã có học liệu approved.
