# Handoff nhanh cho nhóm

## Mỗi người bắt đầu

```cmd
git clone https://github.com/lehuyanh423015/HCI-Sign-Language.git
cd HCI-Sign-Language
git switch main
git pull --ff-only
git switch -c <branch-name>
npm ci
npm run doctor
```

3D member dùng Blender 5.2.4 LTS + MPFB 2.0.18, đọc `SETUP_BLENDER.md`, tạo working copy đúng folder và báo nhóm đang giữ file nào. Web/QA member chạy `npm run check` trước khi push.

Release chuẩn cho cả nhóm là tag `master-avatar-v1.0.0` trên repository `https://github.com/lehuyanh423015/HCI-Sign-Language.git`. Đọc `docs/team/MASTER_V1_HANDOFF.md` trước khi tạo branch hoặc Blender working copy.

## Xem technical prototype

```cmd
npm ci
npm run sync:data
npm run sync:technical-assets
npm run validate:technical-asset
npm run dev
```

Mở `http://localhost:5173/technical-viewer`. Banner phải ghi `TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE`. Thử pause/resume, replay, loop, 0.5×/1×, rotate/zoom, reset camera và hand preset.

Viewer mặc định dùng `technical-hand-test-neutral.glb`. Đây là technical fixture trung tính, chưa phải production sign. Official shared source là `blender/master/avatar_master.blend`; viewer fixture vẫn tách biệt vì chứa `TECH_HAND_CONTROL_TEST`.

## Giao gì và phụ thuộc ai

- **Huy Anh:** master revision + skeleton/preflight record + S001–S003 `.blend`/preview/GLB. Mien phụ thuộc master; Nhat phụ thuộc GLB contract; Thao phụ thuộc preview/evidence.
- **Mien:** S004–S006 source/preview/GLB dựa trên đúng master revision. Huy Anh review technical trước khi Nhat tích hợp.
- **Nhat:** viewer controls, route/UI và browser playback evidence. Cần Huy Anh cung cấp clip/GLB đúng contract và Thao cung cấp metadata approval.
- **Thao:** canonical metadata, reference/evidence, adaptive rules/tests và QA result. Nhat chỉ publish educational mode sau approval.

## Asset nào được sửa

- Huy Anh/Mien chỉ sửa file trong working folder của mình. Không save trực tiếp `blender/avatar_master.blend` hoặc file animator khác.
- `assets/exports/technical/technical-hand-test.glb` là baseline TASK-0003; `technical-hand-test-neutral.glb` là neutral fixture TASK-0004. Không đổi hai file này thành S001–S006.
- Nhat consume canonical GLB qua `npm run sync:technical-assets`; không commit public generated copy.
- Thao sửa canonical `data/`, source/evidence; không tự đánh `approved` thiếu reviewer.
- Shared contracts, master, production export cần review của owner/consumer liên quan.

## Canonical neutral master

- Official release: `blender/master/avatar_master.blend`, `Master Avatar v1.0.0`; exact hash trong `blender/master/master-avatar.manifest.json`.
- Promotion source rc.3 được giữ tại `blender/working/huy-anh/task-0007a-facial-refinement/`; không dùng tiếp làm canonical.
- Static release GLB: `assets/releases/master-avatar-v1/master-avatar-v1-static.glb`.
- Technical demo source: `assets/exports/technical/task-0007a/technical-facial-refined-test.glb`; không đưa bốn clip kỹ thuật vào S001–S006.
- Master giữ 137-bone hierarchy, eye geometry, sáu core `NMM_` targets và bốn technical Action data-block; scene mở neutral và không assign Action/NLA.
- Mien tạo working copy từ exact tag/commit/hash; không copy từ candidate hoặc technical demo.
- Khi export MPFB body phải bake current shape-key mix trên export copy, apply non-Armature modifiers để `Hide helpers` có hiệu lực, giới hạn 4 skin influences và không save các thay đổi export-only vào source.
- Facial controls là technical foundation đã owner duyệt về appearance; linguistic validity và production sign usage vẫn `NOT YET TESTED`. Diagnostic Morph POC không phải deliverable animation.

## Integration

1. PR ngắn, đúng owner, không kèm cache/render tạm.
2. `npm run check`; 3D PR thêm `npm run validate:assets` + manual checklist.
3. Shared contract cần owner + consumer review.
4. Merge vào `main`; thành viên khác rebase/merge main sớm, không sửa binary conflict bằng text merge.

## Báo blocker

Trong group/issue ghi: `BLOCKER`, owner, sign ID/file, master commit/hash, expected/actual, log/screenshot, ảnh hưởng milestone, quyết định cần trước thời điểm nào. Không tự đổi contract hay scope. Ngày 5 dùng evidence thực tế để quyết định 6 hay 3–4 signs.

Mỗi Agent task phải kèm report theo `docs/workflows/AGENT_TASK_PROTOCOL.md`. Pull request nêu exact commands và phân biệt automated PASS với manual visual acceptance.

## Facial technical fixture TASK-0006

```cmd
npm run sync:technical-assets
npm run validate:facial-asset
npm run dev
```

Mở `http://localhost:5173/technical-facial-viewer`. Trang phải hiển thị banner `TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE`, six `NMM_` sliders, gaze controls và four technical clips. Viewer dùng stable generated asset `master-avatar-v1-technical-demo.glb`; nguồn canonical ghi trong release manifest. Clip/biểu cảm là technical fixture, linguistic status `NOT YET TESTED` và không được đưa vào lesson catalog.

## Sign production pipeline TASK-0009

Đọc `docs/team/ONBOARDING.md`, role guide, `docs/team/GIT_WORKFLOW.md` và `docs/contracts/sign-animation-production-contract.md`. Template dùng chung ở `blender/templates/sign-animation-template.blend`; mỗi sign phải được sinh thành isolated working copy, không copy/save đè master. Metadata canonical của production package ở `blender/working/signs/S001`–`S006`.

```cmd
npm run validate:sign-packages
npm run sync:technical-assets
npm run dev
```

Mở `/technical-sign-preview`. Pilot hiện là `TECHNICAL_FIXTURE_NOT_A_SIGN`, không thuộc lesson catalog; linguistic status `NOT YET TESTED`. Actual sign pilot `BLOCKED` cho tới khi Thao/content owner cung cấp reference hợp lệ và qualified review path.

## Git LFS

Git LFS 3.5.1 có trên máy bootstrap và remote endpoint được nhận diện, nhưng repository chưa bật tracking patterns và remote auth/upload chưa được thử. Prototype `.blend`/`.glb` hiện dưới giới hạn GitHub; trước khi thêm nhiều video/GLB lớn, cả bốn máy phải cài `git lfs`, xác nhận remote quota/auth rồi bật patterns trong PR riêng. Không migrate history tùy tiện.
