#!/usr/bin/env python3
"""
Generates all static HTML pages from data/content.json + data/projects.json + templates/*.

Pages generated:
  index.html       — home (hero + all-projects grid)
  games.html       — video games grid
  film.html        — film grid
  commercial.html  — advertising/commercial grid
  about.html       — about + manifesto
  contact.html     — let's talk / direct contact
  demos.html       — hidden demos (noindex)
  projects/<id>.html — project detail pages

Run after editing data/ or templates/:
    python3 build.py
"""

import html
import json
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "https://nroca.com/"
LANGS = ["en"]

with open(ROOT_DIR / "data" / "content.json", encoding="utf-8") as f:
    content = json.load(f)

with open(ROOT_DIR / "data" / "projects.json", encoding="utf-8") as f:
    projects = json.load(f)

home_template    = (ROOT_DIR / "templates" / "home.html.tmpl").read_text(encoding="utf-8")
grid_template    = (ROOT_DIR / "templates" / "grid.html.tmpl").read_text(encoding="utf-8")
about_template   = (ROOT_DIR / "templates" / "about.html.tmpl").read_text(encoding="utf-8")
contact_template = (ROOT_DIR / "templates" / "contact.html.tmpl").read_text(encoding="utf-8")
demos_template   = (ROOT_DIR / "templates" / "demos.html.tmpl").read_text(encoding="utf-8")
project_template = (ROOT_DIR / "templates" / "project.html.tmpl").read_text(encoding="utf-8")


def render(template, mapping):
    def replace(match):
        key = match.group(1)
        if key not in mapping:
            raise KeyError(f"Missing placeholder: {{{{{key}}}}}")
        return str(mapping[key])
    return re.sub(r"\{\{(\w+)\}\}", replace, template)


def t(lang, key):
    return content[lang][key]


def project_url(item, lang):
    """Relative path from site root to a project's page."""
    return f"projects/{item['slug']}.html" if lang == "en" else f"projects/es/{item['slug']}.html"


def lang_url(lang, root_prefix, path):
    """Constructs a URL to a same-language page from any depth."""
    if lang == "en":
        return root_prefix + path
    return root_prefix + "es/" + path


MOBILE_NAV_PAGES = ["games", "film", "commercial", "about", "contact"]


def common_mapping(lang, root_prefix, canonical, hreflang_en,
                   meta_title, meta_description, og_description, active_page=None):
    """Tokens shared by all page templates."""
    mapping = {
        "LANG": lang,
        "META_TITLE": meta_title,
        "META_DESCRIPTION": meta_description,
        "OG_DESCRIPTION": og_description,
        "OG_IMAGE": BASE_URL + "assets/img/og-image.png",
        "CANONICAL_URL": canonical,
        "HREFLANG_EN": hreflang_en,
        "ROOT": root_prefix,
        # Nav labels
        "NAV_HOME":      t(lang, "nav.home"),
        "NAV_GAMES":      t(lang, "nav.games"),
        "NAV_FILM":       t(lang, "nav.film"),
        "NAV_COMMERCIAL": t(lang, "nav.commercial"),
        "NAV_ABOUT":     t(lang, "nav.about"),
        "NAV_LETS_TALK": t(lang, "nav.letsTalk"),
        # Nav URLs
        "HOME_URL":       lang_url(lang, root_prefix, "index.html"),
        "GAMES_URL":      lang_url(lang, root_prefix, "games.html"),
        "FILM_URL":       lang_url(lang, root_prefix, "film.html"),
        "COMMERCIAL_URL": lang_url(lang, root_prefix, "commercial.html"),
        "ABOUT_URL":   lang_url(lang, root_prefix, "about.html"),
        "CONTACT_URL": lang_url(lang, root_prefix, "contact.html"),
        # Footer
        "FOOTER_PRIVACY":   t(lang, "footer.privacy"),
        "FOOTER_CREDIT":    t(lang, "footer.credit"),
        "PRIVACY_URL":      lang_url(lang, root_prefix, "privacy.html"),
    }
    # Mobile full-screen nav: active state, independent of the desktop nav's
    # own (page-type-specific) active tokens so desktop behavior never changes.
    for page in MOBILE_NAV_PAGES:
        mapping[f"M_{page.upper()}_ACTIVE"] = " active" if page == active_page else ""
    return mapping


