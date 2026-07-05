"""Build a MapIt share URL from a set of geographic keypoints.

100% client-side model: this only *builds a URL* (gzip + base64url of a JSON
payload in the fragment). Nothing is sent to a server here. Reused by the MCP
server in ../mcp/.
"""
import base64
import gzip
import json

BASE_URL = "https://jeddoman.com/mapit/"


def build_map_url(points, title=None, marker_color=None, projection="globe",
                  base_url=BASE_URL):
    """Return a shareable MapIt URL rendering `points`.

    points: list of dicts, each either
        {"lat": <num>, "lon": <num>, "label": <str>, "meta": {...}}   or
        {"place": "City, Country", "label": <str>, "meta": {...}}     or
        {"city": "...", "country": "...", "label": <str>, "meta": {...}}
    title / marker_color / projection: optional map options.
    """
    options = {"projection": projection}
    if marker_color:
        options["marker_color"] = marker_color

    payload = {"points": points, "options": options}
    if title:
        payload["title"] = title

    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    enc = base64.urlsafe_b64encode(gzip.compress(raw)).decode("ascii").rstrip("=")
    return f"{base_url}#d={enc}"


if __name__ == "__main__":
    demo = [
        {"lat": 35.99, "lon": -78.90, "label": "Durham HQ", "meta": {"staff": 40}},
        {"place": "Tokyo, Japan", "label": "APAC office", "meta": {"region": "APAC"}},
    ]
    print(build_map_url(demo, title="Customer sites", marker_color="#c07b74"))
