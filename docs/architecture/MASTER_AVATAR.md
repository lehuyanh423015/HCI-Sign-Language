# Master Avatar v1.0.0-rc.1

## Canonical source và version

- Canonical: `blender/master/avatar_master.blend`.
- Manifest: `blender/master/avatar_master.manifest.json`.
- Status: release candidate cho temporary final release, chưa phải public semantic/facial release.
- Blender: **5.2.4 LTS**; MPFB: **2.0.18**.
- Source được promote từ neutral candidate commit `5996ee4`, sau khi loại `TECH_HAND_CONTROL_TEST` khỏi canonical copy và reset pose về neutral. Candidate, legacy master và technical working sources vẫn được giữ nguyên.

## Rig contract

- `Human.rig`: 137 deform bones, hierarchy signature ghi trong manifest và khớp TASK-0002.
- Five finger chains mỗi tay, ba bones mỗi finger; `wrist.L/R`, head/neck/jaw và facial deform bones giữ nguyên tên/parent.
- Không rename/reparent bone, không đổi rest pose, không thay Rigify và không thêm IK tùy ý.
- Armature object giữ rotation Euler `(-0.0550454631, 0.0029658440, -0.2448638231)`. TASK-0003/0004/0005 chứng minh pipeline GLB tương thích; không `Apply Transform` mù. Correction, nếu cần, phải làm bằng task/ADR riêng trên copy và so world-space deformation/export.
- Neutral pose: mọi `pose_bone.matrix_basis` identity; 30 FPS; frame 1; canonical không chứa Action/NLA sign.

## Mesh và appearance

- `Human`, `EDU_NeutralTop`, `EDU_NeutralShorts` đều bind `Human.rig` qua Armature modifier.
- Trang phục teal/slate là low-detail educational prototype. Không tạo male/female variants ở version này.
- Future appearance variants nên reuse canonical skeleton/hierarchy; topology/weights khác phải qua rig compatibility gate.

## Facial capability hiện tại

Audit tự động tìm thấy 50 bones thuộc head/neck/facial naming set. `head`, `neck02`, `jaw`, `eye.L` và `eye.R` tạo mesh deformation và reset chính xác trong controlled tests. Các nhóm `oris`, `oculi`, `orbicularis`, `levator`, `risorius` có weights thực tế ở nhiều endpoint bones.

Giới hạn quan trọng:

- 11 Shape Keys hiện có là MPFB macro/body mix; không key nào có facial semantic. Không dùng chúng như expression/viseme.
- Không có production brow/blink/lip/viseme Shape Keys.
- Eyes/eyebrows không phải object riêng; static GLB close-up cho thấy không có visible eyeball/pupil asset phù hợp eye-direction production.
- Facial bone presence/weights chỉ chứng minh khả năng deformation cấu trúc, chưa chứng minh NMM đúng, đẹp hoặc phù hợp VSL.

Roadmap facial: ưu tiên eye asset/direction, blink, eyebrow raise, jaw/mouth-open corrective, lip/viseme set; mỗi target cần front/side preview, deformation QA, Morph export validation và content/expert review khi được dùng cho NMM.

## Export profiles đã xác minh

### `MASTER_STATIC`

Purpose: preview/reference của canonical neutral master.

- Export-only copy; bake current MPFB shape-key mix; apply non-Armature modifiers (`Hide helpers`); giữ Armature/skin.
- `export_format="GLB"`, selection only, `export_animations=False`, `export_skins=True`, `export_armature_object_remove=True`, `export_apply=True`, `export_all_influences=False`, `export_morph=False`, cameras/lights off, Y-up.
- Output hiện tại: `assets/exports/master/avatar-master-v1-rc1.glb`.

### `ANIMATION_WITH_MORPHS`

Purpose: future production sign animation có bone animation và facial Morph Targets.

- Proof-of-concept dùng `export_animation_mode="ACTIONS"`, `export_merge_animation="ACTION"`, frame range on, force sampling off, skins on, top four influences, `export_morph=True`, morph normals on, morph tangents off.
- POC đã có một static Morph Target, một `weights` animation channel và 15 bone rotation channels cùng `TECH_HAND_CONTROL_TEST`; Khronos validator không có error.
- Diagnostic target không nằm trong master và không phải facial expression. Profile chỉ chứng minh transport/runtime structure; facial authoring và Three.js facial controller vẫn chưa được triển khai.

Exporter options thực tế của Blender 5.2.4 được lưu trong các export report TASK-0005. Dùng `blender/scripts/export_master_profiles.py` và `tools/validate-master-glb.mjs`; không copy option từ Blender version khác.

## TASK-0006 facial working candidate

- Experimental owner-review candidate: `blender/working/huy-anh/task-0006-facial-foundation/avatar_master_facial_candidate.blend`, version `1.0.0-rc.2`.
- Candidate thêm six visible eye assets, six core `NMM_` Morph Targets và four technical clips; canonical `v1.0.0-rc.1` và official manifest không thay đổi.
- Technical GLB: `assets/exports/technical/technical-facial-test.glb`; isolated viewer: `/technical-facial-viewer`.
- Export profile bake MPFB macro mix và `Hide helpers` trên export-only data, rồi giữ six `NMM_` targets/weight animation bằng NLA track merge.
- Đây không phải production facial release. Owner visual approval và linguistic/content approval vẫn là `NOT YET TESTED`; xem `docs/contracts/facial-animation-contract.md`.

## Ownership và change approval

- Le Huy Anh sở hữu canonical master/rig/export profile.
- Le Quang Mien tạo working copy từ exact master commit/hash; không sửa master trực tiếp.
- Nhat review skeleton/clip/Morph runtime contract; Thao review evidence/content gate.
- Thay bone hierarchy, rest pose, weights trọng yếu, facial target naming hoặc export contract cần coordinated approval và evidence before/after. Binary `.blend` không text-merge.
