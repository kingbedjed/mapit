"""Canonical MapIt example gallery — the single source of truth.

The same examples appear (in prose) in web/llms.txt and the MCP tool docstring;
the tests here exercise every entry, so a broken or undocumented example fails
the suite instead of silently shipping in the docs.

Each entry: a name, the build_map_url/create_map kwargs, and how many points to
expect after rendering.
"""

EXAMPLES = [
    {
        "name": "single_pin",
        "expect_points": 1,
        "kwargs": {
            "points": [{"lat": 35.99, "lon": -78.90, "label": "Durham HQ"}],
        },
    },
    {
        "name": "sites_with_meta",
        "expect_points": 2,
        "kwargs": {
            "title": "US offices",
            "points": [
                {"lat": 40.71, "lon": -74.01, "label": "New York", "meta": {"staff": 120, "opened": 2015}},
                {"place": "Austin, Texas", "label": "Austin", "meta": {"staff": 45, "opened": 2021}},
            ],
        },
    },
    {
        "name": "route",
        "expect_points": 3,
        "kwargs": {
            "title": "Delivery route",
            "connect": True, "arc_color": "#6a9a72", "auto_rotate": False,
            "points": [
                {"lat": 51.51, "lon": -0.13, "label": "London"},
                {"lat": 48.85, "lon": 2.35, "label": "Paris"},
                {"lat": 52.52, "lon": 13.41, "label": "Berlin"},
            ],
        },
    },
    {
        "name": "groups_by_color",
        "expect_points": 3,
        "kwargs": {
            "title": "Supply network",
            "points": [
                {"lat": 37.77, "lon": -122.42, "label": "SF — customer", "color": "#6a9a72"},
                {"lat": 40.71, "lon": -74.01, "label": "NYC — supplier", "color": "#c07b74"},
                {"lat": 41.88, "lon": -87.63, "label": "Chicago — supplier", "color": "#c07b74"},
            ],
        },
    },
    {
        "name": "with_photos",
        "expect_points": 1,
        "kwargs": {
            "title": "Property tour",
            "points": [
                {"lat": 37.77, "lon": -122.42, "label": "Loft",
                 "images": ["https://example.com/loft1.jpg", "https://example.com/loft2.jpg"],
                 "meta": {"price": "$2,400/mo"}},
            ],
        },
    },
    {
        "name": "still_labeled",
        "expect_points": 3,
        "kwargs": {
            "title": "APAC sites",
            "auto_rotate": False, "labels": True,
            "points": [
                {"lat": 35.68, "lon": 139.65, "label": "Tokyo"},
                {"lat": 1.35, "lon": 103.82, "label": "Singapore"},
                {"lat": -33.87, "lon": 151.21, "label": "Sydney"},
            ],
        },
    },
]


def signature(ex):
    """A distinctive string that must appear in the docs (title, else first label)."""
    kw = ex["kwargs"]
    return kw.get("title") or kw["points"][0]["label"]
