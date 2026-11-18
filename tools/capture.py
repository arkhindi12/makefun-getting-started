#!/usr/bin/env python3
"""Capture the GitHub repository page of arkhindi12/makefun-getting-started.

Writes screenshot.png beside this file's parent (the repository root): a PNG of
the repository page at 1280 px wide, full page but capped so the pixel count
stays under 16,000,000, taken after the README has rendered.

    python3 tools/capture.py [--url URL] [--out PATH] [--width 1280]

Requires playwright with its bundled Chromium (~/.cache/ms-playwright).
Exit code 0 on a written, in-spec PNG; 1 otherwise.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_URL = "https://github.com/arkhindi12/makefun-getting-started"
MAX_PIXELS = 16_000_000  # the bounty's cap on screenshot.png
MAX_BYTES = 8 * 1024 * 1024
DEFAULT_WIDTH = 1280


def parse_args(argv: list[str]) -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default=DEFAULT_URL, help=f"page to capture (default {DEFAULT_URL})")
    ap.add_argument(
        "--out",
        default=str(here.parent / "screenshot.png"),
        help="where to write the PNG (default: screenshot.png at the repository root)",
    )
    ap.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="viewport width in CSS pixels")
    ap.add_argument("--timeout", type=float, default=60.0, help="seconds to wait for the README")
    ap.add_argument("--max-pixels", type=int, default=MAX_PIXELS, help="cap on width*height")
    return ap.parse_args(argv)


def wait_for_readme(page, timeout_s: float) -> None:
    """Block until the README article has rendered with visible text."""
    page.wait_for_selector("article.markdown-body", state="visible", timeout=timeout_s * 1000)
    # GitHub renders the README lazily; wait until it actually holds text, not a spinner.
    page.wait_for_function(
        """() => {
            const el = document.querySelector('article.markdown-body');
            if (!el) return false;
            const text = (el.innerText || '').trim();
            return text.length > 200;
        }""",
        timeout=timeout_s * 1000,
    )
    # Images (the three badges) load after the text; give them a moment, never fail on them.
    try:
        page.wait_for_load_state("networkidle", timeout=10_000)
    except Exception:
        pass


def capture(page, max_pixels: int) -> tuple[bytes, int, int]:
    """Capture the page at normal scale, cropping its height to the pixel cap.

    The whole page is taken in one full-page shot. When that is over the pixel
    cap, the image is cropped from the top to exactly what fits rather than
    scaled down: the top of the image is what the board and the Feed show, and a
    downscaled capture would make the guide unreadable.
    """
    from PIL import Image

    shot = page.screenshot(full_page=True, animations="disabled", caret="hide", scale="css")
    img = Image.open(io.BytesIO(shot))
    width, height = img.size
    if width * height <= max_pixels:
        return shot, width, height

    keep = max(1, (max_pixels - 1) // max(1, width))  # strictly under the cap
    img = img.crop((0, 0, width, keep))
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    width, height = img.size
    return buf.getvalue(), width, height


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("error: playwright is not importable (pip install playwright)", file=sys.stderr)
        return 1

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                viewport={"width": args.width, "height": 900},
                device_scale_factor=1,  # normal scale, never a 2x capture
                locale="en-US",
            )
            page = context.new_page()
            print(f"opening {args.url} at {args.width}px wide", flush=True)
            page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
            wait_for_readme(page, args.timeout)
            title = page.title()
            print(f"page title: {title!r}", flush=True)
            shot, width, height = capture(page, args.max_pixels)
        finally:
            browser.close()

    out.write_bytes(shot)
    size = out.stat().st_size
    print(f"wrote {out} ({size:,} bytes, {width}x{height} = {width * height:,} pixels)")

    problems = []
    if shot[:8] != b"\x89PNG\r\n\x1a\n":
        problems.append("not a PNG by its first bytes")
    if size > MAX_BYTES:
        problems.append(f"over {MAX_BYTES} bytes")
    if width * height > MAX_PIXELS:
        problems.append(f"over {MAX_PIXELS:,} pixels")
    if size < 100 * 1024:
        problems.append("under 100 KB, which usually means the page did not render")
    if problems:
        for p in problems:
            print(f"FAIL {p}", file=sys.stderr)
        return 1
    print("ok: PNG, within the 8 MB and 16,000,000 pixel caps")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
