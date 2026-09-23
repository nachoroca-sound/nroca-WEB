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
- `previewVideo` apunta a `assets/video/<categoria>/<slug>.mp4`.

## Animaciones

Toda animación debe respetar `prefers-reduced-motion: reduce`.

## Skills prohibidas

No usar ni instalar `apple-design`, `pick-ui-library` ni `find-animation-opportunities`.

## Commits

Mínimos y solo cuando se pidan explícitamente. Nunca commitear por iniciativa propia.

## Trabajo interactivo

Antes de cualquier acción destructiva —borrar o mover ficheros, borrar entradas
de JSON, borrar CSS— enseñar qué se va a hacer y esperar OK.
