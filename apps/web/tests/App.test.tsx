import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { LearningProvider } from '../src/app/LearningState';
import { AppRoutes } from '../src/app/AppRoutes';

function renderRoute(path: string) {
  return renderToStaticMarkup(
    <MemoryRouter initialEntries={[path]}>
      <LearningProvider profile="demo-a"><AppRoutes /></LearningProvider>
    </MemoryRouter>,
  );
}

describe('application routes', () => {
  it('renders the workspace home with an explicitly technical preview', () => {
    const html = renderRoute('/');
    expect(html).toContain('Không gian học tập');
    expect(html).toContain('Xem bản mẫu 3D');
    expect(html).toContain('Thư viện bài học');
    expect(html).not.toContain('Chưa có GLB');
    expect(html).not.toContain('<h2>S001</h2>');
  });

  it('renders account entry points and public demo routes', () => {
    expect(renderRoute('/login')).toContain('Đăng nhập');
    expect(renderRoute('/register')).toContain('Tạo tài khoản');
    expect(renderRoute('/quiz?demo=1')).toContain('Kiểm tra minh họa');
    expect(renderRoute('/review?demo=1')).toContain('Lịch ôn minh họa');
    expect(renderRoute('/admin')).not.toContain('Quản trị học liệu');
  });

  it('renders the isolated technical viewer warning and controls', () => {
    const html = renderRoute('/technical-viewer');
    expect(html).toContain('TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE');
    expect(html).toContain('Neutral educational avatar prototype');
    expect(html).toContain('Cận cảnh tay phải');
  });

  it('renders the isolated facial viewer warning and actual control surface', () => {
    const html = renderRoute('/technical-facial-viewer');
    expect(html).toContain('TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE');
    expect(html).toContain('Facial &amp; non-manual marker foundation');
    expect(html).toContain('Morph Targets');
    expect(html).toContain('Cận cảnh mặt');
    expect(html).toContain('master-avatar-v1-technical-demo.glb');
  });

  it('renders the isolated S001 technical draft without publishing approved lesson content', () => {
    const html = renderRoute('/technical-sign-preview');
    expect(html).toContain('S001 — Xin chào');
    expect(html).toContain('Chờ xác minh ngôn ngữ');
    expect(html).toContain('Snow v4.2');
    expect(html).toContain('Snow Rig (CC) Blender Foundation');
    expect(html).toContain('NOT YET TESTED');
    expect(html).toContain('S001_MAIN');
    expect(html).toContain('LOCAL STAGING ONLY — educational publication NOT APPROVED');
    expect(html).toContain('s001-snow.glb');
    expect(html).toContain('AvatarSample_A (VRoid)');
  });
});
