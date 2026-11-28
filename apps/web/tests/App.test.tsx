import { renderToStaticMarkup } from 'react-dom/server';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AppRoutes } from '../src/app/AppRoutes';

function renderRoute(path: string) {
  return renderToStaticMarkup(
    <MemoryRouter initialEntries={[path]}>
      <AppRoutes />
    </MemoryRouter>,
  );
}

describe('application routes', () => {
  it('renders the neutral technical viewer on the landing route', () => {
    const html = renderRoute('/');
    expect(html).toContain('Avatar giáo dục trung tính');
    expect(html).toContain('TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE');
    expect(html).toContain('Cận cảnh tay phải');
    expect(html).not.toContain('Chưa có GLB');
    expect(html).not.toContain('<h2>S001</h2>');
  });

  it('renders quiz and review routes', () => {
    expect(renderRoute('/quiz')).toContain('Khu vực câu hỏi');
    expect(renderRoute('/review')).toContain('Danh sách ôn tập');
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

  it('renders the isolated S002 technical draft without publishing approved lesson content', () => {
    const html = renderRoute('/technical-sign-preview');
    expect(html).toContain('S002 — Cảm ơn');
    expect(html).toContain('TECHNICAL DRAFT');
    expect(html).toContain('NOT YET TESTED — owner review required');
    expect(html).toContain('NOT YET TESTED');
    expect(html).toContain('S002_MAIN');
    expect(html).toContain('LOCAL STAGING ONLY — educational publication NOT APPROVED');
    expect(html).toContain('s002-cam-on-technical-draft.glb');
  });
});
