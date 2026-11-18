# TASK-0009 — Team Onboarding & Sign Animation Production Pipeline

- Ngày/Timezone: 2026-11-18 / Asia/Saigon
- Branch: `feat/task-0009-team-onboarding-animation-pipeline`
- Base: `origin/main` tại `e6fe22dc4bb19fcdae12a055fa1038417c4db126`
- Scope: onboarding bốn vai trò; template/working-copy/export/validation; metadata S001–S006; technical staging preview; pilot hạ tầng.
- Overall status: **PASS về hạ tầng kỹ thuật; actual sign pilot BLOCKED; linguistic NOT YET TESTED**.

## 1. Executive summary

TASK-0009 đã tạo pipeline tái lập từ Master Avatar v1.0.0 đến isolated `.blend`, GLB một clip, validation JSON, asset sync và Three.js staging preview. Sáu sign chỉ là placeholder `REFERENCE_PENDING`; không có tên/nghĩa/animation giả. Do repository không có reference VSL hợp lệ, pilot dùng `TECHNICAL_FIXTURE_NOT_A_SIGN` và không vào lesson catalog.

## 2. Initial Git state

- Worktree sạch riêng: `node_modules/.task0009`, branch đúng yêu cầu, tracking `origin/main`.
- Local/remote base ban đầu cùng `e6fe22d`; tag `master-avatar-v1.0.0` tồn tại tại `3c38233`.
- Remote: `https://github.com/lehuyanh423015/HCI-Sign-Language.git`.
- Original worktree và bốn user-owned changes của TASK trước không bị sửa/reset/clean/stash.
- Không merge `main`, không force-push, không rewrite history hoặc xóa branch.

## 3. Master Avatar v1 verification

- Canonical: `blender/master/avatar_master.blend`.
- SHA-256 trước/sau: `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC` — khớp manifest.
- Blender validator: 137 deform bones, hierarchy `0A14E14E...C2F89`, 9 bound meshes, bindings/transforms, six core NMM targets, eye bindings, finger chains, technical Actions và neutral state: `PASS`.
- Master không bị save khi sinh template, pilot hoặc S001 isolation test.

Evidence: `docs/reports/artifacts/TASK-0009/master-v1-blender-validation.json`.

## 4. Environment audit

| Tool | Kết quả trên máy hiện tại |
|---|---|
| Blender | `5.2.4 LTS` — PASS |
| MPFB | `2.0.18` baseline; add-on log initialized — PASS |
| Node.js | `v24.14.1` — PASS engine range |
| npm | `11.12.1` — PASS |
| Git | `2.45.1` |
| Git LFS | `3.5.1`; chưa cần bật cho v1 |
| Browser automation | Chrome headless + WebGL — PASS |

Finding TASK-0008 vẫn còn hiệu lực: production dependencies 0 vulnerability; development audit có 12 high-severity notices; không chạy `npm audit fix --force`. Repository chưa có top-level LICENSE được owner duyệt; task không tự chọn license.

## 5. Team environment matrix

`docs/team/TEAM_ENVIRONMENT_MATRIX.md` phân vai tối thiểu: Git cho cả bốn; Blender/MPFB bắt buộc cho Huy Anh/Mien; Node/npm bắt buộc cho Nhat và integration, optional/as-needed cho Mien/Thao; browser cho cả bốn. Chỉ máy hiện tại được kiểm tra, ba máy còn lại `PENDING MEMBER CONFIRMATION`.

## 6. Onboarding documents

Đã tạo:

- `docs/team/ONBOARDING.md`
- `docs/team/TEAM_ENVIRONMENT_MATRIX.md`
- `docs/team/TEAM_ONBOARDING_CHECKLIST.md`
- `docs/setup/SETUP_HUY_ANH.md`
- `docs/setup/SETUP_MIEN.md`
- `docs/setup/SETUP_NHAT.md`
- `docs/setup/SETUP_THAO.md`
- `docs/team/GIT_WORKFLOW.md`

Tài liệu dùng Windows CMD/repository-relative paths, giải thích install/run/test/troubleshooting và cách báo blocker. Không tuyên bố máy của thành viên khác đã setup xong.

## 7. Blender template implementation

- Template: `blender/templates/sign-animation-template.blend`.
- SHA-256: `780D924DA9FEA33698927ADD90A469C9BEFEEC9D312AA4C207E879CC7031EC94`.
- Size: `2,390,398` bytes.
- 30 FPS, frame `1–120`, neutral, no assigned Action/NLA, six targets/137 bones/bindings giữ nguyên.
- Có collections `SIGN_ANIMATION_GUIDES` và `SIGN_EXPORT_NOTES`; reusable Action datablocks vẫn được giữ.
- Generation/validation: `PASS`; expected sign Action trên template và linguistic review là `NOT YET TESTED` đúng chủ đích.

Evidence: `template-generation.json`, `template-validation.json`.

## 8. Working-copy generation tests

