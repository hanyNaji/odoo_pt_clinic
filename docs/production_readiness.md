# Wiqaya Odoo Production Readiness Notes

This checklist records the decisions that make the clinic module suitable for real daily use rather than demo data entry.

## Mobile-first operating model

- Keep reception and therapist entry points on kanban/calendar/list before forms so the Odoo mobile app opens touch-friendly cards first.
- Keep header actions short and state-aware: therapists should only see actions that are useful for the current appointment state.
- Put the highest-frequency fields first on forms: patient, therapist, appointment time, branch, room, and care notes.
- Prefer standard Odoo widgets and responsive backend components instead of custom navigation that can break after upgrades.

## Performance defaults

- Index fields used in daily domains, record rules, overlap checks, and billing selections: company, patient, branch, therapist, dates, state/status, active, billed, and searchable identifiers.
- Avoid per-record dashboard counting. Compute dashboard counters once per company/request and assign the same values to all dashboard rows.
- Use timezone-aware date boundaries for “today” dashboards and appointment filters so clinics outside UTC see correct daily totals.

## Compatibility and upgrades

- Keep custom CSS scoped under `o_pt_clinic_*` classes and Odoo-native views so the module remains compatible with web and mobile clients.
- Avoid replacing Odoo menus, form rendering, or mobile navigation with custom JavaScript unless there is a proven business requirement.
- Run smoke tests, Python compilation, and XML parsing before every delivery.

## Go-live checks

1. Update the module on a staging copy with production-like data volume.
2. Test appointment creation, overlap validation, reminders, session creation, package usage, and invoice creation from desktop and mobile.
3. Verify access rules with manager, therapist, assistant, and billing users.
4. Confirm Arabic language, company logo, branch defaults, sequences, and reports after database restore.
5. Review PostgreSQL indexes after module upgrade and run `VACUUM ANALYZE` during a maintenance window if a large historical import was performed.
