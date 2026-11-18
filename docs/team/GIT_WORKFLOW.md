# Git workflow cho bốn thành viên

## Branch và ownership

- Shared task: `feat/task-0009-team-onboarding-animation-pipeline`.
- Mỗi ký hiệu: `feat/sign-S001` … `feat/sign-S006` từ `main` mới nhất.
- Huy Anh giữ master lock/integration; Mien không sửa `blender/master/`; Nhat không cần `.blend` cho web thường ngày; Thao sở hữu reference/metadata/evidence gate.

```cmd
git switch main
git pull --ff-only
git switch -c feat/sign-S001
git status --short --branch
```

Không force-push, reset/clean user work, rewrite published history, merge trực tiếp `main`, hoặc ghi đè binary của người khác. Một sign có một animator lock tại một thời điểm.

## Commit và PR

Commit nhỏ, mô tả phạm vi: `feat(sign): animate S001`, `docs(content): add S001 reference evidence`, `fix(viewer): preserve clip replay`. Trước push:

```cmd
npm run validate:sign-packages
npm run check
git status --short
git diff --check
git push -u origin feat/sign-S001
```

PR ghi master tag/hash, sign owner, source/reference status, file/action/GLB hashes, commands thật, `PASS`/`FAIL`/`SKIPPED`/`NOT YET TESTED`, screenshots và blockers. Huy Anh review rig/export, Thao/qualified reviewer review content, Nhat review browser integration.

## Binary và conflict

Git thường hiện đủ cho kích thước hiện tại; không bật/migrate LFS nếu chưa có task/backup/owner approval. Không text-merge `.blend`/`.glb`. Khi conflict, dừng, xác định owner và source hash; giữ bản recovery bằng tên mới nếu cần, không xóa branch hay file người khác.

Chỉ GLB đã qua technical + linguistic + browser gates mới vào lesson production path. Fixture luôn ở `assets/exports/technical/` và preview kỹ thuật.
