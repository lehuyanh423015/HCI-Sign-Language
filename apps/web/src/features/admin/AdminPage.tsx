import { useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { api, writeApi } from '../../services/api';
import type { SignMetadata } from '../../types/sign';
import type { Question } from '../lessons/catalog';

type Catalog = { signs: SignMetadata[]; quizzes: Question[] };
const labels: Record<string, string> = { planned: 'Dự kiến', draft: 'Bản nháp', in_review: 'Chờ kiểm chứng', approved: 'Đã duyệt', rejected: 'Từ chối' };
const nullable = (fields: FormData, key: string) => String(fields.get(key) ?? '').trim() || null;
const newSign: SignMetadata = {
  id: '', label: null, description: null, regionalVariant: null, referenceSource: null,
  assignedAnimator: 'Le Huy Anh', glbPath: '', animationClip: '', durationSeconds: null,
  reviewStatus: 'draft', verificationEvidence: null, reviewerReference: null, lastUpdatedAt: '',
};
const newQuiz: Question = { id: '', signId: '', prompt: '', choices: [], correctChoiceId: '', reviewStatus: 'draft' };

function Status({ value, sign }: { value: string; sign?: boolean }) {
  return <label>Trạng thái<select name="reviewStatus" defaultValue={value}>
    {Object.entries(labels).filter(([key]) => sign || key !== 'planned').map(([key, label]) => <option key={key} value={key}>{label}</option>)}
  </select></label>;
}

function SignFields({ sign }: { sign: SignMetadata }) {
  return <>
    <label>Mã ký hiệu<input name="id" required pattern="S[0-9]{3}" placeholder="S007" defaultValue={sign.id} readOnly={!!sign.id}/></label>
    <label>Tên ký hiệu<input name="label" defaultValue={sign.label ?? ''}/></label>
    <label>Mô tả<textarea name="description" defaultValue={sign.description ?? ''}/></label>
    <label>Biến thể vùng miền<input name="regionalVariant" defaultValue={sign.regionalVariant ?? ''}/></label>
    <label>Nguồn tham chiếu<input name="referenceSource" defaultValue={sign.referenceSource ?? ''}/></label>
    <label>Người phụ trách<select name="assignedAnimator" defaultValue={sign.assignedAnimator}><option>Le Huy Anh</option><option>Le Quang Mien</option></select></label>
    <label>Thời lượng (giây)<input name="durationSeconds" type="number" min="0.01" step="any" defaultValue={sign.durationSeconds ?? ''}/></label>
    <label>Người kiểm chứng hoặc mã phiếu duyệt<input name="reviewerReference" defaultValue={sign.reviewerReference ?? ''}/></label>
    <label>Minh chứng kiểm chứng (mỗi dòng một mục)<textarea name="verificationEvidence" defaultValue={sign.verificationEvidence?.join('\n') ?? ''}/></label>
    <Status sign value={sign.reviewStatus}/>
  </>;
}

function QuizFields({ quiz, signs }: { quiz: Question; signs: SignMetadata[] }) {
  const [choices, setChoices] = useState(quiz.choices.length ? quiz.choices : [{ id: 'A', label: '' }, { id: 'B', label: '' }]);
  return <>
    <label>Mã câu hỏi<input name="id" required pattern="Q[0-9]{3}" placeholder="Q001" defaultValue={quiz.id} readOnly={!!quiz.id}/></label>
    <label>Ký hiệu<select name="signId" required defaultValue={quiz.signId}><option value="">Chọn ký hiệu</option>
      {signs.map(s => <option key={s.id} value={s.id}>{s.id} · {s.label ?? labels[s.reviewStatus]}</option>)}
    </select></label>
    <label>Câu hỏi<textarea name="prompt" required defaultValue={quiz.prompt}/></label>
    {choices.map((c, index) => <label key={index}>Mã và nội dung phương án {index + 1}
      <span className="choice-editor"><input name="choiceId" required aria-label={'Mã phương án ' + (index + 1)} defaultValue={c.id}/><input name="choiceLabel" required aria-label={'Nội dung phương án ' + (index + 1)} defaultValue={c.label}/></span>
    </label>)}
    <div className="actions"><button type="button" onClick={() => setChoices([...choices, { id: '', label: '' }])}>Thêm phương án</button>
      {choices.length > 2 && <button type="button" onClick={() => setChoices(choices.slice(0, -1))}>Bỏ phương án cuối</button>}</div>
    <label>Mã đáp án đúng<input name="correctChoiceId" required defaultValue={quiz.correctChoiceId}/></label>
    <Status value={quiz.reviewStatus}/>
  </>;
}

export function AdminPage() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [kind, setKind] = useState<'sign' | 'quiz'>('sign');
  const [editing, setEditing] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    api<Catalog>('admin/catalog', { signal: controller.signal }).then(setCatalog)
      .catch(error => { if (!controller.signal.aborted) setError(error.message); });
    return () => controller.abort();
  }, []);
  if (!catalog) return error ? <p role="alert">{error}</p> : <p role="status">Đang tải danh mục…</p>;
  const records = kind === 'sign' ? catalog.signs : catalog.quizzes;
  async function save(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const id = String(f.get('id'));
    const reviewStatus = String(f.get('reviewStatus'));
    const evidence = nullable(f, 'verificationEvidence')?.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
    const record = kind === 'sign' ? {
      id, reviewStatus, label: nullable(f, 'label'), description: nullable(f, 'description'),
      regionalVariant: nullable(f, 'regionalVariant'), referenceSource: nullable(f, 'referenceSource'),
      assignedAnimator: f.get('assignedAnimator'), durationSeconds: nullable(f, 'durationSeconds') === null ? null : Number(f.get('durationSeconds')),
      reviewerReference: nullable(f, 'reviewerReference'), verificationEvidence: evidence ?? null,
      glbPath: 'models/signs/' + id + '.glb', animationClip: id + '_MAIN',
    } : {
      id, reviewStatus, signId: f.get('signId'), prompt: nullable(f, 'prompt'),
      choices: f.getAll('choiceId').map((value, index) => ({ id: String(value).trim(), label: String(f.getAll('choiceLabel')[index]).trim() })),
      correctChoiceId: nullable(f, 'correctChoiceId'),
    };
    setError('');
    setMessage('');
    setSaving(true);
    try {
      await writeApi('admin/' + kind, 'PUT', { record, expected: records.find(row => row.id === editing) ?? null });
      setCatalog(await api<Catalog>('admin/catalog'));
      setEditing(null);
      setMessage('Đã lưu ' + id + '.');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Chưa lưu được học liệu.');
    } finally { setSaving(false); }
  }
  return <><h1>Quản trị học liệu</h1><p>Quản lý danh mục ký hiệu và bài kiểm tra nhận biết.</p><Link className="textlink" to="/admin">Về dashboard</Link>
    <div className="actions">{(['sign','quiz'] as const).map(value => <button key={value} disabled={saving} aria-pressed={kind === value} onClick={() => { setKind(value); setEditing(null); setError(''); setMessage(''); }}>{value === 'sign' ? 'Ký hiệu' : 'Câu hỏi'}</button>)}</div>
    {message && <p role="status">{message}</p>}
    <section className="panel">
      <button className="primary" disabled={saving} onClick={() => { setEditing(''); setError(''); }}>Thêm {kind === 'sign' ? 'ký hiệu' : 'câu hỏi'}</button>
      {records.map(record => <div className="listrow" key={record.id}><strong>{record.id} · {('label' in record ? record.label : record.prompt) ?? 'Chưa đặt tên'}</strong><span>{labels[record.reviewStatus]}</span><button disabled={saving} onClick={() => { setEditing(record.id); setError(''); }}>Chỉnh sửa</button></div>)}
      {!records.length && <p>Danh mục hiện chưa có mục nào.</p>}
    </section>
    {editing !== null && <section className="panel"><h2>{editing ? 'Chỉnh sửa ' + editing : 'Tạo mục mới'}</h2>
      <form key={kind + editing} className="account-form" onSubmit={save}><fieldset disabled={saving}>
        {kind === 'sign' ? <SignFields sign={catalog.signs.find(s => s.id === editing) ?? newSign}/> : <QuizFields quiz={catalog.quizzes.find(q => q.id === editing) ?? newQuiz} signs={catalog.signs}/>}
      </fieldset>
      {error && <p role="alert" className="notice">{error}</p>}
      <div className="actions"><button className="primary" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu học liệu'}</button><button type="button" disabled={saving} onClick={() => setEditing(null)}>Hủy</button></div>
      </form>
    </section>}
  </>;
}
