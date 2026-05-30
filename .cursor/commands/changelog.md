Generá el borrador de changelog de la última semana para usuarios del producto Polko.

**Pasos:**

1. Desde la raíz del proyecto, corré `venv/bin/python fetch_mrs.py` para obtener los MRs mergeados en JSON.
   - Si el usuario pasó `--since YYYY-MM-DD`, agregá ese flag al comando: `venv/bin/python fetch_mrs.py --since YYYY-MM-DD`

2. Pre-filtrá sin evaluar: descartá los MRs cuyo título empiece con alguno de estos prefijos:
   `chore:`, `ci:`, `test:`, `docs:`, `build:`, `bump:`, `deps:`
   O cuyo título empiece con `Merge branch ` o `Revert "`

3. Con los MRs restantes, evaluá cuáles afectan directamente la experiencia del usuario final
   (no infra interna, refactors de código, o cambios de configuración sin impacto visible).
   Usá el título + descripción del MR para juzgar. Ante la duda, incluilo.

4. Para los user-facing, escribí entradas en español claro, sin jerga técnica.
   Destacá el beneficio para el usuario, no la implementación.
   Agrupá en (omití las secciones vacías):
   - ✨ Novedades
   - 🔧 Mejoras
   - 🐛 Bugs resueltos

5. Escribí el resultado en `changelogs/YYYY-WW.md` (semana ISO actual, ej: `changelogs/2026-22.md`).

   Formato del archivo:
   ```
   # Changelog — Semana WW · YYYY

   > Borrador generado el YYYY-MM-DD. Revisá el tono antes de publicar.

   ## nombre-repo

   ### ✨ Novedades
   ...

   ---
   *MRs analizados: X · Incluidos: Y · Descartados: Z*
   ```

6. Imprimí el path del archivo generado.
