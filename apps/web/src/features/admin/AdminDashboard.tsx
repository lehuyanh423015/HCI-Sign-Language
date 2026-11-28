import { useEffect, useState } from 'react';
import { BookOpen, ClipboardList, Search, UsersRound } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../../services/api';

type Learner = { id: string; email: string; lessonsPracticed: number; answers: number; lastPractice: string | null };
type Dashboard = {
  lessonCount: number;
  publishedLessons: number;
  awaitingReview: number;
  questionCount: number;
  publishedQuestions: number;
  learnerCount: number;
  matching: number;
  learners: Learner[];
  page: number;
  pageCount: number;
};
const datetime = new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short', timeStyle: 'short', timeZone: 'Asia/Ho_Chi_Minh' });

export function AdminDashboard() {
  const [params, setParams] = useSearchParams();
  const query = params.get('q') ?? '';
  const page = params.get('page') ?? '1';
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState('');
  const [reload, setReload] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    const search = new URLSearchParams({ q: query, page });
    setData(null);
    setError('');
    api<Dashboard>('admin/dashboard?' + search, { signal: controller.signal })
      .then(result => { if (!controller.signal.aborted) setData(result); })
      .catch(error => { if (!controller.signal.aborted) setError(error.message); });
    return () => controller.abort();
  }, [query, page, reload]);

  return <>
    <header className="admin-heading">
      <div><h1>Tổng quan quản trị</h1><p>Theo dõi học liệu và hoạt động của người học.</p></div>
      <Link className="primary" to="/admin/catalog">Quản lý học liệu</Link>
    </header>
    {error && <p className="notice" role="alert">{error} <button onClick={() => setReload(r => r + 1)}>Thử lại</button></p>}
    {data && <section className="admin-stats" aria-label="Số liệu tổng quan">
      <article className="panel"><BookOpen aria-hidden="true"/><h2>Bài học</h2><strong>{data.lessonCount}</strong><p>{data.publishedLessons} đang mở · {data.awaitingReview} chờ kiểm chứng</p></article>
      <article className="panel"><ClipboardList aria-hidden="true"/><h2>Câu hỏi</h2><strong>{data.questionCount}</strong><p>{data.publishedQuestions} đã xuất bản</p></article>
      <article className="panel"><UsersRound aria-hidden="true"/><h2>Người học</h2><strong>{data.learnerCount}</strong><p>Tài khoản đã đăng ký</p></article>
    </section>}
    <section className="panel" aria-labelledby="learner-list">
      <div className="admin-heading">
        <div><h2 id="learner-list">Danh sách người học</h2><p>Bài đã luyện được tính khi người học trả lời ít nhất một câu của bài.</p></div>
        <form className="account-form admin-search" role="search" onSubmit={event => {
          event.preventDefault();
          const value = String(new FormData(event.currentTarget).get('email') ?? '').trim();
          setParams(value ? { q: value } : {});
        }}>
          <label>Email người học<input name="email" key={query} type="search" maxLength={254} defaultValue={query} placeholder="Nhập email để tìm"/></label>
          <button className="primary"><Search size={18} aria-hidden="true"/>Tìm</button>
        </form>
      </div>
      {!data && !error && <p role="status">Đang tải số liệu…</p>}
      {data && !data.learners.length && <p>{query ? 'Không tìm thấy email phù hợp.' : 'Chưa có tài khoản người học.'}</p>}
      {data && data.learners.length > 0 && <>
        <p>{data.matching} tài khoản{query ? ' phù hợp' : ''}</p>
        <div className="admin-table" tabIndex={0} role="region" aria-label="Bảng hoạt động người học">
          <table>
            <thead><tr><th scope="col">Email</th><th scope="col">Bài đã luyện</th><th scope="col">Lượt trả lời</th><th scope="col">Trả lời gần nhất</th></tr></thead>
            <tbody>{data.learners.map(learner => <tr key={learner.id}>
              <th scope="row">{learner.email}</th><td>{learner.lessonsPracticed}</td><td>{learner.answers}</td>
              <td>{learner.lastPractice ? <time dateTime={learner.lastPractice}>{datetime.format(new Date(learner.lastPractice))}</time> : 'Chưa luyện tập'}</td>
            </tr>)}</tbody>
          </table>
        </div>
        {data.pageCount > 1 && <nav className="actions" aria-label="Phân trang người học">
          <button disabled={data.page <= 1} onClick={() => setParams({ q: query, page: String(data.page - 1) })}>Trang trước</button>
          <span>Trang {data.page} / {data.pageCount}</span>
          <button disabled={data.page >= data.pageCount} onClick={() => setParams({ q: query, page: String(data.page + 1) })}>Trang sau</button>
        </nav>}
      </>}
    </section>
  </>;
}