`create_sign_working_copy.py` kiểm tra exact Blender LTS string, canonical SHA/hierarchy/NMM, từ chối overwrite source/output, đặt metadata/version/neutral/timeline và save path riêng.

- `TEMPLATE`: PASS.
- `TECHNICAL_FIXTURE_NOT_A_SIGN`: PASS, SHA-256 `F80800E3BE21CF5835E0B6C15AA56BD3A0157AA4B05D25A2C94D9CE2CB8F8633`.
- `S001` isolation test: PASS; binary test tạm đã xóa sau khi ghi JSON evidence; canonical hash vẫn khớp.

Lần chạy đầu dùng expected string `5.2.4` và đúng đắn bị Blender `5.2.4 LTS` từ chối. Script được sửa thành exact `5.2.4 LTS`, sau đó PASS; lỗi trung gian không được ghi thành PASS.

## 9. Sign metadata structure

`blender/working/signs/S001`–`S006` có `sign.json` và placeholder directories `references/`, `evidence/`, `exports/`, `previews/`. Không có `animation.blend`, GLB, preview, tên, gloss hoặc reference giả. Assignment cũ trong `data/signs.json` không bị thay thế; production metadata mới là lớp handoff chi tiết, lesson metadata vẫn giữ contract hiện có.

## 10. JSON Schema validation

Schema: `docs/contracts/sign-metadata.schema.json`, Draft 2020-12, strict objects và approval gate. Sáu record:

- schema/ID/no-accidental-approval: `PASS`;
- reference/source/GLB/preview: `NOT YET TESTED`;
- status: `REFERENCE_PENDING`.

Evidence: `sign-package-validation.json`.

## 11. Animation production contract

`docs/contracts/sign-animation-production-contract.md` định nghĩa bảy bước: reference → working copy → animation → Blender validation → export/package validation → preview → linguistic gate/integration. Exact naming `Snnn_MAIN`, neutral frame 1, 30 FPS, immutable rig và technical/linguistic separation là bắt buộc.

## 12. Blender validation scripts

- `create_sign_working_copy.py`: isolated source/template creation.
- `validate_sign_animation.py`: version/master metadata, 137 bones/hierarchy, bindings, six NMM, timeline/Action/neutral.
- `export_sign_animation.py`: one Action through in-memory NLA, export-only MPFB bake/modifier handling; không save source.

Pilot Blender validation: `PASS`; linguistic: `NOT YET TESTED`. Export lần đầu phát hiện `sorted(Object)` không có key (`TypeError`); sửa deterministic `key=obj.name`, chạy lại và report `PASS`.

## 13. GLB validation results

Pilot: `assets/exports/technical/task-0009/technical-sign-pipeline-pilot.glb`.

- SHA-256: `AB07833D25639FECB47FA055AA1034BF64C148C6DC6096487A2E7E96804B5147`.
- Size: `2,306,344` bytes.
- glTF 2.0, 9 meshes, 1 skin, six core NMM targets: PASS.
- Exact clip `TECH_HAND_FACE_TEST`, duration `1.5s`: PASS.
- Khronos: `0` error, `0` warning: PASS.
- Classification: `TECHNICAL_FIXTURE_NOT_A_SIGN`; linguistic `NOT YET TESTED`.

## 14. Three.js preview results

Route `/technical-sign-preview` tái sử dụng `TechnicalViewer` với configurable GLB/clip/classification. Trang hiển thị ID, master version, exact clip, technical/linguistic status và warning, nằm ngoài lesson catalog. Sync canonical → generated web copy kiểm tra hash PASS.

Browser automation: load/canvas, animation progress, pause/resume, replay, loop, 0.5×, reset/hand camera: tất cả PASS, không runtime exception. `/technical-viewer` regression cùng tám checks: PASS.

## 15. First pilot result

- Infrastructure pilot: **PASS**, dùng technical Action có sẵn, không gán semantic VSL.
- Actual sign pilot: **BLOCKED** vì `data/signs.json` và workspace không có owner-provided/verified reference cho S001–S006.
- Không tạo animation giả và không đổi lesson metadata.

## 16. Linguistic verification status

`NOT YET TESTED` cho template, fixture và S001–S006. Không sign nào được đánh `APPROVED`; automated technical PASS không cấp linguistic PASS.

## 17. Git branch and commit

- Branch: `feat/task-0009-team-onboarding-animation-pipeline`.
- Base: `e6fe22dc4bb19fcdae12a055fa1038417c4db126`.
- Final commit chứa report không thể tự ghi hash của chính nó; exact hash được ghi trong final response của Agent.

## 18. Push status

Normal push của feature branch được task cho phép và sẽ chạy sau final review/commit. Không merge main. Remote URL/exact published commit được ghi trong final response; nếu remote từ chối, local commit vẫn được bảo toàn và blocker được báo chính xác.

## 19. Files changed

- Frontend: route/page/configurable viewer/styles/unit test.
- Pipeline: ba Blender scripts, `tools/validate-sign-package.mjs`, sync/package scripts.
- Binary: template, isolated pilot `.blend`, technical pilot GLB.
- Metadata: schema + six sign workspaces.
- Docs: onboarding/matrix/checklist/four role guides/Git workflow/production contract/README/handoff/report.
- Evidence: 12 JSON/PNG artifacts trong `docs/reports/artifacts/TASK-0009/`.

