import { NavLink } from 'react-router-dom';
import { AppRoutes } from './AppRoutes';

const navItems = [
  { to: '/', label: 'Bài học' },
  { to: '/quiz', label: 'Câu hỏi' },
  { to: '/review', label: 'Ôn tập' },
];

export function App() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <p className="eyebrow">HCI · Nền tảng kỹ thuật</p>
          <h1>VSL 3D Learning</h1>
        </div>
        <nav aria-label="Điều hướng chính">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => (isActive ? 'active' : undefined)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main>
        <AppRoutes />
      </main>
      <footer>
        Chỉ dùng nội dung có trạng thái <code>approved</code> cho học tập và kiểm thử người dùng.
      </footer>
    </div>
  );
}
