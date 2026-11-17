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
  it('renders the lesson and explicit technical placeholder', () => {
    const html = renderRoute('/');
    expect(html).toContain('Kiểm tra ranh giới tích hợp 3D');
    expect(html).toContain('Technical placeholder - not verified sign language.');
  });

  it('renders quiz and review routes', () => {
    expect(renderRoute('/quiz')).toContain('Khu vực câu hỏi');
    expect(renderRoute('/review')).toContain('Danh sách ôn tập');
  });
});
