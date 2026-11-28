import { useEffect, useRef, useState } from "react";
import { NavLink, Link, useLocation } from "react-router-dom";
import {
  Hand,
  House,
  BookOpen,
  History,
  Box,
  ScanFace,
  FlaskConical,
  ChevronRight,
  UserRound,
} from "lucide-react";
import { AppRoutes } from "./AppRoutes";
import { AccountMenu, useAccount } from './Account';
import { LearningProvider } from "./LearningState";

const links = [
  { to: "/", label: "Trang chủ", Icon: House },
  { to: "/lessons", label: "Bài học", Icon: BookOpen },
  { to: "/review", label: "Ôn tập", Icon: History },
];
const tools = [
  { to: "/technical-sign-preview", label: "Bản mẫu ký hiệu", Icon: Box },
  { to: "/technical-viewer", label: "Kiểm tra nhân vật", Icon: Hand },
  {
    to: "/technical-facial-viewer",
    label: "Biểu cảm khuôn mặt",
    Icon: ScanFace,
  },
  { to: "/demo", label: "Mô phỏng ôn tập", Icon: FlaskConical },
];
export function App() {
  const [profile, setProfile] = useState(() => {
    try {
      return localStorage.getItem("hci-vsl:profile") === "demo-b"
        ? "demo-b"
        : "demo-a";
    } catch {
      return "demo-a";
    }
  });
  const { user } = useAccount();
  const { pathname: path, search } = useLocation();
  const demo = path.startsWith('/demo') || new URLSearchParams(search).get('demo') === '1';
  const activeProfile = user && !demo ? user.id : profile;
  const lastPath = useRef(path);
  useEffect(() => {
    if (path !== lastPath.current) {
      lastPath.current = path;
      document.getElementById('content')?.focus({preventScroll:true});
      window.scrollTo(0,0);
    }
  }, [path]);
  const group =
    [...links, ...tools].find((x) =>
      x.to === "/" ? path === "/" : path.startsWith(x.to),
    )?.label ??
    (path === '/admin' ? 'Quản trị' : path === '/login' || path === '/register' ? 'Tài khoản' : path.startsWith("/results") ? "Kết quả" : "Kiểm tra nhận biết");
  return (
    <LearningProvider key={activeProfile} profile={activeProfile} account={!!user && !demo}>
      <div className="workspace">
        <a className="skip" href="#content">
          Đến nội dung
        </a>
        <aside className="sidebar">
          <Link className="brand" to="/">
            <span className="brandmark">
              <Hand />
            </span>
            Ký hiệu <b>3D</b>
          </Link>
          <nav aria-label="Điều hướng chính">
            {links.map(({ to, label, Icon }) => (
              <NavLink key={to} end={to === "/"} to={to}>
                <Icon />
                {label}
              </NavLink>
            ))}
          </nav>
          <details
            className="toolmenu"
            open={tools.some((t) => t.to === path) || undefined}
          >
            <summary>Công cụ dự án</summary>
            {tools.map(({ to, label, Icon }) => (
              <NavLink key={to} to={to}>
                <Icon />
                {label}
              </NavLink>
            ))}
          </details>
        </aside>
        <div className="stage">
          <header className="topbar">
            <span className="crumb">
              <Hand size={18} /> Không gian học <ChevronRight size={15} />{" "}
              <strong>{group}</strong>
            </span>
            <div className="account-actions"><AccountMenu/>{demo && <label className="profile">
              <UserRound size={18} />
              <select
                aria-label="Hồ sơ minh họa"
                value={profile}
                onChange={(e) => {
                  setProfile(e.target.value);
                  try {
                    localStorage.setItem("hci-vsl:profile", e.target.value);
                  } catch {
                    /* session only */
                  }
                }}
              >
                <option value="demo-a">Hồ sơ A</option>
                <option value="demo-b">Hồ sơ B</option>
              </select>
            </label>}</div>
          </header>
          <main id="content" tabIndex={-1}>
            <AppRoutes />
            <details className="mobile-tools">
              <summary>Công cụ dự án</summary>
              {tools.map((t) => (
                <Link key={t.to} to={t.to}>
                  {t.label}
                </Link>
              ))}
            </details>
          </main>
        </div>
        <nav className="mobile-nav" aria-label="Điều hướng di động">
          {links.map(({ to, label, Icon }) => (
            <NavLink key={to} end={to === "/"} to={to}>
              <Icon />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </LearningProvider>
  );
}
