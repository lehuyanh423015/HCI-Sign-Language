# Cấu trúc repository

```text
.
├─ apps/web/                    React + TypeScript + Vite
│  ├─ public/data/              bản sinh bởi sync:data
│  ├─ public/models/signs/      GLB đã duyệt để browser dùng
│  ├─ src/app/                  shell và routing
│  ├─ src/components/viewer/    boundary Three.js/viewer
│  ├─ src/features/             lessons, quiz, review, adaptive
│  ├─ src/services/             truy cập dữ liệu/storage
│  ├─ src/types/                shared frontend types
│  └─ tests/                    smoke tests
├─ blender/
│  ├─ avatar_master.blend       file có sẵn, candidate chưa kiểm tra
│  ├─ master/                   master được duyệt về sau
│  ├─ working/huy-anh|mien/     file làm việc riêng
│  ├─ scripts/                  read-only preflight/export tools
│  ├─ presets/                  export presets được kiểm soát
│  └─ tests/                    Blender pipeline fixtures/tests
├─ assets/
│  ├─ references/               tài liệu nguồn có provenance
│  ├─ staging/                  trung gian local, không commit mặc định
│  ├─ exports/signs/            GLB chờ review
│  └─ previews/                 video review local
├─ data/                        nguồn metadata/quiz canonical
├─ schemas/                     JSON Schema
├─ tools/                       doctor, sync và validators
├─ docs/                        kiến trúc, hợp đồng, setup, workflow, QA
└─ .github/workflows/           quality gate không cần Blender
```

Không tạo app frontend thứ hai. Không sao chép thủ công JSON canonical. Không tự ý sửa `blender/master/`, hợp đồng hoặc production export.
