# Deployment Guide

This repository ships the custom Odoo addon only. Production deployment means running Odoo 19 with `addons/pt_clinic` added to `addons_path`.

## Requirements

- Odoo 19 source or package installation
- PostgreSQL 15 or newer
- Python environment matching the Odoo 19 requirements
- Linux VM for production, preferably Ubuntu LTS
- Reverse proxy with HTTPS for public access
- Daily PostgreSQL + filestore backups

## Local startup

1. Clone this repository.
2. Prepare an Odoo 19 environment.
3. Add this repository's `addons` directory to `addons_path`.
4. Start Odoo with a config based on `config/odoo.conf`.
5. Install or upgrade the `pt_clinic` module from the Apps menu.

Typical command pattern:

```powershell
Set-Location C:\path\to\odoo-19.0
C:\path\to\PT_CLINIC\.venv\Scripts\python.exe -m odoo -c C:\path\to\PT_CLINIC\config\odoo.conf
```

## Production baseline

Use these settings before exposing the system online:

```ini
proxy_mode = True
list_db = False
without_demo = True
dbfilter = ^wiqaya19$
workers = 2
max_cron_threads = 1
limit_memory_soft = 1073741824
limit_memory_hard = 1342177280
limit_time_cpu = 120
limit_time_real = 240
```

Notes:

- Do not run Odoo publicly on raw `:8069`.
- Use a dedicated PostgreSQL user, not `postgres`.
- Put Odoo behind Nginx or Caddy.
- Enable gzip/brotli at the reverse proxy.
- Restart Odoo after addon updates, then upgrade the `pt_clinic` module.
- Clear Odoo assets after major CSS/XML changes.

## Recommended hosting

For a low-cost self-managed deployment, use a small Linux VM and host Odoo behind a reverse proxy. This project includes custom modules, so it is intended for self-hosted Odoo or Odoo.sh rather than Odoo Online.

Recommended minimum for real clinic use:

- 2 vCPU
- 2-4 GB RAM
- SSD storage
- PostgreSQL on the same VM for small deployments
- Automated daily backup copied outside the VM

Oracle Cloud Always Free can work for testing or a very small clinic, but a paid small VM is safer when users depend on it daily.

## Cloudflare usage

Cloudflare is useful in front of Odoo, but it does not replace the Odoo server.

Use Cloudflare for:

- DNS
- HTTPS edge certificate
- WAF/basic protection
- Bot protection/rate limiting
- Static asset caching where safe
- Hiding the origin IP when the origin firewall only allows Cloudflare IP ranges

Do not use Cloudflare as:

- The Odoo application host
- The PostgreSQL host
- A replacement for workers/gevent/proper reverse proxy

Recommended setup:

```text
User browser / mobile
        ↓
Cloudflare DNS + SSL + WAF
        ↓
Nginx or Caddy on VM
        ↓
Odoo 19 workers on 127.0.0.1:8069
        ↓
PostgreSQL
```

Cloudflare DNS should point to the VM public IP. In Cloudflare SSL/TLS, use **Full (strict)** after installing a valid origin certificate or Let's Encrypt certificate on the VM.

## Odoo mobile app

The Odoo mobile app can be used with a self-hosted Odoo URL as long as the server is reachable over HTTPS and the database/login are valid. For this custom clinic module, test every screen because custom backend views may need mobile CSS adjustments. The mobile browser/PWA-style flow should also be supported because reception and therapists may use normal phone browsers.

## Performance checklist

1. Turn on `proxy_mode = True` when behind Nginx/Caddy/Cloudflare.
2. Use workers in production instead of single-process dev mode.
3. Keep Odoo, PostgreSQL, and the custom addon on SSD storage.
4. Avoid installing unused Odoo apps.
5. Add indexes only after measuring slow queries.
6. Compress static assets at the reverse proxy.
7. Keep database backups and filestore backups together.
8. Review Odoo logs for slow requests and traceback loops.
9. Upgrade the custom module after pulling new code:

```bash
sudo systemctl restart odoo
/path/to/odoo-bin -c /etc/odoo/odoo.conf -d wiqaya19 -u pt_clinic --stop-after-init
sudo systemctl restart odoo
```

## Validation

Run the project checks after deployment changes:

```powershell
python tools\smoke_test.py
python -m compileall addons\pt_clinic tests tools
```

If module changes are not visible in the browser, upgrade `pt_clinic`, restart Odoo, and clear cached Odoo assets from developer mode.
