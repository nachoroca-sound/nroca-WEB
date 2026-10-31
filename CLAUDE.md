# nroca.com — reglas del proyecto

Sitio estático en HTML/CSS/JS vanilla. `build.py` genera todo el HTML desde
`data/*.json` + `templates/*.html.tmpl`. Se despliega en Netlify desde la raíz
del repo, sin build step en el servidor.

## Nunca editar ficheros generados

Los `.html` de la raíz, todo `projects/*.html` y `sitemap.xml` son **generados**.
Cualquier cambio en ellos se pierde en el siguiente build.

Todo cambio va en uno de estos cuatro sitios, y después se corre `python3 build.py`:

- `data/content.json` — textos del sitio (nav, hero, about, contact, footer, meta SEO)
- `data/projects.json` — proyectos, su categoría y su orden
- `templates/*.html.tmpl` — estructura HTML
- `build.py` — lógica de generación

Las **únicas** páginas escritas a mano son `privacy.html` y `404.html`.

## Estructura de datos

`data/projects.json` tiene una clave top-level por categoría: `videogames`,
`film`, `commercial`, `demos`. El orden dentro de cada array manda: define el
orden del grid y el ciclo de prev/next de las páginas de proyecto.

- `pending: true` marca un proyecto a la espera de contenido. Sale en el grid y
  tiene página, pero la página lleva `noindex` y queda fuera del sitemap.
- Sin `vimeoId` no se emite ningún iframe (nunca un reproductor roto).
- `previewVideo` apunta a `assets/video/<carpeta>/<slug>.mp4`. La carpeta
  coincide con la categoría salvo en `videogames`, que usa la carpeta `games`
  (`assets/video/games/…`, no `videogames`).
- Al cambiar un `slug`, añadir en `netlify.toml` el redirect 301 del slug viejo
  al nuevo (`/projects/<viejo>.html` → `/projects/<nuevo>.html`). Los redirects
  existentes están ligados a slugs concretos y no se actualizan solos.

## Verificación local

Tras `python3 build.py`, servir la raíz con un servidor estático simple (probado:
las rutas relativas del build, `root_prefix`, resuelven bien):

    python3 -m http.server 8000 --bind 127.0.0.1   # → http://127.0.0.1:8000/

- `http.server` NO aplica `_headers` (CSP) ni los redirects de `netlify.toml`:
  esas dos cosas no se pueden comprobar en local.
- Anchos: escritorio y móvil (hay nav móvil propio, `MOBILE_NAV_PAGES` en
  `build.py`; probar las páginas de esa lista y las de proyecto con prev/next).
- Consola: `_headers` fija una CSP que bloquea todo recurso externo salvo
  `'self'` y Vimeo (y los frames de Google Maps). Un recurso nuevo falla en
  silencio en producción aunque en local cargue bien.
- Tras el build, `git diff`: solo deben cambiar los ficheros esperados.

## Skill web-vanilla

No aplica estructuralmente a este proyecto. Aquí la fuente de datos es
`data/*.json` y el build genera el HTML en la raíz del repo, no en `dist/`. Si
se invoca esa skill, no debe empujar a crear `contenido/` ni `dist/`.

## Animaciones

Toda animación debe respetar `prefers-reduced-motion: reduce`.

## Skills prohibidas

No usar ni instalar `apple-design`, `pick-ui-library` ni `find-animation-opportunities`.

## Commits

Mínimos y solo cuando se pidan explícitamente. Nunca commitear por iniciativa propia.

## Trabajo interactivo

Antes de cualquier acción destructiva —borrar o mover ficheros, borrar entradas
de JSON, borrar CSS— enseñar qué se va a hacer y esperar OK.
