#!/usr/bin/env python3
"""Fast, dependency-free gallery tests: every example builds, its encoded
payload round-trips with the right options, and it's actually in the docs.
Runs anywhere (no browser, no server)."""
import base64
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "builders"))
from gallery import EXAMPLES, signature  # noqa: E402
from mapit_url import build_map_url        # noqa: E402


def decode(url):
    enc = url.split("#d=")[1]
    enc += "=" * (-len(enc) % 4)  # restore stripped base64 padding
    return json.loads(gzip.decompress(base64.urlsafe_b64decode(enc)))


def test_examples_build_and_roundtrip():
    for ex in EXAMPLES:
        name, kw = ex["name"], ex["kwargs"]
        url = build_map_url(**kw)
        assert url.startswith("https://jeddoman.com/mapit/#d="), name

        payload = decode(url)
        assert len(payload["points"]) == ex["expect_points"], name

        opt = payload.get("options", {})
        if kw.get("connect"):
            assert opt.get("connect") is True, name
        if kw.get("auto_rotate") is False:
            assert opt.get("auto_rotate") is False, name
        if kw.get("labels") is True:
            assert opt.get("labels") is True, name
        if kw.get("arc_color"):
            assert opt.get("arc_color") == kw["arc_color"], name
        # per-point color/size survive the round-trip
        for src, out in zip(kw["points"], payload["points"]):
            if "color" in src:
                assert out.get("color") == src["color"], name
            if "images" in src:
                assert out.get("images") == src["images"], name


def test_examples_are_documented():
    """Every gallery example must appear in llms.txt, so docs and tests can't
    drift apart."""
    llms = open(os.path.join(HERE, "..", "web", "llms.txt"), encoding="utf-8").read()
    for ex in EXAMPLES:
        assert signature(ex) in llms, f"{ex['name']} not documented in llms.txt"


if __name__ == "__main__":
    test_examples_build_and_roundtrip()
    test_examples_are_documented()
    print(f"✅ gallery builder tests passed ({len(EXAMPLES)} examples)")
