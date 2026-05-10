import { useEffect, useMemo, useRef, useState } from 'react';
import { CalendarDays, FileSignature, HeartPulse, Languages, LayoutDashboard, LogOut, Plus, Search, Stethoscope, Users, WalletCards } from 'lucide-react';
import { clinicName, isSupabaseConfigured, supabase } from './supabase';

type Lang = 'en' | 'ar';
type Tab = 'dashboard' | 'patients' | 'appointments' | 'sessions' | 'billing' | 'signature';
type Patient = { id: string; code: string; name: string; phone?: string; diagnosis?: string; age?: number; gender?: string; created_at?: string };
type Appointment = { id: string; patient_name: string; therapist_name: string; starts_at: string; status: string; notes?: string };
type Session = { id: string; patient_name: string; therapist_name: string; session_date: string; pain_before?: number; pain_after?: number; soap?: string };

const tr = {
  en: {
    signIn: 'Sign in', email: 'Email', password: 'Password', demo: 'Demo mode', dashboard: 'Dashboard', patients: 'Patients', appointments: 'Appointments', sessions: 'Sessions', billing: 'Billing', signature: 'Signature',
    today: 'Today', activePatients: 'Active patients', revenue: 'Revenue', satisfaction: 'Satisfaction', addPatient: 'Add patient', search: 'Search patients, phone, diagnosis...', name: 'Name', phone: 'Phone', diagnosis: 'Diagnosis', age: 'Age', gender: 'Gender', save: 'Save', clear: 'Clear', exportCsv: 'Export CSV',
    upcoming: 'Upcoming appointments', therapist: 'Therapist', status: 'Status', soap: 'SOAP sessions', beforeAfter: 'Pain before/after', invoices: 'Invoices', paid: 'Paid', pending: 'Pending', handwriting: 'Doctor handwriting signature', draw: 'Draw signature below and save it to Supabase Storage.', saveSignature: 'Save signature', logout: 'Logout', notConfigured: 'Supabase is not configured yet. Add environment variables in Cloudflare Pages.', professional: 'Professional PT clinic system',
  },
  ar: {
    signIn: 'تسجيل الدخول', email: 'البريد الإلكتروني', password: 'كلمة المرور', demo: 'وضع العرض', dashboard: 'الرئيسية', patients: 'المرضى', appointments: 'المواعيد', sessions: 'الجلسات', billing: 'الحسابات', signature: 'التوقيع',
    today: 'اليوم', activePatients: 'مرضى نشطون', revenue: 'الإيراد', satisfaction: 'الرضا', addPatient: 'إضافة مريض', search: 'بحث بالاسم أو الهاتف أو التشخيص...', name: 'الاسم', phone: 'الهاتف', diagnosis: 'التشخيص', age: 'العمر', gender: 'النوع', save: 'حفظ', clear: 'مسح', exportCsv: 'تصدير CSV',
    upcoming: 'المواعيد القادمة', therapist: 'الأخصائي', status: 'الحالة', soap: 'جلسات SOAP', beforeAfter: 'الألم قبل/بعد', invoices: 'الفواتير', paid: 'مدفوع', pending: 'معلق', handwriting: 'توقيع الطبيب بخط اليد', draw: 'ارسم التوقيع بالأسفل واحفظه في Supabase Storage.', saveSignature: 'حفظ التوقيع', logout: 'خروج', notConfigured: 'لم يتم إعداد Supabase بعد. أضف متغيرات البيئة في Cloudflare Pages.', professional: 'نظام احترافي لإدارة عيادة العلاج الطبيعي',
  },
};

const demoPatients: Patient[] = [
  { id: '1', code: 'PT-0001', name: 'Mona Ahmed', phone: '+20 100 123 4567', diagnosis: 'Low back pain', age: 34, gender: 'Female' },
  { id: '2', code: 'PT-0002', name: 'Karim Samir', phone: '+20 111 222 3333', diagnosis: 'ACL rehabilitation', age: 27, gender: 'Male' },
  { id: '3', code: 'PT-0003', name: 'Laila Hassan', phone: '+20 122 555 9988', diagnosis: 'Cervical spondylosis', age: 45, gender: 'Female' },
];
const demoAppointments: Appointment[] = [
  { id: '1', patient_name: 'Mona Ahmed', therapist_name: 'Dr. Youssef', starts_at: new Date().toISOString(), status: 'confirmed', notes: 'Assessment follow-up' },
  { id: '2', patient_name: 'Karim Samir', therapist_name: 'Dr. Salma', starts_at: new Date(Date.now() + 86400000).toISOString(), status: 'scheduled', notes: 'Strength program' },
];
const demoSessions: Session[] = [
  { id: '1', patient_name: 'Mona Ahmed', therapist_name: 'Dr. Youssef', session_date: new Date().toISOString(), pain_before: 7, pain_after: 4, soap: 'S: pain improved. O: ROM improved. A: good response. P: continue.' },
  { id: '2', patient_name: 'Karim Samir', therapist_name: 'Dr. Salma', session_date: new Date().toISOString(), pain_before: 5, pain_after: 3, soap: 'Closed-chain strengthening and gait retraining.' },
];

