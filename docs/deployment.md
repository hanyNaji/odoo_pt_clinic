# Deployment Guide

This repository ships the custom addon only. Production deployment means running Odoo 19 with `addons/pt_clinic` added to `addons_path`.

## Requirements

- Odoo 19 source or package installation
- PostgreSQL 15 or newer
- Python environment matching the Odoo 19 requirements
- Reverse proxy with HTTPS for public access

## Local startup

1. Clone this repository.
2. Prepare an Odoo 19 environment.
3. Add this repository's `addons` directory to `addons_path`.
4. Start Odoo with a config based on [config/odoo.conf](/abs/path/C:/Users/hanyt/PycharmProjects/PT_CLINIC/config/odoo.conf:1).
5. Install or upgrade the `pt_clinic` module from the Apps menu.

Typical command pattern:

```powershell
Set-Location C:\path\to\odoo-19.0
C:\path\to\PT_CLINIC\.venv\Scripts\python.exe -m odoo -c C:\path\to\PT_CLINIC\config\odoo.conf
```

## Production baseline

Use these settings before exposing the system online:

- `proxy_mode = True`
- `list_db = False`
- `without_demo = True`
- a fixed `dbfilter` for the target database
- daily PostgreSQL backups
- HTTPS termination at Nginx or Caddy

## Recommended hosting

For a low-cost or free self-managed deployment, use a small Linux VM and host Odoo behind a reverse proxy. This project includes custom modules, so it is intended for self-hosted Odoo or Odoo.sh rather than Odoo Online.

## Validation

Run the project checks after deployment changes:

```powershell
python tools\smoke_test.py
python -m compileall addons\pt_clinic tests tools
```

If module changes are not visible in the browser, upgrade `pt_clinic` and clear cached Odoo assets.
