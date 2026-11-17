# Hợp đồng dữ liệu nội dung

## Nguồn sự thật

`data/signs.json` và `data/quizzes.json` là canonical. `apps/web/public/data/` là output sinh bằng:

```cmd
npm run sync:data
```

Không sửa public copy. CI dùng `npm run sync:data:check` để phát hiện bản thiếu/cũ.

## Sign metadata

Schema: `schemas/sign.schema.json`. ID phải duy nhất và theo `S001`…; đường dẫn luôn `models/signs/<ID>.glb`; clip luôn `<ID>_MAIN`.

`reviewStatus`:

- `planned`: mới lên kế hoạch, chưa có nội dung.
- `draft`: đang sản xuất, không dùng để dạy.
- `in_review`: chờ technical/expert review, không gọi là đã xác minh.
- `approved`: đủ nguồn, mô tả, duration, evidence và reviewer reference thật.
- `rejected`: không sử dụng; giữ evidence/quyết định để truy vết.

Các trường chưa biết dùng `null`, không đoán reference, dialect, reviewer hay ý nghĩa. Validator bắt lỗi duplicate ID, sai path/clip, enum không hợp lệ và approval metadata thiếu.

## Quiz

`data/quizzes.json` hiện rỗng có chủ đích. Chỉ thêm câu hỏi sau khi sign liên quan có nguồn và quy trình review. `signId` phải tồn tại; `correctChoiceId` phải trỏ đến một choice.

## Publication gate

Frontend phải lọc trạng thái. `draft`/`in_review` chỉ có thể xuất hiện trong chế độ kỹ thuật với nhãn cảnh báo rõ; `planned`/`rejected` không được dùng như bài học. JSON Schema xác minh cấu trúc, không xác minh tính đúng giáo dục.
