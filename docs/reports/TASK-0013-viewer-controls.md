# TASK-0013 — Điều khiển trình xem và tương tác chuột

- Ngày: 28/11/2026, Asia/Saigon.
- Nhánh: codex/task-0013-viewer-controls, base 3aebc7ac353a81fcf35047a09096c0e8cd5f9a91.
- Phạm vi: viewer hoạt ảnh dùng chung, bố cục responsive và kiểm tra trình duyệt. Trạng thái kỹ thuật: PASS.

## Tóm tắt và trạng thái ban đầu

Thanh điều khiển trước đây có mười nút tương đương về thị giác. Nay nhóm phát nằm cạnh thanh tua; chỉnh camera và metadata mở theo nhu cầu. Nhánh gốc codex/task-0012-learning-ui. Remote origin https://github.com/lehuyanh423015/HCI-Sign-Language.git. Thư mục .agents/ chưa track thuộc người dùng.

## Môi trường và thay đổi

Node 24.21.0, npm 11.19.0, Three.js/OrbitControls hiện có, React, Lucide và Chrome headless trên Windows. Baseline Blender 5.2.4 LTS + MPFB 2.0.18. Không chỉnh sửa binary.
- apps/web/src/components/viewer/TechnicalViewer.tsx: tua và dừng tại thời điểm đã chọn, biểu tượng, nhóm nút, chỉ dẫn chuột/cảm ứng, điều chỉnh độ nhạy camera.
- apps/web/src/styles/learning.css: con trỏ kéo/thả, trạng thái đang bật, kích thước nút và lưới trên điện thoại.
- tools/test-technical-viewer.mjs: phát sinh sự kiện chuột thật qua CDP, đối chiếu hình render khi đang dừng, kiểm tra tràn ngang và kích thước nút.
- docs/reports/artifacts/TASK-0013/: viewer.json, controls.png, mobile.png.

## Lệnh thực hiện

~~~powershell
git status -sb
git rev-parse HEAD
git remote -v
git switch -c codex/task-0013-viewer-controls
Get-FileHash blender/master/avatar_master.blend
node -v
npm.cmd -v
npm.cmd run build
npm.cmd run lint
npm.cmd test
node tools/test-technical-viewer.mjs --url http://localhost:5173/technical-sign-preview --report docs/reports/artifacts/TASK-0013/viewer.json --screenshot docs/reports/artifacts/TASK-0013/controls.png --mobile-screenshot docs/reports/artifacts/TASK-0013/mobile.png
git diff --check
~~~

## Ma trận kiểm tra và bằng chứng

| Kiểm tra | Bằng chứng | Trạng thái |
|---|---|---|
| Build TypeScript/Vite và lint | Exit code 0 | PASS |
| Test Node/Vitest | 7 + 8 test | PASS |
| Phát, tạm dừng, phát lại, tốc độ, lặp, hai góc camera | viewer.json | PASS |
| Tua bằng chuột, kéo xoay và cuộn thu phóng trên canvas | mouse_seek, mouse_drag_and_wheel | PASS |
| Chrome viewport 375 px, nút từ 44 px, không tràn ngang | mobile_controls_fit, mobile.png | PASS |
| Cử chỉ trên điện thoại thật và nghiệm thu owner | Cần thao tác thực tế | NOT YET TESTED |

Master SHA-256: DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC.

## Giới hạn, Git và blockers

Build còn cảnh báo kích thước chunk trên 500 kB. S001 đang chờ xác minh ngôn ngữ. Không có blocker cho bản chạy local. Report tạo trước commit cuối; hash bàn giao trong phản hồi.

## Nghiệm thu thủ công và bước tiếp theo

- [ ] Owner kéo avatar, cuộn để nhìn tay, tua đến tư thế và chọn Về góc ban đầu.
- [ ] Kiểm tra vuốt/chụm hai ngón và độ nhạy trên thiết bị cảm ứng thật.

Bước tiếp theo là thu nhận phản hồi thao tác trực tiếp từ người dùng.
