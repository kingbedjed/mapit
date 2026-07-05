# MapIt for agents — integration plan

Goal: make MapIt the go-to tool an agent reaches for when it needs to build a
map highlighting geographic keypoints — **without giving up MapIt's core virtue:
everything renders client-side, the server just serves static files.**

Decisions locked:
- Agents call it via **both an MCP tool and a plain HTTP/URL contract**.
- A call returns an **interactive link** (no server-side image render — agents
  that need a picture screenshot the link with their own harness).
- Points are **coordinates preferred, place names geocoded in the browser** when
  given (same as the original).

## The design keeps the server static

The insight that preserves the light-server model: an agent doesn't need a
backend to hand over data — it **encodes the data into the URL**. Nothing is
stored or computed server-side; the browser does all the work, exactly like the
original drag-drop flow.

```
https://jeddoman.com/mapit/#d=<gzip+base64 JSON>
```

The `#`-fragment is never sent to the server (no logs, no URL-length server
limits, no state). The page decodes it, parses the points, geocodes any names in
the browser, and renders. For larger sets, `?data_url=<csv/json the agent hosts
elsewhere>` — the browser fetches it (needs CORS on that host); MapIt's server
still stores nothing.

Payload shape:
```json
{
  "title": "Customer sites",
  "options": {"marker_color": "#c07b74", "projection": "globe"},
  "points": [
    {"lat": 35.99, "lon": -78.90, "label": "Durham HQ", "meta": {"staff": 40}},
    {"place": "Tokyo, Japan", "label": "APAC office"}
  ]
}
```
Each point is `{lat,lon}` OR `{place}`, plus `label` and free-form `meta` (shown
on hover). Coordinates render instantly; names geocode client-side via Nominatim
(cached in localStorage, as today).

## What changes vs today (all client-side)

Only the **frontend** changes — the server stays a static host (nginx can serve
`web/` directly; the tiny static service is optional).

1. On load, read `#d=` (or `?data_url=`), inflate + parse, and render — in
   addition to the existing drag-drop.
2. Accept explicit `{lat,lon}` points (skip geocoding) alongside `{place}`.
3. Carry `label` + arbitrary `meta` per point through to the hover card.
4. (Optional) a tiny "Copy shareable link" that encodes the current dataset back
   into a `#d=` URL — useful for humans too.

## The agent interface (stateless, ~zero server cost)

A **"points → URL" builder**, exposed two ways over the SAME trivial logic
(gzip+base64-encode the payload, append to the base URL):

- **MCP server** `mapit`: `create_map(points, title="", marker_color=None,
  projection="globe") -> { map_url }`. It just builds the URL — no rendering, no
  storage. Runs as a **stdio** process on the agent's own machine (zero server
  cost) and/or a trivial stateless remote endpoint. Tool description tuned so
  agents pick it: "Create an interactive map/globe highlighting geographic
  keypoints (locations with labels + metadata); returns a shareable URL. Use
  whenever asked to map/plot/visualize places or sites."
- **Plain URL contract** for non-MCP agents: documented `#d=` encoding + a
  one-function snippet (JS/Python) to build the link. No endpoint to call at all
  — the agent constructs the URL itself.

Discoverability: a static `/mapit/llms.txt` (what it is + the encoding + an
example) and the MCP tool schema. Both are static/description only.

## Milestones (each independently useful)

1. **Frontend accepts encoded data** — `#d=`/`?data_url=`, explicit coords,
   `label`+`meta`. Now an agent can hand-build a URL and get a live map. Server
   unchanged (still static).
2. **URL-builder spec + llms.txt** — document the encoding + ship a tiny builder
   snippet so any agent/framework can make links.
3. **MCP server** — stateless `create_map`, stdio + optional remote transport.
4. **Polish** — examples, publish/register the MCP server.

## Explicitly NOT doing (to stay light)

- No backend service, no database, no stored map ids — data lives in the URL.
- No server-side geocoding — stays in the browser.
- No server-side image rendering — agents screenshot the link if they need a
  picture. (If that ever becomes essential, it's an isolated, opt-in add-on, not
  part of the core.)

## Open considerations

- **URL size.** Fragments handle megabytes fine and aren't sent to the server;
  gzip+base64 keeps keypoint-scale payloads tiny. Huge datasets → use `data_url`.
- **`data_url` CORS.** The agent's hosted CSV/JSON must allow cross-origin fetch.
- **Globe vs flat map.** A flat 2D map often reads clearer for a few keypoints in
  a document; the `projection` option leaves room for a 2D mode later — still
  100% client-side.
- **Trust.** Since there's no server state or write API, there's nothing to abuse
  server-side — a nice side effect of the URL-encoded design.