Generated `apps/web/public/models/technical/technical-sign-pipeline-pilot.glb` nằm trong sync output bị ignore, không được coi là canonical.

## 20. Actual commands executed

```text
git fetch origin --prune
git worktree add ... -b feat/task-0009-team-onboarding-animation-pipeline origin/main
Get-FileHash blender\master\avatar_master.blend -Algorithm SHA256
npm run validate:sign-packages
npm run typecheck
npm run lint
npm test
blender.exe -b blender\master\avatar_master.blend --python blender\scripts\create_sign_working_copy.py -- --sign-id TEMPLATE ...
blender.exe -b blender\master\avatar_master.blend --python blender\scripts\create_sign_working_copy.py -- --sign-id TECHNICAL_FIXTURE_NOT_A_SIGN ...
blender.exe -b blender\templates\sign-animation-template.blend --python blender\scripts\validate_sign_animation.py -- --sign-id TEMPLATE ...
blender.exe -b blender\working\pilots\TECHNICAL_FIXTURE_NOT_A_SIGN.blend --python blender\scripts\validate_sign_animation.py -- --sign-id TECHNICAL_FIXTURE_NOT_A_SIGN --expected-clip TECH_HAND_FACE_TEST ...
blender.exe -b blender\working\pilots\TECHNICAL_FIXTURE_NOT_A_SIGN.blend --python blender\scripts\export_sign_animation.py -- --clip TECH_HAND_FACE_TEST --technical-fixture ...
npm run sync:technical-assets
npm run sync:technical-assets:check
npm run build
npm run test:sign-preview
node tools\test-technical-viewer.mjs --url http://127.0.0.1:4173/technical-viewer ...
blender.exe -b blender\master\avatar_master.blend --python blender\scripts\validate_master_v1.py -- ...
npm run check
git diff --check
```

## 21. Test matrix

| Check | Evidence | Status |
|---|---|---|
| Master SHA + Blender v1 contract | `master-v1-blender-validation.json` | PASS |
| Template generation/structure/neutral | `template-generation.json`, `template-validation.json` | PASS |
| Isolated S001 creation; master unchanged | `S001-isolation-test.json`, hash command | PASS |
| Pilot Blender Action/range/neutral | `pilot-blender-validation.json` | PASS |
| Six metadata records/schema | `sign-package-validation.json` | PASS |
| Six real reference/source packages | same report | NOT YET TESTED |
| Pilot export | `pilot-glb-export.json` | PASS |
| Pilot GLB + Khronos | `sign-package-validation.json` | PASS |
| Asset sync/check | command output | PASS |
| Unit tests | 4 Node + 5 Vitest | PASS |
| Build | Vite output | PASS (chunk-size warning) |
| Full existing gate | `npm run check` | PASS |
| Sign preview browser | `sign-preview-browser.json/png` | PASS |
| Existing viewer regression | `technical-viewer-regression.json/png` | PASS |
| Actual VSL sign pilot | missing verified reference | NOT YET TESTED / BLOCKED |
| Linguistic correctness | no qualified review | NOT YET TESTED |
| Team onboarding on other 3 machines | no member evidence | NOT YET TESTED |

## 22. Known limitations

- Chưa có verified VSL reference hoặc sign production animation.
- Template giữ prototype topology/material limitations của Master v1.
- Vite báo main bundle khoảng 928 kB (>500 kB advisory); không phải failure và không refactor ngoài scope.
- Previous development audit notices (12 high) vẫn mở; không force-fix.
- Chưa có owner-approved top-level LICENSE.
- Git LFS chưa cần cho current binaries; cần đánh giá riêng nếu video/binary tăng mạnh.

## 23. Required owner decisions / manual acceptance

- [ ] Huy Anh mở `sign-animation-template.blend`, xác nhận workspace/timeline/appearance/neutral và master lock.
- [ ] Huy Anh xác nhận export preset/one-clip contract phù hợp production.
- [ ] Mien chạy checklist trên máy riêng và tạo một disposable working copy.
- [ ] Nhat xác nhận `/technical-sign-preview` trên browser/máy riêng.
- [ ] Thao xác nhận schema/reference workflow và cung cấp reference có thể truy vết cho pilot thật.
- [ ] Owner quyết định license bằng task riêng.
- [ ] Qualified reviewer được xác định trước khi bất kỳ sign nào chuyển `LINGUISTIC_REVIEW`/`APPROVED`.

## 24. Recommended TASK-0010

`TASK-0010 — Verified Reference Intake & First Real Sign Pilot`: chọn một Snnn sau khi có reference hợp lệ/quyền sử dụng, khóa gloss/variant, sản xuất `Snnn_MAIN`, tạo front/side evidence và thực hiện technical + qualified linguistic review. Không tự động bắt đầu TASK-0010.
