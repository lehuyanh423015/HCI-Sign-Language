import { createContext, useContext, useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { LockKeyhole } from 'lucide-react';
import { api, writeApi } from '../services/api';

type User = { id: string; email: string; role: 'admin' | 'learner' };
type Session = { user: User | null };
type AccountState = { user: User | null; loading: boolean; error: string; setUser: (user: User | null) => void };
const AccountContext = createContext<AccountState>({ user: null, loading: false, error: '', setUser: () => {} });
export const useAccount = () => useContext(AccountContext);

export function AccountProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    api<Session>('session', { signal: controller.signal }).then(({ user }) => setUser(user))
      .catch(() => { if (!controller.signal.aborted) setError('Chưa kết nối được máy chủ tài khoản.'); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    const clear = () => setUser(null);
    window.addEventListener("hci-session-expired", clear);
    return () => { controller.abort(); window.removeEventListener("hci-session-expired", clear); };
  }, []);
  return <AccountContext.Provider value={{ user, loading, error, setUser }}>{children}</AccountContext.Provider>;
}

export function RequireAccount({ children, admin = false }: { children: ReactNode; admin?: boolean }) {
  const { user, loading, error } = useAccount();
  const { pathname, search } = useLocation();
  if (loading) return <p role="status">Đang kiểm tra phiên đăng nhập…</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!user) return <Navigate to="/login" replace state={{ returnTo: pathname + search }} />;
  if (admin && user.role !== 'admin') return <section className="panel"><h1>Quyền truy cập quản trị</h1><p>Khu vực này dành cho quản trị viên.</p><Link to="/">Về trang chủ</Link></section>;
  return children;
}

export function AccountPage({ registering }: { registering: boolean }) {
  const { user, setUser, loading } = useAccount();
  const { state } = useLocation();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  if (loading) return <p role="status">Đang kiểm tra phiên đăng nhập…</p>;
  if (user) return <Navigate to={user.role === 'admin' ? '/admin' : '/'} replace />;
  const title = registering ? 'Tạo tài khoản' : 'Đăng nhập';
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fields = new FormData(e.currentTarget);
    setError('');
    setBusy(true);
    try {
      const { user } = await writeApi<Session>(registering ? 'register' :  'login', 'POST', { email: fields.get('email'), password: fields.get('password') });
      if (!user) throw new Error('Không tạo được phiên đăng nhập.');
      setUser(user);
      const requested = state?.returnTo;
      const safe = typeof requested === 'string' && /^\/(?![\\/])/.test(requested) && !requested.includes('\\');
      navigate(safe ? requested : user.role === 'admin' ? '/admin' : '/', { replace: true });
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Có lỗi xảy ra. Hãy thử lại.');
    } finally { setBusy(false); }
  }
  return <section className="panel account-card"><LockKeyhole aria-hidden="true"/><h1>{title}</h1>
    <p>{registering ? 'Lưu tiến độ và lịch ôn theo tài khoản của bạn.' : 'Tiếp tục học và xem lịch ôn của bạn.'}</p>
    <form className="account-form" onSubmit={submit}>
      <label>Email<input name="email" type="email" autoComplete="email" required maxLength={254}/></label>
      <label>Mật khẩu<input name="password" type="password" autoComplete={registering ? 'new-password' : 'current-password'} required minLength={registering ? 12 : undefined} maxLength={128} aria-describedby={registering ? 'password-help' : undefined}/></label>
      {registering && <span id="password-help">Dùng ít nhất 12 ký tự.</span>}
      {error && <p role="alert" className="notice">{error}</p>}
      <button className="primary" disabled={busy}>{busy ? 'Đang xử lý…' : title}</button>
    </form>
    <Link className="textlink" state={state} to={registering ? '/login' : '/register'}>{registering ? 'Đã có tài khoản? Đăng nhập' : 'Chưa có tài khoản? Đăng ký'}</Link>
  </section>;
}

export function AccountMenu() {
  const { user, setUser } = useAccount();
  const [error, setError] = useState('');
  const navigate = useNavigate();
  if (!user) return <Link className="textlink" to="/login">Đăng nhập</Link>;
  async function logout() {
    try {
      await writeApi('logout', 'POST');
      setUser(null);
      navigate('/');
    } catch { setError('Chưa đăng xuất được. Hãy thử lại.'); }
  }
  return <div className="account-menu">{user.role === 'admin' && <Link to="/admin">Quản trị</Link>}<details><summary>Tài khoản</summary><div><p>{user.email}</p><button onClick={logout}>Đăng xuất</button>{error && <p role="alert">{error}</p>}</div></details></div>;
}
