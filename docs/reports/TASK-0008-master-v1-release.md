# TASK-0008 — Master Avatar v1 Release, GitHub Integration & Team Handoff

- Ngày/Timezone: 2026-11-18, Asia/Saigon
- Branch/base commit: `release/master-avatar-v1` / `db9e13383816ad8f9b7882ad0a05b26d809968d7`
- Scope: promote rc.3 đã owner duyệt, đóng gói/validate Master Avatar v1, ổn định Three.js reference, tích hợp Git/GitHub và handoff bốn thành viên
- Overall status: **PASS local release gates; remote publication và remote fresh clone PENDING trước release commit**

## 1. Executive summary

Owner-approved `Master Avatar v1.0.0-rc.3` đã được promote thành `Master Avatar v1.0.0` tại canonical path. Promotion chỉ đổi release metadata và trạng thái mở file về neutral; fingerprint geometry, bindings, object transforms, rest hierarchy và technical Action curves trước/sau khớp. Candidate rc.3 giữ nguyên SHA-256.

Canonical Blender validation, static/technical GLB, Khronos validators, full `npm run check`, explicit build, stable Three.js asset sync và hai browser viewers đều PASS. Release vẫn là `Temporary Technical Release`; không có sign/lesson hoặc facial control nào được đánh dấu đã xác minh ngôn ngữ.

## 2. Owner approval reference

TASK-0008 ghi nhận owner đã duyệt appearance và technical suitability của refined rc.3. Trạng thái tách biệt:

- Technical validation: `PASS`.
- Owner visual approval: `APPROVED`.
- Vietnamese Sign Language content approval: `NOT YET TESTED`.

## 3. Initial repository status

- Initial branch: `feat/task-0007a-facial-refinement`, HEAD `db9e13383816ad8f9b7882ad0a05b26d809968d7`.
- `main` và `origin/main`: `dc2226179cc346990dac67448ad6d97ed28b4f9a` trước task.
- TASK-0002→0007A là continuous first-parent ancestry; `origin/main` là ancestor của rc.3.
- Remote: `https://github.com/lehuyanh423015/HCI-Sign-Language.git`, đúng repository owner chỉ định.
- Không có existing tag.
- User-owned dirty files trong original worktree: `README.md`, `blender/master/avatar_master_neutral_candidate.blend`, hai TASK-0004 browser evidence files.
- Đã tạo clean worktree ở ignored `node_modules/.task0008` và branch `release/master-avatar-v1`; không stash/reset/clean hoặc stage thay đổi user-owned.

## 4. Environment and dependencies

| Component | Actual result | Status |
|---|---|---|
| OS | Windows, Asia/Saigon | PASS |
| Blender | 5.2.4 LTS, build `cd5dc428cce1` | PASS |
| MPFB | 2.0.18, runtime initialized | PASS |
| Node.js | v24.14.1 | PASS |
| npm | 11.12.1 | PASS |
| Git LFS | 3.5.1 installed; no tracked LFS files | PASS audit |
| GitHub CLI | not installed | SKIPPED — release API/browser alternative to be evaluated after push |
| `npm ci` | completed from lockfile | PASS |
| `npm audit --omit=dev` | 0 production vulnerabilities | PASS |
| full dependency audit notice | `npm ci` reported 12 high issues in development dependency graph | FAIL advisory; no automatic fix/upgrade in release task |

## 5. Approved candidate information and hash verification

| Item | Value | Status |
|---|---|---|
| Path | `blender/working/huy-anh/task-0007a-facial-refinement/avatar_master_facial_refined_candidate.blend` | PASS |
| Expected SHA-256 | `0D9D2ECE642540B792A79F36003FEE1FBB47C6966FFB8A953B7B7F5F043CCAB7` | PASS |
| Before/after promotion SHA-256 | exact match | PASS |
| Version metadata | `1.0.0-rc.3` | PASS |
| Original candidate modified | no | PASS |

## 6. Master promotion method

`blender/scripts/promote_master_v1.py` mở đúng candidate bằng Blender 5.2.4, kiểm tra hash/version/137 bones/six NMM targets/four technical Actions, ghi canonical copy và không save ngược candidate.

Release-only changes:

