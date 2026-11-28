import { DatabaseSync } from 'node:sqlite';
import { randomBytes, randomUUID, scrypt, timingSafeEqual } from 'node:crypto';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

export const root = fileURLToPath(new URL('../../', import.meta.url));
export const databasePath = () => resolve(process.env.HCI_DATABASE || resolve(root, '.hci-private/app.sqlite'));
const derive = promisify(scrypt);
export const passwordHash = (password, salt) => derive(password, salt, 64, { N: 32768, r: 8, p: 3, maxmem: 64 * 1024 ** 2 });
export const validCredentials = (email, password) => typeof email === 'string' && email.length <= 254 &&
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) && typeof password === 'string' && password.length >= 12 && password.length <= 128;

export function openStore(path = databasePath()) {
  if (path !== ':memory:') mkdirSync(dirname(path), { recursive: true });
  const db = new DatabaseSync(path);
  db.exec(`
    PRAGMA foreign_keys = ON;
    PRAGMA busy_timeout = 3000;
    CREATE TABLE IF NOT EXISTS accounts (
      id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, salt TEXT NOT NULL, hash BLOB NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('learner','admin')), resume TEXT NOT NULL DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS sessions (
      token_hash TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id), expires INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS progress (
      account_id TEXT NOT NULL REFERENCES accounts(id), sign_id TEXT NOT NULL, entry TEXT NOT NULL,
      PRIMARY KEY (account_id, sign_id)
    );
    CREATE TABLE IF NOT EXISTS answers (
      account_id TEXT NOT NULL REFERENCES accounts(id), attempt_id TEXT NOT NULL, result TEXT NOT NULL,
      PRIMARY KEY (account_id, attempt_id)
    );
    CREATE TABLE IF NOT EXISTS catalog (
      kind TEXT NOT NULL, id TEXT NOT NULL, record TEXT NOT NULL, PRIMARY KEY (kind,id)
    );
  `);
  return db;
}
export async function createAccount(db, email, password, role) {
  const salt = randomBytes(16).toString('hex');
  const hash = await passwordHash(password, salt);
  const id = randomUUID();
  const result = db.prepare('INSERT OR IGNORE INTO accounts(id,email,salt,hash,role) VALUES(?,?,?,?,?)').run(id,email,salt,hash,role);
  return result.changes ? { id, email, role } : null;
}
export async function authenticate(db, email, password) {
  const row = db.prepare('SELECT * FROM accounts WHERE email = ?').get(email);
  const hash = await passwordHash(password, row?.salt ?? '00000000000000000000000000000000');
  if (!row || !timingSafeEqual(hash, row.hash)) return null;
  return { id: row.id, email: row.email, role: row.role };
}

