# Cài đặt Windows

Các lệnh dưới đây dành cho **Windows CMD**. Không cần Docker, backend, database hoặc global npm package.

## REQUIRED cho mọi thành viên

- Windows 10/11 64-bit.
- Git 2.45 trở lên.
- Node.js 24 LTS; khuyến nghị bản pin trong `.nvmrc` là 24.22.2. Node 26 LTS cũng được engine chấp nhận nhưng CI dùng 24.22.2.
- npm 11 đi kèm Node; lockfile hiện được tạo bằng npm 11.12.1.

Kiểm tra:

```cmd
git --version
node --version
npm --version
```

Nếu PowerShell chặn `npm.ps1`, mở CMD như tài liệu này hoặc gọi `npm.cmd`; không cần hạ execution policy toàn máy.

## OPTIONAL theo vai trò

- Blender 5.2.4 LTS + MPFB 2.0.18: bắt buộc trên máy 3D, không bắt buộc cho Nhat chạy web.
- Git LFS 3.x: chỉ bật tracking sau khi cả bốn máy xác nhận có `git lfs version`.
- System Python: không cần cho web và không thay thế Blender embedded Python.

## Clone hoặc mở repository

Nếu đã có remote do nhóm tạo:

```cmd
git clone https://github.com/lehuyanh423015/HCI-Sign-Language.git
cd HCI-Sign-Language
git switch main
npm ci
```

Nếu nhận thư mục trực tiếp, mở CMD tại folder có `package.json`. TASK-0001 không tạo/push remote.

## Cài và chạy

```cmd
npm ci
npm run sync:data
npm run doctor
npm run dev
```

`npm ci` phải dùng khi đã có `package-lock.json`; chỉ dùng `npm install <package>@<exact-version>` trong PR chủ đích thay dependency.

Quality gate:

```cmd
npm run typecheck
npm run lint
npm run validate:data
npm run test
npm run build
npm run validate:assets
npm run validate:master-v1
npm run check
```

Git LFS 3.x có thể cài sẵn nhưng Master v1 không dùng LFS pointer. Các binary release hiện dưới 100 MB/file và được clone bằng Git thường. Không chạy `git lfs migrate` hoặc bật pattern LFS nếu chưa có PR/policy chung.

## Chỉ định Blender

Trong CMD hiện tại:

```cmd
set "BLENDER_EXECUTABLE=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
npm run doctor
```

Hoặc:

```cmd
npm run doctor -- --blender "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
```

Không commit đường dẫn cá nhân. Doctor đọc `BLENDER_EXECUTABLE`, CLI hoặc `.env.local` bị Git-ignore.

## Phân biệt runtime

- **Node.js/npm:** build React, validation JSON/GLB, tests.
- **System Python:** công cụ Python độc lập nếu task sau thực sự cần; TASK-0001 không cần pip.
- **Blender embedded Python (`bpy`):** chỉ chạy bên trong Blender. Không `pip install bpy` hay global pip để sửa Blender/MPFB.

## Lỗi thường gặp

- `npm.ps1 cannot be loaded`: dùng CMD hoặc `npm.cmd`.
- `npm ci` báo engine: cài Node 24 LTS đúng major/patch khuyến nghị; đóng/mở terminal rồi kiểm tra PATH.
- `sync:data:check` fail: chạy `npm run sync:data`, review cả canonical và generated diff.
- `validate:assets` in `NOT YET TESTED`: bình thường khi chưa có GLB; không gọi là PASS 3D.
- Blender version fail: không upgrade/downgrade âm thầm; báo Huy Anh và dùng đúng 5.2.4 LTS.
- Port Vite bận: chạy `npm run dev -- --port 5174`.