- set `master_avatar_version=1.0.0` và approval/status metadata;
- frame 1, range 1–1, 30 FPS;
- reset pose basis và six NMM current values về neutral;
- gỡ Action/NLA assignments khỏi runtime scene nhưng giữ bốn Action data-block;
- gắn nhãn technical fixture/linguistic `NOT YET TESTED` cho Actions.

## 7. Previous master preservation and recovery

Previous canonical SHA-256: `A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232`.

Nó còn trong Git history ở commit `db9e13383816ad8f9b7882ad0a05b26d809968d7` và có thể recover mà không thay canonical:

```cmd
git show db9e13383816ad8f9b7882ad0a05b26d809968d7:blender/master/avatar_master.blend > avatar_master-v1-rc1-recovery.blend
```

## 8. Final canonical master

- Path: `blender/master/avatar_master.blend`.
- Version: `1.0.0`.
- SHA-256: `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC`.
- Size: 2,393,258 bytes.
- Canonical manifest: `blender/master/master-avatar.manifest.json`.
- Compatibility manifest: `blender/master/avatar_master.manifest.json`.
- `.blend1`/`.blend2` backup files: 0.

## 9. Release manifest details

Manifests ghi version/status, Blender/MPFB, source/master hashes, 137-bone fingerprint, geometry/binding/transform fingerprints, mesh/skin, NMM targets, facial bones, Actions, export paths/hashes, approval states, limitations, release date và immutable tag reference. Final commit không thể tự ghi chính nó mà không làm đổi commit; immutable annotated tag là release reference.

## 10. Blender rig verification

`docs/reports/artifacts/TASK-0008/master-v1-blender-validation.json`:

- canonical re-open bằng Blender 5.2.4: PASS;
- 137/137 deform bones: PASS;
- hierarchy/rest fingerprint: PASS;
- geometry/binding/object-transform fingerprints: PASS;
- nine skinned meshes: PASS;
- five three-bone finger chains mỗi tay: PASS;
- eye meshes bound 1.0 tới `eye.L/R`: PASS;
- neutral pose/timeline/no assigned animation: PASS.

Hierarchy fingerprint: `0A14E14E5899D4697732D0B0E3F6AC1D6531979B87A7CD23E2652865D9DC2F89`.

## 11. Facial Morph Target verification

Six core targets tồn tại và giữ exact names:

`NMM_BROW_RAISE_L`, `NMM_BROW_RAISE_R`, `NMM_EYE_BLINK_L`, `NMM_EYE_BLINK_R`, `NMM_LIPS_ROUND`, `NMM_LIPS_SPREAD`.

Neutral values = 0; geometry fingerprint khớp rc.3; technical Action curve fingerprint `E8AB1DCCD5C9388F05FFC1FC6D2B41EE9C64C7BB30AE2E81CF985790C0947148`.

## 12. GLB exports and validation

| Asset | SHA-256 | Result |
|---|---|---|
| `assets/releases/master-avatar-v1/master-avatar-v1-static.glb` | `F489677DCBD009A5A6370F09FC7613F851F14FF7A825FC1528A27B217F195CA2` | PASS: 9 meshes, skin, eye nodes, six targets, 0 animation, Khronos 0 errors |
| `assets/exports/technical/task-0007a/technical-facial-refined-test.glb` | `D59AE5422E9B759006FE9D666B6CA56AD1183D157DF666B33813FAE923A492AB` | PASS: four clips, combined hand/face channels, Khronos 0 errors |

Technical demo size 2,455,392 bytes. File này là single source of truth; không tạo duplicate trong release directory.

Four clips, positive durations, Morph weights, hand/head/jaw/eye channels và Khronos 0 errors: PASS.

## 13. Three.js integration results

- Stable generated URL: `/models/technical/master-avatar-v1-technical-demo.glb`.
- Source mapping được quản lý bởi `tools/sync-technical-assets.mjs`; generated public GLB vẫn ignored.
- `/technical-facial-viewer`: actual GLB load, clip/morph inventory, pause, slider, gaze, camera presets, replay/progress, loop/speed và reset — PASS.
- `/technical-viewer`: GLB/canvas, progress, pause/resume/replay, loop, speed và camera regression — PASS on independent rerun.
- Banner unverified giữ nguyên; technical fixture không được thêm vào S001–S006.

