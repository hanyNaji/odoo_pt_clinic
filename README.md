# Wiqaya Physiotherapy Clinic for Odoo 19

`pt_clinic` is an Arabic-first Odoo 19 module for physiotherapy clinic operations. It combines reception, therapist, billing, and reporting workflows in one application, with terminology and printouts adapted to a real outpatient physiotherapy setting.

## What it covers

- patient registration and medical profile management
- appointment scheduling and attendance tracking
- physiotherapy assessment sheets and care plans
- session documentation and therapy follow-up sheets
- packages, billing, contracts, and clinic reporting
- Arabic UI with the English medical terms commonly used in practice

## Repository layout

```text
addons/pt_clinic   Main Odoo module
docs/              Minimal project documentation
tests/             Test coverage for clinic logic
tools/             Utility and smoke-test scripts
```

## Local development

This repository contains the custom module, not a full Odoo distribution. Run it with an Odoo 19 source checkout and update [config/odoo.conf](/abs/path/C:/Users/hanyt/PycharmProjects/PT_CLINIC/config/odoo.conf:1) for your machine.

Typical Windows command:

```powershell
Set-Location C:\path\to\odoo-19.0
C:\path\to\PT_CLINIC\.venv\Scripts\python.exe -m odoo -c C:\path\to\PT_CLINIC\config\odoo.conf
```

Then open:

```text
http://127.0.0.1:8069/web/login?db=wiqaya19
```

## Module highlights

- Arabic-first patient, appointment, treatment, billing, and report menus
- physiotherapy-specific assessment and care plan records
- printable therapy sheets matching common paper-clinic workflows
- role-based access for manager, therapist, assistant, and billing staff
- Wiqaya clinic branding and UI customization

## Quality checks

```powershell
python tools\smoke_test.py
python -m compileall addons\pt_clinic tests tools
```

## Documentation

- [Deployment Guide](docs/deployment.md)

## License

This project is released under `LGPL-3`, matching the module manifest.
