# Approved master assets

Canonical master hiện tại là `avatar_master.blend`, version `Master Avatar v1.0.0` (Temporary Technical Release).
Chỉ Le Huy Anh cập nhật file này sau coordinated approval; animator luôn tạo working copy.

- `avatar_master.blend`: official shared master, mở ở neutral; giữ reusable Actions được gắn nhãn technical fixture và không assign vào scene.
- `master-avatar.manifest.json`: canonical release manifest, hash, rig/facial inventory, exports và approval states.
- `avatar_master.manifest.json`: compatibility manifest cho tooling cũ, trỏ tới canonical manifest.
- `avatar_master_neutral_candidate.blend`: nguồn candidate TASK-0004 được giữ để truy vết; không tiếp tục dùng làm canonical.
- `../avatar_master.blend`: pre-neutral legacy source được giữ nguyên, không phải official master.

Không rename bone, apply armature transform, đổi rest pose hoặc merge binary `.blend` bằng text tools.

Sáu core `NMM_` targets và eye geometry đã được owner duyệt về appearance/technical development. Linguistic approval: `NOT YET TESTED`.