Evidence: `master-v1-browser-runtime.json`, screenshots và `technical-viewer-regression.json` trong TASK-0008 artifacts.

## 14. Git LFS decision

Git LFS 3.5.1 installed nhưng repository không track pattern/file nào và endpoint upload auth chưa được chứng minh. Largest tracked file khoảng 6.1 MB, release `.blend`/GLB khoảng 2.2–2.5 MB, nhỏ hơn nhiều giới hạn GitHub 100 MB/file.

Quyết định: dùng normal Git cho v1, không đổi `.gitattributes`, không migrate/rewrite history. Bốn thành viên chỉ cân nhắc LFS bằng PR riêng khi asset growth/quota yêu cầu.

## 15. Dependency and licensing audit

- Production dependency audit: 0 vulnerabilities.
- Development graph: npm notice 12 high; cần task dependency-maintenance riêng, không chạy `npm audit fix --force`.
- Official MPFB license: code GPLv3; bundled assets CC0; project-generated/saved output do user kiểm soát.
- Official MakeHuman license cảnh báo third-party downloaded assets có license riêng.
- TASK-0008 không thêm external asset pack hoặc redistribute MPFB software; uncertain assets bị loại.
- Repository chưa có top-level license cho code nhóm: owner cần quyết định license trong PR riêng.

## 16. Git integration history

`origin/main` → TASK-0002 → TASK-0003 → TASK-0004 → TASK-0005 → TASK-0006 → TASK-0007 → TASK-0007A là linear ancestry. Release có thể fast-forward; không cần merge commit, rebase hoặc history rewrite.

## 17. Actual pushed branch and commit

- Release branch: `release/master-avatar-v1`.
- Local release commit: `PENDING` trước commit bắt buộc của protocol.
- Remote release branch: `NOT YET TESTED`.
- Remote main: `NOT YET TESTED`.
- PR requirement: `NOT YET TESTED`, phụ thuộc branch protection khi push.

## 18. GitHub tag and release

- Planned annotated tag: `master-avatar-v1.0.0`.
- Planned title: `Master Avatar v1.0.0 — Technical Foundation`.
- Planned prerelease/technical preview: yes.
- GitHub Release URL: `NOT YET TESTED`.
- GitHub Pages/public website deployment: out of scope, not performed.

## 19. Fresh-clone results

- Local clean worktree from TASK-0007A: `npm ci`, checks/build/runtime PASS.
- Actual remote fresh clone: `NOT YET TESTED` until release branch is pushed.
- Mien/Nhat/Thao machine onboarding: `PENDING`; không được suy ra từ agent test.

## 20. Test matrix

| Check | Evidence | Status |
|---|---|---|
| Approved candidate hash unchanged | promotion report | PASS |
| Canonical opens in Blender 5.2.4 | Blender validation | PASS |
| 137 bones/hierarchy | Blender validation | PASS |
| Geometry/bindings/transforms vs rc.3 | deterministic fingerprints | PASS |
| Finger/eye controls | Blender validation | PASS |
| Six NMM Morph Targets | Blender + GLB validators | PASS |
| Static GLB | release validator | PASS |
| Technical demo GLB/four clips | facial + release validators | PASS |
| Khronos validation | 0 errors on both release GLBs | PASS |
| Stable sync/hash | sync check | PASS |
| `npm run check` | full output | PASS |
| explicit `npm run build` | Vite build | PASS, chunk-size warning |
| facial Three.js runtime | 10 checks | PASS |
| old technical viewer regression | independent rerun | PASS |
| S001–S006 lesson GLBs | none present | NOT YET TESTED |
| Linguistic approval | no qualified evidence | NOT YET TESTED |
| Remote push/main/tag/release | pending commit | NOT YET TESTED |
| Remote fresh clone | pending publication | NOT YET TESTED |
| Other members onboarding | not executed on their machines | NOT YET TESTED |

## 21. Created and modified files

- Canonical/release binaries and manifests under `blender/master/` and `assets/releases/master-avatar-v1/`.
- Promotion/validation/export scripts under `blender/scripts/`.
- Release validator and sync/viewer updates under `tools/`, `apps/web/`, `package.json`.
- `README.md`, contracts, setup, ownership/handoff, `CHANGELOG.md`, `docs/releases/MASTER_AVATAR_V1.md`, `docs/team/MASTER_V1_HANDOFF.md`.
- TASK-0008 evidence and this report.

