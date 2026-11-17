# Approved master assets

Canonical master hiện tại là `avatar_master.blend`, version `Master Avatar v1.0.0-rc.1`.
Chỉ Le Huy Anh cập nhật file này sau coordinated approval; animator luôn tạo working copy.

- `avatar_master.blend`: official shared master release candidate, không chứa technical/sign action.
- `avatar_master.manifest.json`: hash, rig/facial inventory và validation metadata.
- `avatar_master_neutral_candidate.blend`: nguồn candidate TASK-0004 được giữ để truy vết; không tiếp tục dùng làm canonical.
- `../avatar_master.blend`: pre-neutral legacy source được giữ nguyên, không phải official master.

Không rename bone, apply armature transform, đổi rest pose hoặc merge binary `.blend` bằng text tools.
