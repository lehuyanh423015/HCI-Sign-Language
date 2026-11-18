# Master Avatar v1.0.0 — Technical Foundation

- Release date: 2026-11-18
- Classification: `Temporary Technical Release`
- Git tag: `master-avatar-v1.0.0`
- Repository: `https://github.com/lehuyanh423015/HCI-Sign-Language.git`

## Purpose and approval

Release này thiết lập baseline 3D ổn định cho development của bốn thành viên. Owner đã duyệt appearance và technical suitability của rc.3. Technical validation là `PASS`; linguistic/content approval là `NOT YET TESTED`. Không có animation bài học Ngôn ngữ Ký hiệu Việt Nam nào được release này xác nhận.

## Source and hashes

| Artifact | SHA-256 |
|---|---|
| Approved rc.3 candidate | `0D9D2ECE642540B792A79F36003FEE1FBB47C6966FFB8A953B7B7F5F043CCAB7` |
| Canonical `blender/master/avatar_master.blend` | `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC` |
| Static GLB | `F489677DCBD009A5A6370F09FC7613F851F14FF7A825FC1528A27B217F195CA2` |
| Technical demo GLB | `D59AE5422E9B759006FE9D666B6CA56AD1183D157DF666B33813FAE923A492AB` |

Canonical khác byte rc.3 vì metadata version/approval được cập nhật, scene được đặt frame 1 neutral, NMM values/pose basis được reset và Action/NLA assignments được gỡ. Fingerprints geometry, bindings, object transforms, rest hierarchy và Action curves giữ nguyên.

## Technical specification

- Blender 5.2.4 LTS; MPFB 2.0.18.
- 137 deform bones; hierarchy/rest pose giữ nguyên từ rc.3.
- Nine skinned mesh objects, gồm body/clothing và six eye components.
- Six core Morph Targets: brow L/R, blink L/R, lips round/spread.
- `head`, `neck01/02/03`, `jaw`, `eye.L/R` và five three-bone finger chains mỗi tay.
- Reusable technical clips: `NMM_BLINK_TEST`, `NMM_BROW_TEST`, `NMM_MOUTH_TEST`, `TECH_HAND_FACE_TEST`.

## Release assets

- Static preview: `assets/releases/master-avatar-v1/master-avatar-v1-static.glb`.
- Technical demo single source: `assets/exports/technical/task-0007a/technical-facial-refined-test.glb`.
- Web generated reference: `/models/technical/master-avatar-v1-technical-demo.glb`.
- Sync: `npm run sync:technical-assets`.
- Validation: `npm run validate:master-v1`.

## Compatibility guarantee

Minor visual/material improvements must not silently rename bones/targets, change hierarchy/rest pose, or break `Snnn_MAIN` export and existing technical clips. Breaking changes require coordinated contract review, migration notes and a new major release decision.

## Licensing and redistribution audit

MPFB's official license states bundled assets are CC0 and generated/saved output is controlled by the user; MPFB program code itself is GPLv3 and is not redistributed here. MakeHuman also warns that third-party downloaded assets can have separate licenses. TASK-0008 did not add external asset packs or redistribute MPFB software. Any future downloaded clothing, texture or community asset requires a per-asset license record before commit/release.

Project source currently has no repository-level `LICENSE`; therefore this release does not infer a license for the team's own code. The owner should add an explicit repository license in a dedicated decision/PR.

Official references:

- `https://github.com/makehumancommunity/mpfb2/blob/master/LICENSE.md`
- `https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md`

## Known limitations

- Eyebrow geometry remains a simplified prototype.
- Eyelid topology is not fully production quality.
- Skin/facial materials may be refined later.
- Facial controls have not been linguistically validated.
- No real Vietnamese Sign Language learning animation has been approved.
- `npm ci` currently reports dependency audit findings; automated build/runtime gates remain separate from `npm audit` remediation.

## Upgrade and recovery

Previous rc.1 master remains recoverable from commit `db9e13383816ad8f9b7882ad0a05b26d809968d7`:

```cmd
git show db9e13383816ad8f9b7882ad0a05b26d809968d7:blender/master/avatar_master.blend > avatar_master-v1-rc1-recovery.blend
```

Không ghi đè canonical bằng file recovery. Mọi upgrade phải tạo working copy, chạy fingerprint/Blender/GLB/Three.js gates và cập nhật manifest/report trước commit.