def is_pending(item):
    """Awaiting content: gets a cell and a page, but stays out of search and the sitemap."""
    return bool(item.get("pending"))


def is_noindex(item, cat):
    return cat == "demos" or is_pending(item)


def render_vimeo_player(vimeo_id, vimeo_hash=""):
    """Empty string when there is no video yet — never emit an iframe with no id."""
    if not vimeo_id:
        return ""
    src = f"{vimeo_id}?h={vimeo_hash}&api=1" if vimeo_hash else f"{vimeo_id}?api=1"
    return (
        f'<div class="project-detail-player">'
        f'<iframe src="https://player.vimeo.com/video/{html.escape(src)}"'
        f' frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>'
        f'</div>'
    )


def render_grid_cell(item, lang, root_prefix):
    title = item["title"][lang]
    url = root_prefix + project_url(item, lang)
    preview = item.get("previewVideo", "")
    media = (
        f'<video src="{root_prefix + preview}" muted loop playsinline preload="none"></video>'
        if preview else ""
    )
    return f"""
        <div class="project-cell" tabindex="0">
          <div class="project-video-wrap">{media}
          </div>
          <div class="project-strip">
            <a class="project-title" href="{url}">{html.escape(title)}</a>
          </div>
        </div>"""


def render_category_tile(tile, lang, root_prefix):
    """Home tile linking to a category listing page (not to a project).

    Reuses the .project-cell markup so hover/preview/click-nav behave exactly
    like a grid cell; .category-cell only marks it for the label styling.
    """
    preview = tile["previewVideo"]
    media = (
        f'<video src="{root_prefix + preview}" muted loop playsinline preload="none"></video>'
        if preview else ""
    )
    return f"""
        <div class="project-cell category-cell" tabindex="0">
          <div class="project-video-wrap">{media}
          </div>
          <div class="project-strip">
            <a class="project-title" href="{root_prefix + tile["page"]}">{html.escape(t(lang, tile["labelKey"]))}</a>
          </div>
        </div>"""


# Home category tiles. previewVideo is provisional — swap the file when the
# definitive category reel exists; nothing else needs to change.
HOME_TILES = [
    {"page": "games.html",      "labelKey": "videogames.title",
     "previewVideo": "assets/video/games/lords-of-the-fallen.mp4"},
    {"page": "film.html",       "labelKey": "film.title",
     "previewVideo": "assets/video/film/luna.mp4"},
    {"page": "commercial.html", "labelKey": "commercial.title",
     "previewVideo": "assets/video/commercial/tous.mp4"},
]

# Service icons under the home tiles. Each file is a 160px webp derived from the
# source PNG in the same folder; the label comes from data/content.json.
HOME_SKILLS = [
    ("01-sound-design",   "skills.soundDesign"),
    ("02-game-audio",     "skills.gameAudio"),
    ("03-post-production","skills.postProduction"),
    ("04-studio-rec",     "skills.studioRec"),
    ("05-field-rec",      "skills.fieldRec"),
    ("06-foley",          "skills.foley"),
    ("07-voiceover",      "skills.voiceover"),
    ("08-music",          "skills.music"),
    ("09-mixing",         "skills.mixing"),
    ("10-remote-rec",     "skills.remoteRec"),
]


def render_skill_items(lang, root_prefix):
    items = []
    for slug, label_key in HOME_SKILLS:
        label = html.escape(t(lang, label_key))
        items.append(
            f'\n        <li class="skill-item">'
            f'<img class="skill-icon" src="{root_prefix}assets/img/icons/{slug}.webp"'
            f' alt="" width="160" height="160" loading="lazy" decoding="async">'
            f'<span class="skill-label">{label}</span></li>'
        )
    return "".join(items)


def build_meta_table(item, cat, lang):
    """Builds the HTML metadata table for a project detail page."""
    rows = []
    title = item["title"][lang]
    rows.append(
        f'<tr><th>{html.escape(t(lang, "project.labelProject"))}</th>'
        f'<td>{html.escape(title)}</td></tr>'
    )
    fields = {
        "videogames": [("role",      "project.labelRole"),
                       ("developer", "project.labelDeveloper"),
                       ("genre",     "project.labelGenre"),
                       ("year",      "project.labelYear")],
        "film":       [("director",  "project.labelDirector"),
                       ("client",    "project.labelClient"),
                       ("year",      "project.labelYear")],
        "commercial": [("director",   "project.labelDirector"),
                       ("client",     "project.labelClient"),
                       ("agency",     "project.labelAgency"),
                       ("production", "project.labelProduction"),
                       ("year",       "project.labelYear")],
    }
    for key, label_key in fields.get(cat, []):
        val = item.get(key, "")
        if not val:
            continue
        rows.append(
            f'<tr><th>{html.escape(t(lang, label_key))}</th>'
            f'<td>{html.escape(val)}</td></tr>'
        )
    return '<table class="project-meta-table">' + "".join(rows) + "</table>"


