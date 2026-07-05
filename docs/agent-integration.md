# MapIt for agents — integration plan

Goal: make MapIt the go-to tool an agent reaches for when it needs to build a
map highlighting geographic keypoints. Decisions locked: **both MCP + HTTP
API**, **return both an interactive link and a static image**, **accept
coordinates preferred, geocode place names when needed**.

## The one-call contract

An agent hands over keypoints and gets back a link + an image in a single call.

```
POST /mapit/api/maps
{
  "title": "Customer sites",
  "points": [
    {"lat": 35.99, "lon": -78.90, "label": "Durham HQ", "meta": {"staff": 40}},
    {"place": "Tokyo, Japan", "label": "APAC office"}
  ],
  "options": {"marker_color": "#c07b74", "projection": "globe"}
}
->
{
  "id": "k3f9a2",
  "map_url":   "https://jeddoman.com/mapit/m/k3f9a2",
  "image_url": "https://jeddoman.com/mapit/api/maps/k3f9a2/image.png",
  "resolved":  [ {"label":"APAC office","lat":35.68,"lon":139.65,"source":"geocoded"} ],
  "warnings":  []
}
```

Each point is `{lat,lon}` OR `{place}`, plus `label` and free-form `meta`
(shown on hover). Names are geocoded server-side and cached; coordinates pass
straight through (fast, deterministic, no rate limit).

## Architecture

One FastAPI service (replaces the current `python -m http.server` on :8005)
that serves the existing globe AND the API — one service, one nginx route.

| Piece | What |
|---|---|
| Static mount | serves `web/` (the globe) as today |
| `POST /api/maps` | create a map from JSON points or CSV → store → return urls |
| `GET /api/maps/{id}` | the dataset JSON the globe fetches to render |
| `GET /m/{id}` | the interactive globe, preloaded with dataset `{id}` |
| `GET /api/maps/{id}/image.png` | server-rendered PNG (headless chromium), cached |
| geocoding module | Nominatim client + sqlite cache + 1 req/s limiter |
| storage | sqlite: `maps(id, points_json, options_json, created_at)` |

**Frontend change:** the globe reads a dataset id from the URL and fetches
`/api/maps/{id}` (keep drag-drop for humans). Add a `window.__mapitReady = true`
signal once markers are placed so the screenshotter knows when to capture.

**Static render:** `image.png` loads `/m/{id}` in headless chromium (Playwright
is already on the box), waits for `__mapitReady`, screenshots, caches the PNG by
id. This is the piece that lets an agent embed a map in a report/message.

**MCP server** (`mapit-mcp`, thin wrapper over the HTTP API) exposes:
```
create_map(points, title="", marker_color=None, projection="globe")
    -> { map_url, image_url, warnings }
get_map_image(id) -> image bytes
```
Tool description tuned so agents pick it: "Create an interactive map/globe
highlighting geographic keypoints (locations with labels + metadata). Returns a
shareable interactive URL and a static PNG. Use whenever asked to map, plot, or
visualize places/sites/locations."

Transport: **stdio** for local agents (Claude Code) + **remote HTTP/SSE** at a
stable URL (e.g. `mcp.jeddoman.com` or `/mapit/mcp`) so hosted agents can add it
as a remote MCP server. Backed by the same HTTP API, so non-MCP frameworks use
`POST /api/maps` directly.

**Discoverability:** `/mapit/llms.txt` (what it is + how to call it), FastAPI's
free OpenAPI at `/mapit/api/openapi.json`, and a "for agents" section in the
README with copy-paste examples.

## Milestones

1. **API + id-loaded globe** — `POST /api/maps`, storage, server-side geocode +
   cache, globe loads by id. Agent can POST points and get an interactive link.
2. **Static PNG render** — headless screenshot endpoint, cached. Dual output done.
3. **MCP server** — stdio + remote HTTP/SSE, wrapping the API.
4. **Discoverability** — llms.txt, OpenAPI polish, agent examples; publish/register
   the MCP server.

Each milestone is independently useful and deployable.

## Open questions / risks (decide as we build)

- **Abuse / auth.** A public write API can be spammed (storage fill, geocoding
  abuse). Mitigate: rate-limit writes, cap dataset size, TTL old maps, optionally
  require an API key for `POST` while leaving reads public. Decide the trust model.
- **Render cost.** Headless chromium per image is heavy — cache PNGs by id,
  render lazily on first request, cap concurrency.
- **Geocoding at volume.** Nominatim is rate-limited and not for bulk; cache hard.
  If agents push large batches, consider a bulk-friendly geocoder or requiring
  coords above N points.
- **Globe vs flat map.** A 3D globe is striking but a flat 2D map often reads
  clearer for "highlight a few points." The `projection` option leaves room for a
  2D mode later — worth it for agent output that goes into documents.
- **Hosting.** FastAPI on :8005 (existing nginx route). MCP remote transport
  needs its own port + nginx route or subdomain via the tunnel. Data/PNG cache in
  a gitignored `~/.local/share/mapit/`.
