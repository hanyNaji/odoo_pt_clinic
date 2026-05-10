# Wiqaya PT Clinic - Cloudflare + Supabase

Standalone physiotherapy clinic management system designed for Cloudflare Pages and Supabase.

## Modules

- Dashboard and daily KPIs
- Patient registry
- Appointment tracking
- SOAP session documentation
- Billing and treatment packages foundation
- Doctor handwritten signature pad
- Supabase Storage upload for signatures
- English / Arabic UI switch
- Cloudflare Pages SPA routing and security headers
- Supabase SQL schema with Row Level Security

## Local run

```bash
npm install
cp .env.example .env
npm run dev
```

Fill `.env` with:

```bash
VITE_SUPABASE_URL=https://PROJECT_REF.supabase.co
VITE_SUPABASE_ANON_KEY=PASTE_PUBLIC_ANON_KEY_HERE
VITE_CLINIC_NAME=Wiqaya PT Clinic
```

## Supabase setup

1. Create a Supabase project.
2. Open SQL Editor.
3. Run `supabase/001_schema.sql`.
4. Create your first user from Supabase Auth.
5. Promote the first user to admin:

```sql
insert into public.clinic_profiles (user_id, full_name, role)
values ('USER_UUID_FROM_AUTH_USERS', 'Clinic Admin', 'admin');
```

## Cloudflare Pages

- Framework preset: Vite
- Build command: `npm run build`
- Build output directory: `dist`
- Root directory: `cloudflare-pt-clinic`

Add environment variables in Cloudflare Pages settings:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_CLINIC_NAME`

## Notes

This branch is intentionally standalone and does not require Odoo. It was designed from the existing PT clinic workflow: patients, appointments, assessments, care plans, therapy sessions, packages, billing, reports, staff roles, and handwritten doctor signatures.
