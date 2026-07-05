# MapIt MCP server

Exposes MapIt as an MCP tool, `create_map`, so an agent can turn a list of
geographic keypoints into a shareable interactive-globe URL. It is **stateless
and local** — it only builds a URL (gzip+base64url of the payload), so it makes
no network calls and costs the MapIt host nothing.

## Install

```sh
pip install mcp          # the MCP Python SDK
```

Run directly (stdio):
```sh
python mcp/server.py
```

## Add to Claude Code

```sh
claude mcp add mapit -- python /home/jed/git/mapit/mcp/server.py
```

Or in an MCP client config (`mcpServers`):
```json
{
  "mcpServers": {
    "mapit": {
      "command": "python",
      "args": ["/home/jed/git/mapit/mcp/server.py"]
    }
  }
}
```

## The tool

`create_map(points, title="", marker_color="") -> { map_url, point_count }`

- `points`: list of `{lat, lon, label, meta}` (preferred) or
  `{place, label, meta}` (browser-geocoded).
- Returns a `map_url` like `https://jeddoman.com/mapit/#d=...`. Open it to view
  the globe; screenshot it if you need a static image.

## Non-MCP agents

You don't need this server — just build the URL yourself with
`builders/mapit_url.py` or the encoding documented in `web/llms.txt`.
