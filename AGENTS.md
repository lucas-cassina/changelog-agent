# Changelog Agent

Genera el borrador de changelog semanal de GitLab para usuarios finales del producto.

Para ejecutarlo, usá el skill `changelog` definido en `skills/changelog/SKILL.md`.

## Configuración

- Repos y project IDs: `config.py`
- Token GitLab: `.env` → `GITLAB_TOKEN`
- Dependencias: `pip install -r requirements.txt` (o usar `venv/bin/python`)
