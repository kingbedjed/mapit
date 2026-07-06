# MapIt

An interactive 3D globe (Three.js / WebGL) that plots points from a CSV. Drop in
a `city, country, …metadata` CSV and each row becomes a glowing marker on a
rotating Earth; hover or click a marker to see its details. No coordinates
needed — cities are geocoded automatically.

Pure static frontend — the server only serves files. Extracted from
`jeds_useful_code/interactive_map` and hardened for hosting.

Live at **https://jeddoman.com/mapit**.

## CSV format
```csv
city,country,[any other columns you want]
New York,USA,Financial Hub,8.3M
Tokyo,Japan,Tech Center,14.0M
```
First two columns are city + country; everything after is shown on hover. See
[CSV_USAGE.md](CSV_USAGE.md).

## Run locally
```sh
python -m http.server 8005 --directory web
# open http://localhost:8005/
```

## Layout
```
web/                      # docroot served on :8005
  index.html              # the app
  geocoder.js             # Nominatim geocoding + localStorage cache
  cities.csv              # sample data
  textures/earth_atmos_2048.jpg   # vendored Earth texture
deploy/mapit.service      # systemd user unit (serves web/ on 127.0.0.1:8005)
```

## For agents

MapIt is built to be an agent's go-to tool for "make a map of these keypoints",
while staying 100% client-side (nothing is stored or rendered on the server).
An agent hands over points and gets a shareable URL — the data rides in the URL
fragment, so there's no API to run.

- **MCP tool** — `mcp/server.py` exposes `create_map(points, title, marker_color)`.
  Add it with `claude mcp add mapit -- python $PWD/mcp/server.py`. See
  [mcp/README.md](mcp/README.md).
- **URL builder** — `builders/mapit_url.py` (`build_map_url(...)`) for non-MCP use.
- **Spec** — [web/llms.txt](web/llms.txt) (served at `/mapit/llms.txt`) documents
  the `#d=<gzip+base64url JSON>` encoding and the point schema.
- **Design** — [docs/agent-integration.md](docs/agent-integration.md).

Point schema: each is `{lat, lon, label, meta}` (renders instantly) or
`{place: "City, Country", label, meta}` (geocoded in the browser).

## Tests

The documented example gallery (in `web/llms.txt` / the MCP tool) is the test
suite — every example is exercised, so a broken or undocumented example fails
rather than silently shipping. Examples live once in `tests/gallery.py`.

```sh
python tests/test_gallery_builder.py   # fast: builds + round-trips each example,
                                       # and checks each is documented (no deps)
python tests/test_gallery_render.py    # renders each in a headless browser
                                       # (needs playwright + internet; auto-skips
                                       #  if unavailable)
```

To add a gallery example: add it to `tests/gallery.py` and to the prose gallery
in `web/llms.txt` — the builder test enforces that both exist.

## Hosting notes
- **Earth texture is vendored** (`web/textures/`) rather than hotlinked from
  GitHub raw, so it can't break when that path moves.
- **Three.js** loads from the jsDelivr CDN (a real CDN; reliable).
- **Geocoding** uses Nominatim (OpenStreetMap), rate-limited to 1 req/sec and
  cached in the browser's `localStorage`. It identifies via the `email` param
  per Nominatim's usage policy. Keep datasets modest; it's not for bulk geocoding.
- Behind nginx the app is served under `/mapit/` with a `<base href="/mapit/">`
  inject, so its relative asset paths resolve correctly.
