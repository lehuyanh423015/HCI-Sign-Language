import { createHash, randomBytes } from 'node:crypto';
import { inspectGlb } from '../../tools/inspect-glb.mjs';
import { resolve } from 'node:path';
import { authenticate, createAccount, openStore, root, validCredentials } from './store.mjs';
import { validateCanonicalData, validateSignsData, validateQuizData } from '../../tools/validate-data.mjs';
import { applyAnswer } from '../web/src/features/adaptive/history.ts';

const TTL = 7 * 86400;
const signId = /^S\d{3}$/;
const questionId = /^Q\d{3}$/;
const digest = token => createHash('sha256').update(token).digest('hex');
const fail = (status, message) => { throw Object.assign(new Error(message), { status }); };
const cookie = (token, age, secure) => `hci_session=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${age}${secure ? '; Secure' : ''}`;
function send(res, status, value) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' });
  res.end(JSON.stringify(value));
}
async function body(req) {
  if (req.headers['content-type']?.split(';')[0] !== 'application/json') fail(415, 'Cần dữ liệu JSON.');
  if (Number(req.headers['content-length']) > 65536) fail(413, 'Dữ liệu quá lớn.');
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 65536) fail(413, 'Dữ liệu quá lớn.');
    chunks.push(chunk);
  }
  let value;
  try { value = JSON.parse(Buffer.concat(chunks).toString()); } catch { fail(400, 'JSON không hợp lệ.'); }
  if (!value || Array.isArray(value) || typeof value !== 'object') fail(400, 'Dữ liệu không hợp lệ.');
  return value;
}
export function createApi({ db = openStore(), assetRoot = resolve(root, 'apps/web/public'), secure = !!process.env.HCI_ORIGIN?.startsWith('https:'), origin = process.env.HCI_ORIGIN, now = Date.now } = {}) {
  const baseline = validateCanonicalData({ silent: true });
  if (baseline.errors.length) throw new Error(baseline.errors.join('\n'));
  const attempts = new Map();
  function throttle(ip) {
    const time = now();
    for (const [key, bucket] of attempts) if (bucket.until <= time) attempts.delete(key);
    const bucket = attempts.get(ip) ?? { count: 0, until: time + 60000 };
    if (bucket.count >= 8) fail(429, 'Bạn thử quá nhiều lần. Hãy thử lại sau một phút.');
    bucket.count += 1;
    attempts.set(ip, bucket);
  }
  function catalog() {
    const signs = new Map(baseline.signs.map(s => [s.id, s]));
    const quizzes = new Map(baseline.quizzes.map(q => [q.id, q]));
    for (const { kind, id, record } of db.prepare('SELECT * FROM catalog').all()) {
      (kind === 'sign' ? signs : quizzes).set(id, JSON.parse(record));
    }
    return { signs: [...signs.values()], quizzes: [...quizzes.values()] };
  }
  function available(sign) {
    if (sign.reviewStatus !== 'approved' || !/^models\/signs\/S\d{3}\.glb$/.test(sign.glbPath)) return false;
    try { inspectGlb(resolve(assetRoot, sign.glbPath), sign.animationClip); return true; }
    catch { return false; }
  }
  function published() {
    const { signs, quizzes } = catalog();
    const live = signs.filter(available);
    return { signs: live, quizzes: quizzes.filter(q => q.reviewStatus === 'approved' && live.some(s => s.id === q.signId)) };
  }
  function saveRecord(kind, { record: input, expected }) {
    if (!input || typeof input !== 'object' || Array.isArray(input) || expected === undefined) fail(400, 'Thiếu dữ liệu học liệu.');
    const { signs, quizzes } = catalog();
    const record = kind === 'sign' ? { ...input, lastUpdatedAt: new Date(now()).toISOString().replace(/\.\d{3}Z$/, 'Z') } : input;
    const collection = kind === 'sign' ? signs : quizzes;
    const previous = collection.find(item => item.id === record.id) ?? null;
    if (JSON.stringify(previous) !== JSON.stringify(expected)) fail(409, 'Học liệu đã thay đổi. Hãy tải lại trang trước khi lưu.');
    const current = collection.filter(item => item.id !== record.id);
    const errors = kind === 'sign'
      ? validateSignsData([...current, record])
      : validateQuizData([...current, record], new Set(signs.map(s => s.id)));
    if (errors.length) fail(400, 'Kiểm tra lại các trường: ' + errors.join('; '));
    if (kind === 'quiz' && new Set(record.choices.map(c => c.id)).size !== record.choices.length) fail(400, 'Mã phương án phải khác nhau.');
    if (record.reviewStatus === 'approved' && (kind === 'sign' ? !available(record) : !signs.some(s => s.id === record.signId && available(s)))) {
      fail(400, 'Cần ký hiệu đã kiểm chứng và tệp GLB đúng đường dẫn trước khi xuất bản.');
    }
    db.prepare('INSERT INTO catalog VALUES (?,?,?) ON CONFLICT(kind,id) DO UPDATE SET record=excluded.record').run(kind, record.id, JSON.stringify(record));
    return record;
  }
  return async function api(req, res, next) {
    const pathname = (req.url ?? '').split('?')[0];
    if (/^\/data\/(signs|quizzes)\.json$/.test(pathname)) return send(res, 404, { message: 'Dùng danh mục học liệu đã xuất bản.' });
    if (!pathname.startsWith('/api/')) return next();
    try {
      const method = req.method;
      if (method !== 'GET') {
        const expected = origin ?? ((secure ? 'https://' : 'http://') + req.headers.host);
        if (req.headers.origin !== expected) fail(403, 'Nguồn yêu cầu không hợp lệ.');
      }
      const token = /(?:^|;\s*)hci_session=([a-f0-9]{64})(?:;|$)/.exec(req.headers.cookie ?? '')?.[1];
      const session = token && digest(token);
      const account = session && db.prepare('SELECT a.id, a.email, a.role, a.resume FROM sessions s JOIN accounts a ON a.id=s.account_id WHERE s.token_hash=? AND s.expires>?').get(session, now());
      const identity = account ? { id: account.id, email: account.email, role: account.role } : null;
      if (method === 'GET' && pathname === '/api/session') return send(res, 200, { user: identity });
      if (method === 'POST' && ['/api/login', '/api/register'].includes(pathname)) {
        throttle(req.socket.remoteAddress);
        const input = await body(req);
        const email = typeof input.email === 'string' ? input.email.trim().toLowerCase() : '';
        if (!validCredentials(email, input.password)) fail(400, 'Nhập email hợp lệ và mật khẩu từ 12 đến 128 ký tự.');
        const joining = pathname === '/api/register';
        const user = joining ? await createAccount(db, email, input.password, 'learner') : await authenticate(db, email, input.password);
        if (!user) fail(joining ? 409 : 401, joining ? 'Email này đã được đăng ký.' : 'Email hoặc mật khẩu chưa đúng.');
        if (session) db.prepare('DELETE FROM sessions WHERE token_hash=?').run(session);
        db.prepare('DELETE FROM sessions WHERE expires<=?').run(now());
        const fresh = randomBytes(32).toString('hex');
        db.prepare('INSERT INTO sessions VALUES(?,?,?)').run(digest(fresh), user.id, now()+TTL*1000);
        res.setHeader('Set-Cookie', cookie(fresh, TTL, secure));
        return send(res, joining ? 201 : 200, { user });
      }
      if (method === 'POST' && pathname === '/api/logout') {
        if (session) db.prepare('DELETE FROM sessions WHERE token_hash=?').run(session);
        res.setHeader('Set-Cookie', cookie('', 0, secure));
        return send(res, 200, { user: null });
      }
      if (method === 'GET' && pathname === '/api/catalog') {
        const data = published();
        return send(res, 200, { signs: data.signs, quizzes: data.quizzes.map(({ correctChoiceId: _, ...q }) => q) });
      }
      if (!account) fail(401, 'Hãy đăng nhập để tiếp tục.');
      if (pathname.startsWith('/api/admin/')) {
        if (account.role !== 'admin') fail(403, 'Khu vực này dành cho quản trị viên.');
        if (method === 'GET' && pathname === '/api/admin/catalog') return send(res, 200, catalog());
        if (method === 'PUT' && ['/api/admin/sign', '/api/admin/quiz'].includes(pathname)) {
          const input = await body(req);
          db.exec('BEGIN IMMEDIATE');
          let saved;
          try {
            saved = saveRecord(pathname.endsWith('sign') ? 'sign' : 'quiz', input);
            db.exec('COMMIT');
          } catch (error) {
            db.exec('ROLLBACK');
            throw error;
          }
          return send(res, 200, saved);
        }
      }
      if (method === 'GET' && pathname === '/api/progress') {
        const entries = db.prepare('SELECT entry FROM progress WHERE account_id=?').all(account.id).map(row => JSON.parse(row.entry));
        return send(res, 200, { resume: account.resume, entries });
      }
      if (method === 'PUT' && pathname === '/api/progress/resume') {
        const { id } = await body(req);
        if (!published().signs.some(s => s.id === id)) fail(400, 'Bài học chưa khả dụng.');
        db.prepare('UPDATE accounts SET resume=? WHERE id=?').run(id, account.id);
        return send(res, 200, { resume: id });
      }
      if (method === 'POST' && pathname === '/api/progress/answer') {
        const { attempt, question, choice, review } = await body(req);
        if (typeof attempt !== 'string' || !/^[a-f0-9-]{36}$/.test(attempt) ||
          typeof question !== 'string' || !questionId.test(question) || typeof review !== 'boolean') fail(400, 'Lượt trả lời không hợp lệ.');
        const q = published().quizzes.find(q => q.id === question);
        if (!q || !q.choices.some(c => c.id === choice) || !signId.test(q.signId)) fail(400, 'Câu hỏi hoặc đáp án chưa khả dụng.');
        db.exec('BEGIN IMMEDIATE');
        try {
          const existing = db.prepare('SELECT result FROM answers WHERE account_id=? AND attempt_id=?').get(account.id, attempt);
          if (existing) {
            db.exec('COMMIT');
            return send(res, 200, JSON.parse(existing.result));
          }
          const row = db.prepare('SELECT entry FROM progress WHERE account_id=? AND sign_id=?').get(account.id, q.signId);
          const correct = q.correctChoiceId === choice;
          const entry = applyAnswer(row ? JSON.parse(row.entry) : undefined, account.id, q.signId, correct ? 'correct' : 'wrong', review, new Date(now()));
          const result = { correct, entry };
          db.prepare('INSERT INTO answers VALUES (?,?,?)').run(account.id, attempt, JSON.stringify(result));
          db.prepare('INSERT INTO progress VALUES (?,?,?) ON CONFLICT(account_id,sign_id) DO UPDATE SET entry=excluded.entry').run(account.id,q.signId,JSON.stringify(entry));
          db.exec('COMMIT');
          return send(res, 200, result);
        } catch (error) {
          db.exec('ROLLBACK');
          throw error;
        }
      }
      fail(404, 'Không tìm thấy địa chỉ API.');
    } catch (error) {
      if (!error.status) console.error(error);
      if (!res.headersSent && !res.destroyed) send(res, error.status ?? 500, { message: error.status ? error.message : 'Máy chủ gặp lỗi. Hãy thử lại.' });
    }
  };
}