function uid() { return crypto.randomUUID ? crypto.randomUUID() : String(Date.now() + Math.random()); }
function money(n: number) { return new Intl.NumberFormat('en-EG', { style: 'currency', currency: 'EGP', maximumFractionDigits: 0 }).format(n); }
function csv(rows: Patient[]) { return ['code,name,phone,diagnosis,age,gender', ...rows.map(p => [p.code,p.name,p.phone,p.diagnosis,p.age,p.gender].map(v => `"${String(v ?? '').replaceAll('"','""')}"`).join(','))].join('\n'); }

function SignaturePad({ lang }: { lang: Lang }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawing = useRef(false);
  const [message, setMessage] = useState('');
  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext('2d')!;
    ctx.lineWidth = 2.5; ctx.lineCap = 'round'; ctx.strokeStyle = '#0f172a';
  }, []);
  const pos = (e: PointerEvent | React.PointerEvent) => {
    const r = canvasRef.current!.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top };
  };
  const start = (e: React.PointerEvent) => { drawing.current = true; const p = pos(e); const ctx = canvasRef.current!.getContext('2d')!; ctx.beginPath(); ctx.moveTo(p.x,p.y); };
  const move = (e: React.PointerEvent) => { if (!drawing.current) return; const p = pos(e); const ctx = canvasRef.current!.getContext('2d')!; ctx.lineTo(p.x,p.y); ctx.stroke(); };
  const stop = () => { drawing.current = false; };
  const clear = () => canvasRef.current!.getContext('2d')!.clearRect(0,0,720,240);
  const save = async () => {
    const dataUrl = canvasRef.current!.toDataURL('image/png');
    if (!supabase) { setMessage('Signature saved locally in demo mode.'); return; }
    const blob = await (await fetch(dataUrl)).blob();
    const path = `doctor-signatures/signature-${Date.now()}.png`;
    const { error } = await supabase.storage.from('clinic-files').upload(path, blob, { contentType: 'image/png', upsert: true });
    setMessage(error ? error.message : `Saved: ${path}`);
  };
  return <section className="card wide"><div className="cardTitle"><FileSignature /> <span>{tr[lang].handwriting}</span></div><p>{tr[lang].draw}</p><canvas ref={canvasRef} width="720" height="240" className="signatureCanvas" onPointerDown={start} onPointerMove={move} onPointerUp={stop} onPointerLeave={stop}/><div className="actions"><button onClick={clear}>{tr[lang].clear}</button><button className="primary" onClick={save}>{tr[lang].saveSignature}</button></div>{message && <p className="notice">{message}</p>}</section>;
}