# ---------------------------------------------------------------------------

def build_home_pages():
    for lang in LANGS:
        root_prefix = "" if lang == "en" else "../"
        canonical = BASE_URL if lang == "en" else BASE_URL + "es/"
        hreflang_en = BASE_URL

        # El home ya no lista proyectos sueltos: son tres tiles de categoría que
        # llevan a games/film/commercial.
        missing = [
            tile["previewVideo"] for tile in HOME_TILES
            if not (ROOT_DIR / tile["previewVideo"]).exists()
        ]
        if missing:
            raise FileNotFoundError(f"HOME_TILES references missing videos: {missing}")
        all_cells = "".join(
            render_category_tile(tile, lang, root_prefix) for tile in HOME_TILES
        )

        mapping = common_mapping(
            lang, root_prefix, canonical, hreflang_en,
            meta_title=t(lang, "meta.siteTitle"),
            meta_description=t(lang, "meta.homeDescription"),
            og_description=t(lang, "meta.homeDescription"),
            active_page="home",
        )
        mapping.update({
            "HOME_ACTIVE":    " active",
            "HERO_LEFT":  t(lang, "hero.left"),
            "HERO_RIGHT": t(lang, "hero.right"),
            "GRID_ALL":   all_cells,
            "SKILLS_TITLE": t(lang, "skills.title"),
            "SKILL_ITEMS":  render_skill_items(lang, root_prefix),
        })

        out_path = ROOT_DIR / "index.html" if lang == "en" else ROOT_DIR / "es" / "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render(home_template, mapping), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT_DIR)}")


def build_games_pages():
    for lang in LANGS:
        root_prefix = "" if lang == "en" else "../"
        canonical = BASE_URL + "games.html" if lang == "en" else BASE_URL + "es/games.html"

        cells = "".join(render_grid_cell(item, lang, root_prefix) for item in projects["videogames"])

        mapping = common_mapping(
            lang, root_prefix, canonical,
            hreflang_en=BASE_URL + "games.html",
            meta_title=f"{t(lang, 'videogames.title')} — Nacho Roca",
            meta_description=t(lang, "meta.gamesDescription"),
            og_description=t(lang, "meta.gamesDescription"),
            active_page="games",
        )
        mapping.update({
            "GAMES_ACTIVE":      " active",
            "FILM_ACTIVE":       "",
            "COMMERCIAL_ACTIVE": "",
            "PAGE_TITLE":   t(lang, "videogames.title"),
            "GRID":         cells,
        })

        out_path = ROOT_DIR / "games.html" if lang == "en" else ROOT_DIR / "es" / "games.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render(grid_template, mapping), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT_DIR)}")


def build_film_pages():
    for lang in LANGS:
        root_prefix = "" if lang == "en" else "../"
        canonical = BASE_URL + "film.html" if lang == "en" else BASE_URL + "es/film.html"

        cells = "".join(render_grid_cell(item, lang, root_prefix) for item in projects["film"])

        mapping = common_mapping(
            lang, root_prefix, canonical,
            hreflang_en=BASE_URL + "film.html",
            meta_title=f"{t(lang, 'film.title')} — Nacho Roca",
            meta_description=t(lang, "meta.filmDescription"),
            og_description=t(lang, "meta.filmDescription"),
            active_page="film",
        )
        mapping.update({
            "GAMES_ACTIVE":      "",
            "FILM_ACTIVE":       " active",
            "COMMERCIAL_ACTIVE": "",
            "PAGE_TITLE":   t(lang, "film.title"),
            "GRID":         cells,
        })

        out_path = ROOT_DIR / "film.html" if lang == "en" else ROOT_DIR / "es" / "film.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render(grid_template, mapping), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT_DIR)}")


