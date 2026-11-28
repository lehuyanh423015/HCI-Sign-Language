import { createAccount, openStore, validCredentials } from './store.mjs';

const email = process.env.HCI_ADMIN_EMAIL?.trim().toLowerCase();
const password = process.env.HCI_ADMIN_PASSWORD;
if (!validCredentials(email, password)) {
  throw new Error('Cần HCI_ADMIN_EMAIL hợp lệ và HCI_ADMIN_PASSWORD từ 12 đến 128 ký tự.');
}
const db = openStore();
try {
  const account = await createAccount(db, email, password, 'admin');
  if (!account) throw new Error('Email đã tồn tại. Hãy dùng email riêng cho tài khoản quản trị.');
  console.log('Đã tạo tài khoản quản trị.');
} finally {
  db.close();
}
