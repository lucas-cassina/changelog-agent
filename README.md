# changelog-agent

Agente de IA que convierte los merge requests de GitLab en un borrador de changelog en lenguaje llano, pensado para los equipos que operan, comunican y comercializan el producto — no para desarrolladores.

## El problema que resuelve

El equipo de desarrollo habla en commits. El resto de la empresa, no.

Marketing necesita saber qué cambió para actualizar los materiales. Ventas necesita saber qué mejoró para tener conversaciones honestas con clientes. Operaciones necesita saber qué se arregló. Comunicación necesita saber qué vale la pena contar. Y lo que llega es `refactor(core): extraer lógica de MapperFactory a capa de servicios`.

Este agente hace el trabajo de traducción: busca los MRs mergeados en la última semana, descarta los que son cambios internos irrelevantes para el resto del equipo, y con los que quedan genera un borrador de changelog en lenguaje que puede leer cualquier persona de la empresa. El resultado no se distribuye directo — lo revisás, ajustás el tono donde hace falta, y lo mandás.

## Cómo funciona

```
GitLab API → fetch_mrs.py → JSON → Claude/Cursor/Codex → changelogs/YYYY-WW.md
```

1. **`fetch_mrs.py`** consulta la API de GitLab y devuelve en JSON los MRs mergeados en el período indicado.
2. El agente de IA pre-filtra por prefijo de título (`chore:`, `ci:`, `test:`, etc.) descartando lo que nunca es relevante fuera del equipo de desarrollo.
3. Con los MRs restantes, el modelo juzga cuáles tienen impacto visible para el resto de la empresa y genera entradas en lenguaje llano, sin jerga técnica.
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

**Evaluado por el modelo** (incluido si tiene impacto fuera del equipo de desarrollo):
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
- **Sugerencias contextuales en el flujo de carga**: El sistema ahora muestra
  opciones relevantes según el paso en el que se encuentra el usuario,
  reduciendo la necesidad de buscar manualmente.

### 🔧 Mejoras
- La pantalla de configuración avanzada carga más rápido en conexiones lentas.

### 🐛 Bugs resueltos
- Se corrigió un problema en el panel de filtros que en ciertos casos
  no guardaba la selección correctamente.

---
*MRs analizados: 14 · Incluidos: 3 · Descartados: 11*
```

## Obtener el token de GitLab

1. GitLab → **User Settings → Access Tokens**
2. Nombre: `changelog-agent`
3. Scopes: `read_api`
4. Copiá el token generado en tu `.env`

Para repositorios en una instancia propia de GitLab, actualizá `GITLAB_BASE_URL` en `config.py`.
