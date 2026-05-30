# changelog-agent

Agente de IA que convierte los merge requests de GitLab en un borrador de changelog en lenguaje llano, pensado para usuarios del producto — no para desarrolladores.

## El problema que resuelve

Publicar changelogs para usuarios requiere criterio: no todo lo que se mergea les importa, y lo que sí les importa hay que contarlo diferente. Transformar commits técnicos en lenguaje accesible es un trabajo que nadie hace porque lleva tiempo y requiere contexto.

Este agente hace el trabajo pesado: busca los MRs mergeados en la última semana, descarta los que son refactors, fixes internos o cambios de infraestructura, y con los que quedan genera un borrador de changelog listo para revisar. El resultado no se publica directo — lo revisás, ajustás el tono donde hace falta, y lo mandás.

## Cómo funciona

```
GitLab API → fetch_mrs.py → JSON → Claude/Cursor/Codex → changelogs/YYYY-WW.md
```

1. **`fetch_mrs.py`** consulta la API de GitLab y devuelve en JSON los MRs mergeados en el período indicado.
2. El agente de IA pre-filtra por prefijo de título (`chore:`, `ci:`, `test:`, etc.) descartando lo que nunca es relevante para usuarios.
3. Con los MRs restantes, el modelo juzga cuáles tienen impacto visible para el usuario y genera entradas de changelog en español, sin jerga técnica.
4. El borrador se guarda en `changelogs/YYYY-WW.md` (por número de semana ISO) listo para editar y publicar.

### Por qué un script Python y no una conexión MCP

La alternativa obvia sería conectar el agente directamente a GitLab vía MCP. El problema es que cada llamada HTTP que hace el modelo consume tokens del contexto: headers, respuestas intermedias, paginación, manejo de errores. Con 50-100 MRs por semana y múltiples repos, eso se acumula rápido en tokens que no aportan nada al resultado.

`fetch_mrs.py` resuelve esto fuera del contexto del modelo: hace todas las llamadas HTTP, pagina, filtra y devuelve un JSON limpio y compacto. El modelo recibe solo los datos que necesita para razonar — títulos, descripciones, branches — sin el ruido de la comunicación con la API.

## Requisitos

- Python 3.8+
- Token de GitLab con acceso `read_api` a los repositorios
- Claude Code, Cursor o Codex app

## Instalación

```bash
git clone https://github.com/lucas-cassina/changelog-agent.git
cd changelog-agent
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Editá `.env` y completá tu token de GitLab:

```
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
```

## Configuración

Editá `config.py` para agregar tus repositorios:

```python
REPOS = [
    {"id": "123456", "name": "mi-frontend"},
    {"id": "789012", "name": "mi-backend"},
]

DAYS_LOOKBACK = 7          # días hacia atrás por defecto
GITLAB_BASE_URL = "https://gitlab.com"  # o tu instancia propia
```

El `id` de cada proyecto lo encontrás en **GitLab → Settings → General** de cada repo, o en la URL del proyecto.

## Uso

Abrí el proyecto en tu editor con IA y ejecutá el comando:

### Claude Code

```
/changelog
```

### Cursor

```
/changelog
```

### Codex app

Pedile al agente: *"generá el changelog de esta semana"* — detecta el skill automáticamente.

---

Para un rango de fechas personalizado, pasá `--since`:

```
/changelog --since 2026-05-01
```

El borrador se genera en `changelogs/2026-22.md` (semana ISO actual).

## Estructura del proyecto

```
changelog-agent/
├── .claude/
│   └── commands/
│       └── changelog.md       # Slash command para Claude Code
├── .cursor/
│   └── commands/
│       └── changelog.md       # Slash command para Cursor
├── skills/
│   └── changelog/
│       └── SKILL.md           # Skill para Codex app
├── AGENTS.md                  # Instrucciones generales para Codex
├── fetch_mrs.py               # Script de fetch a GitLab API
├── config.py                  # Configuración de repos y parámetros
├── requirements.txt
├── .env.example
└── changelogs/                # Borradores generados (ignorados por git)
```

## Qué filtra y qué incluye

**Descartado automáticamente** (por prefijo de título):
- `chore:` — mantenimiento interno
- `ci:` — pipelines y automatización
- `test:` — tests
- `docs:` — documentación interna
- `build:` — sistema de build
- `bump:` / `deps:` — actualizaciones de dependencias
- `Merge branch ...` — commits de merge automáticos
- `` Revert "..." `` — reverts

**Evaluado por el modelo** (incluido si tiene impacto para el usuario):
- `feat:` — nuevas funcionalidades
- `fix:` — bugs corregidos
- `hotfix:` — correcciones urgentes
- `perf:` — mejoras de rendimiento visibles
- Cualquier MR sin prefijo convencional

El modelo juzga cada caso usando el título y la descripción del MR. Ante la duda, incluye.

## Ejemplo de output

```markdown
# Changelog — Semana 22 · 2026

> Borrador generado el 2026-05-30. Revisá el tono antes de publicar.

## mi-frontend

### ✨ Novedades
- **Acciones sugeridas en errores de emisión**: Cuando ocurre un error conocido
  al emitir una póliza, el sistema ahora muestra pasos concretos para resolverlo.

### 🐛 Bugs resueltos
- Se corrigió la barra de descuento adicional que en ciertos casos no aplicaba correctamente.
- El descuento extra ya no puede superar el límite permitido en coberturas fuera de pauta.

---
*MRs analizados: 14 · Incluidos: 3 · Descartados: 11*
```

## Obtener el token de GitLab

1. GitLab → **User Settings → Access Tokens**
2. Nombre: `changelog-agent`
3. Scopes: `read_api`
4. Copiá el token generado en tu `.env`

Para repositorios en una instancia propia de GitLab, actualizá `GITLAB_BASE_URL` en `config.py`.
