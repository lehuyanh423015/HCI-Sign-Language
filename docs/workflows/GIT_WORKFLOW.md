# Git workflow

`main` là integration branch luôn hướng tới build được. Không push trực tiếp vào `main` cho công việc thông thường; dùng short-lived branch và PR khi thực tế cho phép. TASK-0001 không tạo remote.

## Branch names

- `feat/3d-foundation`, `feat/3d-huy-anh`, `feat/3d-mien`
- `feat/frontend`, `feat/adaptive-qa`
- `fix/<scope>-<short-description>`, `docs/<topic>`

Một branch/PR nên có một mục tiêu và sống tối đa vài ngày. Đồng bộ `main` trước khi bắt đầu và trước merge.

## Commit và PR checklist

- [ ] Đúng owner đã review; shared contract có consumer review.
- [ ] `npm ci` hoạt động từ lockfile và `npm run check` được chạy.
- [ ] Không có secret, cache, temp render, fake reference/reviewer/approval.
- [ ] Binary có owner lock, naming đúng và evidence/size hợp lý.
- [ ] UI ghi rõ placeholder/unverified content.
- [ ] PR nêu test thực sự chạy và mục `NOT YET TESTED`.

## Conflict

Text: dừng, hiểu thay đổi hai phía, phối hợp owner, sửa và chạy lại check. Không dùng `--ours/--theirs` mù quáng. `.blend`, `.glb`, `.mp4` không merge: xác định file canonical với hai tác giả, giữ bản còn lại dưới tên backup ngoài production, rồi owner re-apply thay đổi cần thiết. Không xóa source asset để “giải quyết” conflict.

## Git LFS

`.gitattributes` đã đánh binary nhưng LFS lines đang comment. Chỉ bật khi cả bốn máy/CI có Git LFS và remote support:

```cmd
git lfs install
git lfs version
```

Sau quyết định chung, uncomment patterns trong một PR riêng. Không migrate history trong deadline nếu chưa backup/đồng ý. Với file nhỏ có thể commit Git thường; theo dõi kích thước repo và tránh duplicate.
