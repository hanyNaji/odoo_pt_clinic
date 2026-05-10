create extension if not exists pgcrypto;

create table if not exists public.clinic_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  full_name text not null,
  role text not null default 'therapist' check (role in ('admin','manager','therapist','reception','billing')),
  created_at timestamptz default now()
);

create table if not exists public.patients (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null,
  phone text,
  whatsapp text,
  email text,
  national_id text unique,
  age int,
  gender text,
  diagnosis text,
  medical_history text,
  allergy_notes text,
  created_at timestamptz default now()
);

create table if not exists public.appointments (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid references public.patients(id) on delete cascade,
  therapist_id uuid references public.clinic_profiles(id) on delete set null,
  starts_at timestamptz not null,
  ends_at timestamptz,
  status text not null default 'scheduled' check (status in ('scheduled','confirmed','arrived','done','cancelled','no_show')),
  notes text,
  created_at timestamptz default now()
);

create table if not exists public.assessments (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid references public.patients(id) on delete cascade,
  therapist_id uuid references public.clinic_profiles(id) on delete set null,
  assessment_date date default current_date,
  chief_complaints text,
  diagnosis text not null,
  pain_score int check (pain_score between 0 and 10),
  red_flags text,
  functional_limitations text,
  goals text,
  recommendations text,
  doctor_signature_path text,
  created_at timestamptz default now()
);

create table if not exists public.treatment_plans (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid references public.patients(id) on delete cascade,
  therapist_id uuid references public.clinic_profiles(id) on delete set null,
  plan_date date default current_date,
  status text default 'draft' check (status in ('draft','active','completed')),
  findings text,
  goals text,
  modalities text,
  home_exercise_plan boolean default false,
  created_at timestamptz default now()
);

create table if not exists public.sessions (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid references public.patients(id) on delete cascade,
  therapist_id uuid references public.clinic_profiles(id) on delete set null,
  appointment_id uuid references public.appointments(id) on delete set null,
  treatment_plan_id uuid references public.treatment_plans(id) on delete set null,
  session_date timestamptz default now(),
  duration_minutes int default 45,
  pain_before int check (pain_before between 0 and 10),
  pain_after int check (pain_after between 0 and 10),
  subjective_notes text,
  objective_notes text,
  assessment_notes text,
  plan_notes text,
  doctor_signature_path text,
  created_at timestamptz default now()
);

create table if not exists public.invoices (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid references public.patients(id) on delete cascade,
  invoice_number text unique not null,
  amount numeric(12,2) not null default 0,
  paid_amount numeric(12,2) not null default 0,
  status text default 'draft' check (status in ('draft','issued','paid','partial','cancelled')),
  issued_on date default current_date,
  created_at timestamptz default now()
);

create table if not exists public.treatment_packages (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid references public.patients(id) on delete cascade,
  name text not null,
  total_sessions int not null,
  used_sessions int not null default 0,
  price numeric(12,2) not null default 0,
  start_date date default current_date,
  end_date date,
  created_at timestamptz default now()
);

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_id uuid references auth.users(id) on delete set null,
  action text not null,
  entity text not null,
  entity_id uuid,
  created_at timestamptz default now()
);

create or replace view public.appointment_view as
select a.id, p.name as patient_name, coalesce(cp.full_name,'Unassigned') as therapist_name, a.starts_at, a.status, a.notes
from public.appointments a
left join public.patients p on p.id = a.patient_id
left join public.clinic_profiles cp on cp.id = a.therapist_id
order by a.starts_at desc;

alter table public.clinic_profiles enable row level security;
alter table public.patients enable row level security;
alter table public.appointments enable row level security;
alter table public.assessments enable row level security;
alter table public.treatment_plans enable row level security;
alter table public.sessions enable row level security;
alter table public.invoices enable row level security;
alter table public.treatment_packages enable row level security;
alter table public.audit_logs enable row level security;

create or replace function public.current_role() returns text language sql stable as $$
  select role from public.clinic_profiles where user_id = auth.uid() limit 1
$$;

create policy "profiles read authenticated" on public.clinic_profiles for select to authenticated using (true);
create policy "profiles self insert" on public.clinic_profiles for insert to authenticated with check (user_id = auth.uid());
create policy "profiles admin update" on public.clinic_profiles for update to authenticated using (public.current_role() in ('admin','manager'));

create policy "patients read" on public.patients for select to authenticated using (true);
create policy "patients write staff" on public.patients for all to authenticated using (public.current_role() in ('admin','manager','therapist','reception')) with check (public.current_role() in ('admin','manager','therapist','reception'));

create policy "appointments read" on public.appointments for select to authenticated using (true);
create policy "appointments write staff" on public.appointments for all to authenticated using (public.current_role() in ('admin','manager','therapist','reception')) with check (public.current_role() in ('admin','manager','therapist','reception'));

create policy "clinical read" on public.assessments for select to authenticated using (true);
create policy "clinical write therapists" on public.assessments for all to authenticated using (public.current_role() in ('admin','manager','therapist')) with check (public.current_role() in ('admin','manager','therapist'));
create policy "plans read" on public.treatment_plans for select to authenticated using (true);
create policy "plans write therapists" on public.treatment_plans for all to authenticated using (public.current_role() in ('admin','manager','therapist')) with check (public.current_role() in ('admin','manager','therapist'));
create policy "sessions read" on public.sessions for select to authenticated using (true);
create policy "sessions write therapists" on public.sessions for all to authenticated using (public.current_role() in ('admin','manager','therapist')) with check (public.current_role() in ('admin','manager','therapist'));

create policy "billing read" on public.invoices for select to authenticated using (public.current_role() in ('admin','manager','billing'));
create policy "billing write" on public.invoices for all to authenticated using (public.current_role() in ('admin','manager','billing')) with check (public.current_role() in ('admin','manager','billing'));
create policy "packages read" on public.treatment_packages for select to authenticated using (true);
create policy "packages write" on public.treatment_packages for all to authenticated using (public.current_role() in ('admin','manager','billing','reception')) with check (public.current_role() in ('admin','manager','billing','reception'));
create policy "audit admin read" on public.audit_logs for select to authenticated using (public.current_role() in ('admin','manager'));

insert into storage.buckets (id, name, public) values ('clinic-files','clinic-files',false) on conflict (id) do nothing;
create policy "clinic files read" on storage.objects for select to authenticated using (bucket_id = 'clinic-files');
create policy "clinic files upload" on storage.objects for insert to authenticated with check (bucket_id = 'clinic-files');
