# Deployment Guide

## 1. Supabase

Create a Supabase project, then run:

```sql
-- Open Supabase SQL Editor and run:
-- supabase/001_schema.sql
```

Create your first auth user, then promote that user:

```sql
insert into public.clinic_profiles (user_id, full_name, role)
values ('PASTE_AUTH_USER_ID', 'Clinic Admin', 'admin');
```

Do not put Supabase service-role keys in the frontend or Cloudflare Pages public variables. Use only the anon key with RLS.

## 2. Cloudflare Pages

Connect GitHub repository:

- Repository: `hanyNaji/odoo_pt_clinic`
- Branch: `wiqaya-cloudflare-pt-clinic`
- Root directory: `cloudflare-pt-clinic`
- Build command: `npm run build`
- Output directory: `dist`

Environment variables:

```text
VITE_SUPABASE_URL=https://PROJECT_REF.supabase.co
VITE_SUPABASE_ANON_KEY=PASTE_PUBLIC_ANON_KEY_HERE
VITE_CLINIC_NAME=Wiqaya PT Clinic
```

## 3. Local test

```bash
cd cloudflare-pt-clinic
npm install
npm run build
npm run dev
```

## 4. First production checklist

- Confirm RLS is enabled on all public tables.
- Create admin profile after first signup.
- Test patient creation.
- Test appointment listing.
- Test signature upload to `clinic-files` bucket.
- Add a custom domain in Cloudflare Pages.