Generated `apps/web/public/models/technical/*.glb`, `node_modules/` và `dist/` không được stage.

## 22. Commands actually executed

```text
git fetch --prune origin
git branch -a -vv
git log --graph --decorate --oneline --all -30
git lfs version
git lfs env
git worktree add -b release/master-avatar-v1 node_modules/.task0008 db9e133...
python -m py_compile blender/scripts/master_v1_utils.py ...
blender.exe <rc.3> --background --python promote_master_v1.py -- ...
blender.exe blender/master/avatar_master.blend --background --python validate_master_v1.py -- ...
blender.exe blender/master/avatar_master.blend --background --python export_master_v1_static.py -- ...
npm ci
npm run sync:technical-assets
npm run sync:technical-assets:check
npm run verify:master
npm run validate:master-v1
node tools/validate-facial-asset.mjs --asset <technical-demo> --report <TASK-0008-report>
npm run check
npm audit --omit=dev
npm ls --depth=0
npm run build
npm run dev --workspace @hci-sign/web -- --host 127.0.0.1 --port 4173
node tools/test-facial-viewer.mjs --url http://127.0.0.1:4173/technical-facial-viewer ...
node tools/test-technical-viewer.mjs --url http://127.0.0.1:4173/technical-viewer ...
Get-FileHash ... -Algorithm SHA256
```

Honest failures/resolutions:

1. Một PowerShell audit command có closing-parenthesis syntax error; không đổi file, chạy lại bằng command đơn giản.
2. Promotion run đầu dừng trước save vì Blender `Bone` không có property `roll`; fingerprint đổi sang `matrix_local`, rerun PASS.
3. Validator finger-chain run đầu dùng semantic `thumb/index/...` không khớp rig `finger1-1...finger5-3`; sửa theo inventory, rerun PASS.
4. Vite start đầu truyền sai npm workspace separator; process dừng, chạy lại đúng cú pháp.
5. Technical viewer runtime lần đầu timing sample trả 0 trong khi pause/resume đã hoạt động; independent rerun toàn bộ checks PASS. First FAIL được ghi nhận tại đây; evidence file cuối phản ánh rerun PASS.

## 23. Team handoff deliverables

- `docs/team/MASTER_V1_HANDOFF.md`: fresh clone, role/tool matrix, safe working copy, export, metadata, issue/PR và acceptance pending.
- `README.md`, `HANDOFF.md`, `OWNERSHIP.md`, Windows/Blender setup và two contracts được cập nhật.
- Nhat không cần Blender cho ordinary frontend work; Mien/Huy Anh bắt buộc Blender 5.2.4 + MPFB 2.0.18.

## 24. Unresolved issues

- Remote publication và actual remote fresh-clone chờ release commit.
- GitHub CLI không cài; GitHub Release cần authenticated REST/browser workflow hoặc owner action nếu auth không khả dụng.
- Dev dependency audit notice: 12 high; production audit 0.
- No repository-level license cho team code.
- Eyebrow geometry simplified; eyelid topology chưa production-quality; materials có thể refine.
- S001–S006 và linguistic validation chưa có.

## 25. Owner acceptance checklist

- [x] rc.3 appearance đã được owner duyệt theo TASK-0008.
- [x] canonical v1 được tạo từ exact rc.3 hash.
- [x] previous master recoverable.
- [x] structural/GLB/Three.js gates PASS.
- [ ] Xác nhận remote main/tag/GitHub Release sau publication.
- [ ] Chọn repository-level license cho code/docs của nhóm.
- [ ] Mien, Nhat và Thao hoàn tất onboarding trên máy riêng.
- [ ] Qualified linguistic reviewer duyệt từng sign/NMM use trước educational publication.

## 26. Recommended TASK-0009 scope

Đề xuất TASK-0009 tập trung vào animation-production workflow trên Master v1: tạo working-copy templates cho S001–S006, source/reference/evidence gate, per-sign Blender/GLB/Three.js validation và không thay đổi master hierarchy. Không tự động bắt đầu TASK-0009.
