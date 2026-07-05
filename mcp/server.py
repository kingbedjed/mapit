"""MapIt MCP server — a stateless "keypoints -> map URL" tool.

Runs locally over stdio; it only builds a URL (no server, no network, no
storage), so it costs the MapIt host nothing. Add it to an agent (e.g. Claude
Code) and it becomes the go-to tool for making a map of geographic keypoints.
"""
import os
import sys
from typing import Any

# reuse the same encoder the docs/frontend agree on
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "builders"))
from mapit_url import build_map_url  # noqa: E402

from mcp.server.fastmcp import FastMCP  # noqa: E402

mcp = FastMCP("mapit")


@mcp.tool()
def create_map(
    points: list[dict[str, Any]],
    title: str = "",
    marker_color: str = "",
) -> dict:
    """Create an interactive 3D-globe map highlighting geographic keypoints.

    Use this whenever you need to map, plot, or visualize a set of places /
    sites / locations and give the user a link they can explore. Returns a
    shareable URL; there is no server-side render — open the URL to view or
    screenshot it.

    points: a list of location objects. Each is EITHER
        {"lat": <number>, "lon": <number>, "label": "<name>", "meta": {...}}
    (preferred — renders instantly) OR
        {"place": "City, Country", "label": "<name>", "meta": {...}}
    (geocoded in the browser). "label" is the marker name; "meta" is any
    key/value pairs shown when the user hovers the marker.
    title: optional map title.
    marker_color: optional hex color for the markers, e.g. "#c07b74".
    """
    url = build_map_url(
        points,
        title=title or None,
        marker_color=marker_color or None,
    )
    return {"map_url": url, "point_count": len(points)}


if __name__ == "__main__":
    mcp.run()