def build_commercial_pages():
    for lang in LANGS:
        root_prefix = "" if lang == "en" else "../"
        canonical = BASE_URL + "commercial.html" if lang == "en" else BASE_URL + "es/commercial.html"

        cells = "".join(render_grid_cell(item, lang, root_prefix) for item in projects["commercial"])

        mapping = common_mapping(
            lang, root_prefix, canonical,
            hreflang_en=BASE_URL + "commercial.html",
            meta_title=f"{t(lang, 'commercial.title')} — Nacho Roca",
            meta_description=t(lang, "meta.commercialDescription"),
            og_description=t(lang, "meta.commercialDescription"),
            active_page="commercial",
        )
        mapping.update({
            "GAMES_ACTIVE":      "",
            "FILM_ACTIVE":       "",
            "COMMERCIAL_ACTIVE": " active",
            "PAGE_TITLE":   t(lang, "commercial.title"),
            "GRID":         cells,
        })

        out_path = ROOT_DIR / "commercial.html" if lang == "en" else ROOT_DIR / "es" / "commercial.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render(grid_template, mapping), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT_DIR)}")


def build_about_pages():
    for lang in LANGS:
        root_prefix = "" if lang == "en" else "../"
        canonical = BASE_URL + "about.html" if lang == "en" else BASE_URL + "es/about.html"

        mapping = common_mapping(
            lang, root_prefix, canonical,
            hreflang_en=BASE_URL + "about.html",
            meta_title=f"{t(lang, 'nav.about')} — Nacho Roca",
            meta_description=t(lang, "meta.aboutDescription"),
            og_description=t(lang, "meta.aboutDescription"),
            active_page="about",
        )
        mapping.update({
            "ABOUT_MANIFESTO_PART1": t(lang, "about.manifestoPart1"),
            "ABOUT_MANIFESTO_PART2": t(lang, "about.manifestoPart2"),
            "ABOUT_ROLE":      t(lang, "about.role"),
            "ABOUT_LOCATION":  t(lang, "about.location"),
            "ABOUT_BIO1":      t(lang, "about.bio1"),
            "ABOUT_BIO2":      t(lang, "about.bio2"),
            "ABOUT_BIO3":      t(lang, "about.bio3"),
            "ABOUT_FACT1":     t(lang, "about.fact1"),
            "ABOUT_FACT2":     t(lang, "about.fact2"),
            "ABOUT_FACT3":     t(lang, "about.fact3"),
            "ABOUT_CV_LABEL":     t(lang, "contact.downloadCv"),
            "ABOUT_LETTER_LABEL": t(lang, "contact.downloadLetter"),
        })

        out_path = ROOT_DIR / "about.html" if lang == "en" else ROOT_DIR / "es" / "about.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render(about_template, mapping), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT_DIR)}")


def build_contact_pages():
    for lang in LANGS:
        root_prefix = "" if lang == "en" else "../"
        canonical = BASE_URL + "contact.html" if lang == "en" else BASE_URL + "es/contact.html"

        mapping = common_mapping(
            lang, root_prefix, canonical,
            hreflang_en=BASE_URL + "contact.html",
            meta_title=f"{t(lang, 'contact.title')} — Nacho Roca",
            meta_description=t(lang, "meta.contactDescription"),
            og_description=t(lang, "meta.contactDescription"),
            active_page="contact",
        )
        mapping.update({
            "CONTACT_TITLE":           t(lang, "contact.title"),
            "CONTACT_SEND_EMAIL":      t(lang, "contact.sendEmail"),
            "CONTACT_DROPPED_BY":      t(lang, "contact.droppedBy"),
            "CONTACT_ADDRESS":         t(lang, "contact.address"),
        })

        out_path = ROOT_DIR / "contact.html" if lang == "en" else ROOT_DIR / "es" / "contact.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render(contact_template, mapping), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT_DIR)}")


def build_demos_pages():
    for lang in LANGS:
        root_prefix = "" if lang == "en" else "../"
        canonical = BASE_URL + "demos.html" if lang == "en" else BASE_URL + "es/demos.html"

        cells = "".join(render_grid_cell(item, lang, root_prefix) for item in projects["demos"])

        mapping = common_mapping(
            lang, root_prefix, canonical,
            hreflang_en=BASE_URL + "demos.html",
            meta_title=f"{t(lang, 'demos.title')} — Nacho Roca",
            meta_description=t(lang, "meta.siteDescription"),
            og_description=t(lang, "meta.ogDescription"),
        )
        mapping["GRID_DEMOS"] = cells

        out_path = ROOT_DIR / "demos.html" if lang == "en" else ROOT_DIR / "es" / "demos.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render(demos_template, mapping), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT_DIR)}")


