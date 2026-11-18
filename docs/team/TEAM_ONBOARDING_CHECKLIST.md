# Checklist onboarding nhóm

Mỗi thành viên copy mục của mình vào Issue/PR và đính kèm output thật. Không tick hộ máy khác.

## Chung

- [ ] `git --version`; clone repository; `git status --short --branch` sạch hoặc thay đổi đã được nhận diện.
- [ ] Đọc `AGENTS.md`, `docs/team/ONBOARDING.md`, `docs/team/GIT_WORKFLOW.md` và guide theo vai trò.
- [ ] Xác nhận không commit credential, cache, user-local path hoặc file không có quyền sử dụng.
- [ ] Ghi OS/tool versions, command, output, blocker và người chịu trách nhiệm.

## Huy Anh / Mien

- [ ] Blender báo `5.2.4 LTS`; MPFB báo `2.0.18`.
- [ ] `certutil -hashfile blender\master\avatar_master.blend SHA256` khớp manifest.
- [ ] Tạo working copy thử bằng script, xác nhận master hash không đổi.
- [ ] Chạy Blender validator; mở template và kiểm tra neutral/timeline.

## Nhat

- [ ] Node/npm đúng `package.json`; `npm ci` hoàn tất.
- [ ] `npm run check` và `npm run build`.
- [ ] Mở `/technical-sign-preview`, kiểm tra playback/camera/warning.

## Thao

- [ ] Có Node/npm nếu trực tiếp validate metadata; nếu không, CI/Nhat chạy giúp và đính kèm report.
- [ ] `npm run validate:data` và `npm run validate:sign-packages`.
- [ ] Reference/evidence có nguồn, quyền sử dụng và trạng thái rõ; không tự đánh `APPROVED`.

Trạng thái onboarding của bốn máy: máy hiện tại `VERIFIED FOR TASK COMMANDS`; ba máy còn lại `PENDING MEMBER CONFIRMATION`.
