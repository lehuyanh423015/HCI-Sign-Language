# Agent Task Protocol

Áp dụng bắt buộc từ TASK-0003.

## Trước khi sửa

1. Ghi task ID, objectives, in/out-of-scope.
2. Đọc `AGENTS.md`, contracts, setup, ownership và report task trước.
3. Ghi branch, commit, remote, `git status`; bảo toàn mọi user change.
4. Ghi runtime/dependency/tool versions và hash binary source liên quan.
5. Tạo task branch theo yêu cầu; không merge/push nếu chưa được phép.

## Khi thực hiện

- Thay đổi tối thiểu, reproducible, không hardcode machine path/credential.
- Tách canonical và generated artifacts; cung cấp sync/check command.
- Binary/model experiment chỉ chạy trên working copy.
- Log command thực sự chạy và outcome. Không biến `SKIPPED`/`NOT YET TESTED` thành PASS.
- Structural, programmatic runtime và human visual verification là ba lớp riêng.

## Report bắt buộc

Tạo/cập nhật `docs/reports/TASK-XXXX-short-description.md` bằng tiếng Việt, giữ technical identifiers/commands tiếng Anh. Report phải có:

1. Task identification, scope/objectives.
2. Initial repository status.
3. Environment/dependency versions.
4. Implemented changes và file list.
5. Commands thực sự chạy.
6. Test matrix với `PASS`/`FAIL`/`SKIPPED`/`NOT YET TESTED`.
7. Evidence/generated artifact paths và hashes khi phù hợp.
8. Known issues/limitations và outstanding blockers.
9. Branch/commit information; nếu report được commit trước final hash, nói rõ và ghi hash trong final response hoặc follow-up commit.
10. Owner manual acceptance checklist.
11. Next recommended tasks; không tự bắt đầu task kế tiếp.

Nếu task bị gián đoạn, tạo partial report với trạng thái thật khi khả thi.

## Trước commit/final

1. Review complete diff và staged diff; loại cache/secret/unrelated changes.
2. Chạy tests phù hợp; đối chiếu source hash/binary preservation.
3. Cập nhật report trước commit.
4. Commit coherent trên task branch; không stage user-owned unrelated changes.
5. Final response ngắn gọn: implemented, verified, manual review, cách chạy, handoff readiness, next step và actual commit hash.
