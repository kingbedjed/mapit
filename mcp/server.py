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
    auto_rotate: bool = True,
    connect: bool = False,
    labels: bool | None = None,
    arc_color: str = "",
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
    key/value pairs shown when the user hovers the marker. A point may also
    set "color" (hex) and "size" to style itself.
    title: optional map title.
    marker_color: optional default hex color for the markers, e.g. "#c07b74".
    auto_rotate: leave True for a spinning globe; set False for a still,
        framed view (better if you're going to screenshot it).
    connect: True draws arcs between consecutive points (e.g. a route);
        arc_color optionally colors them (hex).
    labels: True/False forces marker text labels on/off (default: shown for
        small maps of <= 15 points).

    Examples:
      # one pin
      create_map(points=[{"lat": 35.99, "lon": -78.90, "label": "Durham HQ"}])
      # a route, framed still for a screenshot
      create_map(connect=True, auto_rotate=False, points=[
          {"lat": 51.51, "lon": -0.13, "label": "London"},
          {"lat": 48.85, "lon": 2.35,  "label": "Paris"}])
      # groups by color, with hover details
      create_map(points=[
          {"lat": 37.77, "lon": -122.42, "label": "SF",  "color": "#6a9a72", "meta": {"type": "customer"}},
          {"place": "Chicago, USA",       "label": "Chi", "color": "#c07b74", "meta": {"type": "supplier"}}])
    """
    url = build_map_url(
        points,
        title=title or None,
        marker_color=marker_color or None,
        auto_rotate=auto_rotate,
        connect=connect,
        labels=labels,
        arc_color=arc_color or None,
    )
    return {"map_url": url, "point_count": len(points)}


if __name__ == "__main__":
    mcp.run()
