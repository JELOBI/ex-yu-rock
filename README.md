# EX-YU Rock Centar – tablet pages

Four standalone pages, one per exhibition tablet. Each button opens the matching PDF.

| Page | Room | PDFs |
|---|---|---|
| `tablet-1.html` | Room 1 | Roots / Rock Bands (14) |
| `tablet-2.html` | Room 2 | Pop Rock Bands (9) |
| `tablet-3.html` | Room 2 | The New Primitives Movement (4) |
| `tablet-4.html` | Room 3 | Sarajevo Demo Scene Bands (11) |

- `pdf/` – optimized PDFs (~1.3 MB each, text still selectable)
- `img/logo.png` – footer logo
- `tools/make_site.py` – regenerates the 4 pages from one list (edit labels/PDF names there)
- `tools/optimize_pdf.py` – shrinks a new PDF the same way (background JPEGs only)

Hosting: GitHub Pages (Settings → Pages → deploy from branch, root). Page URLs:
`https://<user>.github.io/<repo>/tablet-1.html` … `tablet-4.html`.