export default function App() {
  const [lang, setLang] = useState<Lang>('en');
  const [tab, setTab] = useState<Tab>('dashboard');
  const [query, setQuery] = useState('');
  const [patients, setPatients] = useState<Patient[]>(demoPatients);
  const [appointments, setAppointments] = useState<Appointment[]>(demoAppointments);
  const [sessions] = useState<Session[]>(demoSessions);
  const [newPatient, setNewPatient] = useState({ name: '', phone: '', diagnosis: '', age: '', gender: 'Female' });
  const t = tr[lang];
  const filtered = useMemo(() => patients.filter(p => `${p.code} ${p.name} ${p.phone} ${p.diagnosis}`.toLowerCase().includes(query.toLowerCase())), [patients, query]);

  useEffect(() => { document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'; document.documentElement.lang = lang; }, [lang]);
  useEffect(() => { (async () => {
    if (!supabase) return;
    const { data: p } = await supabase.from('patients').select('*').order('created_at', { ascending: false }).limit(100);
    const { data: a } = await supabase.from('appointment_view').select('*').limit(50);
    if (p?.length) setPatients(p as Patient[]);
    if (a?.length) setAppointments(a as Appointment[]);
  })(); }, []);

  const addPatient = async () => {
    if (!newPatient.name.trim()) return;
    const row: Patient = { id: uid(), code: `PT-${String(patients.length + 1).padStart(4,'0')}`, name: newPatient.name, phone: newPatient.phone, diagnosis: newPatient.diagnosis, age: Number(newPatient.age || 0), gender: newPatient.gender };
    setPatients([row, ...patients]); setNewPatient({ name: '', phone: '', diagnosis: '', age: '', gender: 'Female' });
    if (supabase) await supabase.from('patients').insert(row);
  };
  const downloadCsv = () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([csv(filtered)], { type: 'text/csv' })); a.download = 'patients.csv'; a.click(); };

  const nav: [Tab, any, string][] = [['dashboard', LayoutDashboard, t.dashboard], ['patients', Users, t.patients], ['appointments', CalendarDays, t.appointments], ['sessions', Stethoscope, t.sessions], ['billing', WalletCards, t.billing], ['signature', FileSignature, t.signature]];
  return <main className="shell"><aside><div className="brand"><div className="logo"><HeartPulse /></div><div><h1>{clinicName}</h1><p>{t.professional}</p></div></div><nav>{nav.map(([id, Icon, label]) => <button key={id} className={tab===id?'active':''} onClick={() => setTab(id)}><Icon size={18}/>{label}</button>)}</nav><div className="asideFoot"><button onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}><Languages size={18}/>{lang === 'en' ? 'العربية' : 'English'}</button><button><LogOut size={18}/>{t.logout}</button></div></aside><section className="content"><header><div><h2>{nav.find(([id])=>id===tab)?.[2]}</h2><p>{isSupabaseConfigured ? 'Connected to Supabase-ready backend' : t.notConfigured}</p></div><span className="pill">{t.demo}</span></header>{tab==='dashboard' && <div className="grid"><div className="metric"><span>{t.today}</span><strong>{appointments.length}</strong></div><div className="metric"><span>{t.activePatients}</span><strong>{patients.length}</strong></div><div className="metric"><span>{t.revenue}</span><strong>{money(18450)}</strong></div><div className="metric"><span>{t.satisfaction}</span><strong>96%</strong></div><section className="card wide"><h3>{t.upcoming}</h3>{appointments.map(a => <div className="row" key={a.id}><b>{a.patient_name}</b><span>{a.therapist_name}</span><span>{new Date(a.starts_at).toLocaleString()}</span><em>{a.status}</em></div>)}</section></div>}{tab==='patients' && <div className="stack"><section className="card wide"><div className="cardTitle"><Plus/> <span>{t.addPatient}</span></div><div className="form"><input placeholder={t.name} value={newPatient.name} onChange={e=>setNewPatient({...newPatient,name:e.target.value})}/><input placeholder={t.phone} value={newPatient.phone} onChange={e=>setNewPatient({...newPatient,phone:e.target.value})}/><input placeholder={t.diagnosis} value={newPatient.diagnosis} onChange={e=>setNewPatient({...newPatient,diagnosis:e.target.value})}/><input placeholder={t.age} value={newPatient.age} onChange={e=>setNewPatient({...newPatient,age:e.target.value})}/><select value={newPatient.gender} onChange={e=>setNewPatient({...newPatient,gender:e.target.value})}><option>Female</option><option>Male</option></select><button className="primary" onClick={addPatient}>{t.save}</button></div></section><section className="card wide"><div className="toolbar"><label><Search size={18}/><input placeholder={t.search} value={query} onChange={e=>setQuery(e.target.value)}/></label><button onClick={downloadCsv}>{t.exportCsv}</button></div><div className="table">{filtered.map(p => <div className="row" key={p.id}><b>{p.code}</b><span>{p.name}</span><span>{p.phone}</span><span>{p.diagnosis}</span><em>{p.age} / {p.gender}</em></div>)}</div></section></div>}{tab==='appointments' && <section className="card wide"><h3>{t.upcoming}</h3>{appointments.map(a => <div className="row" key={a.id}><b>{a.patient_name}</b><span>{t.therapist}: {a.therapist_name}</span><span>{new Date(a.starts_at).toLocaleString()}</span><em>{t.status}: {a.status}</em></div>)}</section>}{tab==='sessions' && <section className="card wide"><h3>{t.soap}</h3>{sessions.map(s => <div className="session" key={s.id}><div className="row"><b>{s.patient_name}</b><span>{s.therapist_name}</span><em>{t.beforeAfter}: {s.pain_before}/{s.pain_after}</em></div><p>{s.soap}</p></div>)}</section>}{tab==='billing' && <div className="grid"><div className="metric"><span>{t.invoices}</span><strong>42</strong></div><div className="metric"><span>{t.paid}</span><strong>{money(37800)}</strong></div><div className="metric"><span>{t.pending}</span><strong>{money(6900)}</strong></div><section className="card wide"><h3>Packages</h3><div className="row"><b>12 sessions package</b><span>Mona Ahmed</span><span>8 remaining</span><em>{money(3600)}</em></div><div className="row"><b>Post-op rehab</b><span>Karim Samir</span><span>5 remaining</span><em>{money(5000)}</em></div></section></div>}{tab==='signature' && <SignaturePad lang={lang}/>}</section></main>;
}
