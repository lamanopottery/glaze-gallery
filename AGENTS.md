# Glaze Gallery

## Overview

Glaze Gallery is a password-protected web gallery for browsing photos of two-glaze
("1st dip / 2nd dip") combinations. It has two decoupled halves:

- **Astro frontend** (`src/`) — TypeScript, server-rendered, deployed to Cloudflare Pages.
- **Python data pipeline** (`glaze_gallery/`) — Poetry project that pulls source data from Google
  Sheets/Drive, processes images, and publishes JSON manifests + images to object storage.

The frontend never touches Google APIs — it only reads the JSON manifests and images the pipeline
publishes.

## Commands

Frontend (Node 22 / Yarn 4, see `.nvmrc`):

- `yarn dev` — runs `download_data`, then starts the Astro dev server.
- `yarn build` — runs `download_data`, then `astro check` (typecheck) and `astro build`.
- `yarn preview` — serves the built `dist/` via `wrangler pages dev` (Cloudflare runtime).
- `yarn lint` — `astro check` + `prettier --check .`. Prettier is the formatter (`prettier --write .`).

Python pipeline (Poetry, Python ≥ 3.11):

- `poetry run download_data` — fetches the four JSON manifests into `src/data/`. Cheap; runs
  automatically before every `dev`/`build`. **Overwrites `src/data/`**, so don't hand-edit it.
- `poetry run download_images` — the heavy pipeline: reads the Google Sheet, downloads images from
  Drive, resizes/watermarks them, and writes per-studio output to `downloads/`. Run manually when
  the source data changes; requires Google OAuth (`credentials.json` → `token.json`).
- `poetry run mypy glaze_gallery` — typecheck.

There is no test suite.

## Architecture

### Data flow

```
Google Sheet (combo metadata) + Google Drive (raw photos)
        │  download_images  (manual, glaze_gallery/_download_images.py)
        ▼
downloads/<studio>/  →  uploaded to object storage (GLAZE_GALLERY_IMAGES_URL)
   ├─ WebP image variants            (each in its own random UUID dir)
   └─ glaze-names / glaze-combo-info / images-{high,low} JSON  (also in random UUID dirs)
        │  download_data  (auto on dev/build; manifest paths come from per-file env vars)
        ▼
src/data/*.json  →  imported directly by Astro pages/components
```

The Google Sheet is the source of truth for which combos exist and their warning flags
(`not_food_safe`, `runny`, `blister_jump_crawl`, `notes`). `download_images` also stamps a
"last synced" timestamp back into the sheet.

### Multi-studio (single codebase, multiple deployments)

One codebase serves multiple pottery studios (currently "La Mano Pottery" and "Mud Matters").
`download_images` produces a **separate data set per studio** (`downloads/la-mano`,
`downloads/mud-matters`), honoring per-row `hide_la_mano` / `hide_mud_matters` flags so a combo can
appear on one studio's site but not another's. At runtime the active studio is chosen by
`GLAZE_GALLERY_STUDIO`, which selects branding (logo + favicons) in `src/utils/studio.ts`. Adding a
studio touches **both** sides: the `STUDIOS` map in `studio.ts` (+ logo assets) and the hardcoded
per-studio dirs/flags/logos in `_download_images.py`.

### Image hosting & obfuscation

Image URLs are not predictable. Each image lives under a random UUID directory; the
`images-low.json` / `images-high.json` manifests map a logical name (`<combo>-<front|back>`) to its
UUID prefix. `imageURL()` in `src/utils/glaze-combos.ts` reconstructs the URL as
`{GLAZE_GALLERY_IMAGES_URL}/{uuidPrefix}/{name}-{low|high}.webp`. The pipeline also writes a
`robots.txt` disallowing all crawlers. `_image_processing.py` produces high (2000px) and low
(1000px) WebP variants and paints a translucent studio logo watermark.

### Naming conventions

Glaze names are normalized to a key by lowercasing and stripping whitespace (`_format_glaze` in
Python; combo key is `<glaze1key>-<glaze2key>`). The same keys are used in URLs, JSON manifests, and
image filenames, so they must stay consistent across the pipeline and frontend.

### Auth

Password-gated (`GLAZE_GALLERY_PASSWORD`) with JWT cookies signed via `jose` (`src/utils/login.ts`):
a short-lived `login-token` (30 min) and a `refresh-token` (7 days) that silently re-mints it. Every
protected page guards in its frontmatter with
`if (!(await isLoggedIn(Astro))) return redirectToLogin(Astro);`. Auth is per-request, so the site
runs in Astro `output: "server"` mode (no static prerender).

### Pages

- `src/pages/index.astro` — the gallery grid. Tiles render server-side; filtering by 1st/2nd dip is
  **client-side**, toggling `display` on `.glaze-tile` elements and syncing to URL search params
  (`1st-dip` / `2nd-dip`, see `src/constants.ts`). Tiles flip front/back via a CSS 3D transform.
- `src/pages/[glaze1]-[glaze2].astro` — single-combo detail page (work in progress). Validates the
  params against the manifests and rewrites to `/404` if unknown.

## Conventions & gotchas

- **Path alias**: `@/*` maps to `src/*` (see `tsconfig.json`).
- **Env vars** are split by process. The **Python pipeline reads `.env`** (copy
  `.env.example`), while the **Astro/Wrangler runtime reads `.dev.vars`** (copy
  `.dev.vars.example`). Only variables used by both processes, currently
  `GLAZE_GALLERY_IMAGES_URL`, belong in both files and must stay in sync. The populated files are
  ignored; the example files are committed and should be updated whenever configuration changes.
  Astro variables are declared with a typed schema in `astro.config.ts` and imported via
  `astro:env/server`; mark secrets with `access: "secret"`.
- `src/data/*.json` is generated — edit the Google Sheet and re-run the pipeline, not the JSON.
- TypeScript extends `astro/tsconfigs/strict`; mypy is `strict`. Keep both clean — `astro check`
  runs in the build.
