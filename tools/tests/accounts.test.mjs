import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { once } from 'node:events';
import { test } from 'node:test';
import { createApi } from '../../apps/server/api.mjs';
import { createAccount, openStore } from '../../apps/server/store.mjs';

test('sessions, roles, publication and progress isolation', async t => {
  const db = openStore(':memory:');
  const assetRoot = mkdtempSync(join(tmpdir(), 'hci-api-'));
  let now = Date.now();
  const server = createServer((req, res) => api(req, res, () => res.writeHead(404).end()));
  const api = createApi({ db, assetRoot, now: () => now });
  await createAccount(db, 'admin@example.test', 'test-only password', 'admin');
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(() => { server.closeAllConnections(); server.close(); db.close(); rmSync(assetRoot, {recursive:true,force:true}); });
  const origin = 'http://127.0.0.1:' + server.address().port;
  async function request(path, { method = 'GET', data, cookie, source = origin } = {}) {
    const response = await fetch(origin + '/api/' + path, {
      method,
      headers: { Origin: source, ...(cookie && { Cookie: cookie }), ...(data && { 'Content-Type': 'application/json' }) },
      body: data && JSON.stringify(data),
    });
    const session = response.headers.get('set-cookie');
    return { status: response.status, body: await response.json(), session, cookie: session?.split(';')[0] };
  }
  const password = 'test-only password';
  const register = email => request('register', { method: 'POST', data: { email, password, role: 'admin' } });
  const first = await register('one@example.test');
  const second = await register('two@example.test');
  assert.equal(first.status, 201);
  assert.match(first.session, /HttpOnly; SameSite=Lax/);
  assert.equal(first.body.user.role, 'learner');
  assert.notEqual(first.body.user.id, second.body.user.id);
  assert.equal((await request('admin/catalog')).status, 401);
  assert.equal((await request('admin/catalog', first)).status, 403);
  assert.equal((await request('admin/sign', { method: 'PUT', data: {}, cookie: first.cookie })).status, 403);
  assert.equal((await request('login', { method: 'POST', source: 'https://different.invalid', data: {} })).status, 403);
  const admin = await request('login', { method: 'POST', data: { email: 'admin@example.test', password } });
  assert.equal(admin.body.user.role, 'admin');
  const catalog = await request('admin/catalog', admin);
  const candidate = { ...catalog.body.signs[1], reviewStatus: 'approved' };
  let expectedSign = catalog.body.signs[1];
  async function save(kind, record) {
    const expected = kind === 'sign' ? expectedSign : null;
    const response = await request('admin/' + kind, { method: 'PUT', data: { record, expected }, cookie: admin.cookie });
    if (kind === 'sign' && response.status === 200) expectedSign = response.body;
    return response;
  }
  assert.equal((await save('sign', candidate)).status, 400);
  // A synthetic asset is used only in this isolated test database.
  Object.assign(candidate, { label: 'Test fixture', description: 'Test fixture', referenceSource: 'test', reviewerReference: 'test', verificationEvidence: ['test'], durationSeconds: 1 });
  assert.equal((await save('sign', candidate)).status, 400);
  const json = Buffer.from(JSON.stringify({ animations: [{ name: candidate.animationClip }], meshes: [{}], skins: [{}] }));
  const glb = Buffer.alloc(20 + json.length);
  glb.write('glTF');
  glb.writeUInt32LE(2, 4);
  glb.writeUInt32LE(glb.length, 8);
  glb.writeUInt32LE(json.length, 12);
  glb.writeUInt32LE(0x4e4f534a, 16);
  json.copy(glb, 20);
  mkdirSync(join(assetRoot, 'models', 'signs'), { recursive: true });
  writeFileSync(join(assetRoot, candidate.glbPath), glb);
  assert.equal((await save('sign', candidate)).status, 200);
  assert.equal((await request('admin/sign', { method: 'PUT', data: { record: candidate, expected: null }, cookie: admin.cookie })).status, 409);
  const q = { id: 'Q001', signId: candidate.id, prompt: 'Test?', choices: [{ id: 'A', label: 'A' }, { id: 'B', label: 'B' }], correctChoiceId: 'A', reviewStatus: 'approved' };
  assert.equal((await save('quiz', q)).status, 200);
  const live = await request('catalog');
  assert.equal(live.body.quizzes.length, 1);
  assert.equal(live.body.quizzes[0].correctChoiceId, undefined);
  assert.equal((await save('sign', { ...candidate, reviewStatus: 'draft' })).status, 200);
  assert.equal((await request('catalog')).body.quizzes.length, 0);
  assert.equal((await save('sign', candidate)).status, 200);
  const answer = { attempt: '12345678-1234-1234-1234-123456789012', question: 'Q001', choice: 'B', review: false };
  assert.equal((await request('progress/resume', { method: 'PUT', data: { id: candidate.id }, cookie: first.cookie })).status, 200);
  const submit = () => request('progress/answer', { method: 'POST', data: answer, cookie: first.cookie });
  assert.equal((await submit()).body.correct, false);
  assert.equal((await submit()).body.entry.wrongStreak, 1);
  const progress = await request('progress', first);
  assert.equal(progress.body.entries.length, 1);
  assert.equal(progress.body.resume, candidate.id);
  assert.deepEqual((await request('progress', second)).body, { resume: '', entries: [] });
  assert.equal((await request('logout', { method: 'POST', cookie: first.cookie })).status, 200);
  assert.equal((await request('progress', first)).status, 401);
  now += 8 * 86400 * 1000;
  assert.equal((await request('session', second)).body.user, null);
});