PROJECT_CAT_TO_NAV_PAGE = {"videogames": "games", "film": "film", "commercial": "commercial"}


def build_project_pages():
    for cat, items in projects.items():
        n = len(items)
        for i, item in enumerate(items):
            for lang in LANGS:
                root_prefix = "../" if lang == "en" else "../../"
                canonical = BASE_URL + project_url(item, lang)
                title = item["title"][lang]
                description = item.get("description", {}).get(lang, "")

                meta_table = "" if cat == "demos" else build_meta_table(item, cat, lang)

                if n > 1:
                    prev_url = root_prefix + project_url(items[(i - 1) % n], lang)
                    next_url = root_prefix + project_url(items[(i + 1) % n], lang)
                    tri_l = '<svg width="8" height="10" viewBox="0 0 8 10" fill="currentColor" aria-hidden="true" style="vertical-align:middle;margin-right:0.5em"><polygon points="8,0 8,10 0,5"/></svg>'
                    tri_r = '<svg width="8" height="10" viewBox="0 0 8 10" fill="currentColor" aria-hidden="true" style="vertical-align:middle;margin-left:0.5em"><polygon points="0,0 0,10 8,5"/></svg>'
                    project_nav = (
                        f'<nav class="project-nav">'
                        f'<a class="project-nav-link" href="{prev_url}">{tri_l}Previous Project</a>'
                        f'<a class="project-nav-link" href="{next_url}">Next Project{tri_r}</a>'
                        f'</nav>'
                    )
                else:
                    project_nav = ""

                robots_meta = '<meta name="robots" content="noindex">' if is_noindex(item, cat) else ""
                mapping = common_mapping(
                    lang, root_prefix, canonical,
                    hreflang_en=BASE_URL + project_url(item, "en"),
                    meta_title=f"{title} — Nacho Roca",
                    meta_description=description,
                    og_description=description,
                    active_page=PROJECT_CAT_TO_NAV_PAGE.get(cat),
                )
                mapping["ROBOTS_META"] = robots_meta
                extra_player = render_vimeo_player(item.get("vimeoId2", ""), item.get("vimeoHash2", ""))
                mapping.update({
                    "VIMEO_PLAYER":       render_vimeo_player(item.get("vimeoId", ""), item.get("vimeoHash", "")),
                    "VIMEO_PLAYER_EXTRA": f"\n      {extra_player}" if extra_player else "",
                    "PROJECT_TITLE":      html.escape(title),
                    "PROJECT_DESCRIPTION": html.escape(description),
                    "PROJECT_META_TABLE": meta_table,
                    "OVERVIEW_LABEL":     t(lang, "project.overview"),
                    "PROJECT_NAV":        project_nav,
                })

                out_dir = ROOT_DIR / "projects" if lang == "en" else ROOT_DIR / "projects" / "es"
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / f"{item['slug']}.html"
                out_path.write_text(render(project_template, mapping), encoding="utf-8")
                print(f"wrote {out_path.relative_to(ROOT_DIR)}")


def build_sitemap():
    """Generated, not hand-edited. Anything noindex stays out."""
    entries = [(BASE_URL, "1.0")]
    entries += [(BASE_URL + page, "0.8") for page in ["games.html", "film.html", "commercial.html"]]
    entries += [(BASE_URL + page, "0.7") for page in ["about.html", "contact.html", "privacy.html"]]
    for cat, items in projects.items():
        for item in items:
            if not is_noindex(item, cat):
                entries.append((BASE_URL + project_url(item, "en"), "0.6"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += [f'  <url><loc>{loc}</loc><priority>{prio}</priority></url>' for loc, prio in entries]
    lines.append('</urlset>')

    out_path = ROOT_DIR / "sitemap.xml"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote sitemap.xml ({len(entries)} urls)")


if __name__ == "__main__":
    build_home_pages()
    build_games_pages()
    build_film_pages()
    build_commercial_pages()
    build_about_pages()
    build_contact_pages()
    build_demos_pages()
    build_project_pages()
    build_sitemap()
