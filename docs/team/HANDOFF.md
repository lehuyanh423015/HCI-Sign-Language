# Handoff nhanh cho nhóm

## Mỗi người bắt đầu

```cmd
git switch main
git pull --ff-only
git switch -c <branch-name>
npm ci
npm run doctor
```

3D member đọc `SETUP_BLENDER.md`, tạo working copy đúng folder và báo nhóm đang giữ file nào. Web/QA member chạy `npm run check` trước khi push.

## Giao gì và phụ thuộc ai

- **Huy Anh:** master revision + skeleton/preflight record + S001–S003 `.blend`/preview/GLB. Mien phụ thuộc master; Nhat phụ thuộc GLB contract; Thao phụ thuộc preview/evidence.
- **Mien:** S004–S006 source/preview/GLB dựa trên đúng master revision. Huy Anh review technical trước khi Nhat tích hợp.
- **Nhat:** viewer controls, route/UI và browser playback evidence. Cần Huy Anh cung cấp clip/GLB đúng contract và Thao cung cấp metadata approval.
- **Thao:** canonical metadata, reference/evidence, adaptive rules/tests và QA result. Nhat chỉ publish educational mode sau approval.

## Integration

1. PR ngắn, đúng owner, không kèm cache/render tạm.
2. `npm run check`; 3D PR thêm `npm run validate:assets` + manual checklist.
3. Shared contract cần owner + consumer review.
4. Merge vào `main`; thành viên khác rebase/merge main sớm, không sửa binary conflict bằng text merge.

## Báo blocker

Trong group/issue ghi: `BLOCKER`, owner, sign ID/file, master commit/hash, expected/actual, log/screenshot, ảnh hưởng milestone, quyết định cần trước thời điểm nào. Không tự đổi contract hay scope. Ngày 5 dùng evidence thực tế để quyết định 6 hay 3–4 signs.
