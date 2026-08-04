#!/usr/bin/env python3
"""Generate repository SVG figures and social preview from frozen data."""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
BLUE = "#1558B1"
BLACK = "#111827"
GRAY = "#475569"
LIGHT = "#E8EFF9"
BORDER = "#CBD5E1"
WHITE = "#FFFFFF"


def svg_text(x: float, y: float, text: str, size: int, weight: int = 400, anchor: str = "start", fill: str = BLACK) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">'
        f'{escape(text)}</text>'
    )


def write_architecture_svg() -> None:
    width, height = 1600, 900
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Four web GTM and server-side GTM benchmark architectures</title>',
        '<desc id="desc">Comparison of control, browser-heavy web GTM, proxy-only server-side GTM, and consolidated server-side GTM flows.</desc>',
        f'<rect width="{width}" height="{height}" fill="{WHITE}"/>',
        svg_text(80, 85, "Architecture, not the hostname, determines browser cost", 38, 700),
        svg_text(80, 125, "The fixture is identical in every run; only the measurement flow changes.", 20, 400, fill=GRAY),
    ]
    cards = [
        ("1", "Control", ["Page + hero image", "No measurement JavaScript", "0 event requests"], "2 browser requests"),
        ("2", "Web GTM-style", ["1 browser container", "4 synthetic vendor libraries", "4 direct event requests"], "11 browser requests"),
        ("3", "sGTM proxy-only", ["Same 5 browser scripts", "Same 4 browser events", "Only endpoint changes"], "11 browser requests"),
        ("4", "sGTM consolidated", ["1 small dispatcher", "1 first-party event", "Server fans out to 4 destinations"], "4 browser requests"),
    ]
    x_positions = [70, 455, 840, 1225]
    for index, (number, title, lines, result) in enumerate(cards):
        x = x_positions[index]
        y = 190
        card_w = 305
        card_h = 570
        parts.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="24" fill="{WHITE}" stroke="{BORDER}" stroke-width="2"/>')
        parts.append(f'<circle cx="{x+42}" cy="{y+48}" r="25" fill="{BLUE}"/>')
        parts.append(svg_text(x+42, y+56, number, 22, 700, "middle", WHITE))
        parts.append(svg_text(x+78, y+57, title, 24, 700))
        # browser boundary
        parts.append(f'<rect x="{x+24}" y="{y+105}" width="{card_w-48}" height="220" rx="16" fill="{LIGHT}"/>')
        parts.append(svg_text(x+42, y+140, "BROWSER", 15, 700, fill=BLUE))
        yy = y + 185
        for line in lines:
            parts.append(f'<circle cx="{x+44}" cy="{yy-7}" r="5" fill="{BLUE}"/>')
            parts.append(svg_text(x+60, yy, line, 18, 400))
            yy += 52
        # Arrow
        parts.append(f'<line x1="{x+card_w/2}" y1="{y+342}" x2="{x+card_w/2}" y2="{y+405}" stroke="{BLACK}" stroke-width="3"/>')
        parts.append(f'<polygon points="{x+card_w/2-8},{y+398} {x+card_w/2+8},{y+398} {x+card_w/2},{y+414}" fill="{BLACK}"/>')
        # server block
        server_label = "No measurement layer" if index == 0 else ("Vendor endpoints" if index == 1 else ("First-party proxy" if index == 2 else "Server validation + fan-out"))
        parts.append(f'<rect x="{x+24}" y="{y+430}" width="{card_w-48}" height="72" rx="16" fill="{BLACK}"/>')
        parts.append(svg_text(x+card_w/2, y+474, server_label, 17, 700, "middle", WHITE))
        parts.append(f'<line x1="{x+24}" y1="{y+528}" x2="{x+card_w-24}" y2="{y+528}" stroke="{BORDER}" stroke-width="2"/>')
        parts.append(svg_text(x+card_w/2, y+575, result, 22, 700, "middle", BLUE))
        deliveries = ["0 logical deliveries", "4 logical deliveries", "4 logical deliveries", "4 logical deliveries"][index]
        parts.append(svg_text(x+card_w/2, y+615, deliveries, 17, 400, "middle", GRAY))
    parts.append(svg_text(80, 840, "Synthetic benchmark • 15 cold loads per variant • Median values • No live vendor endpoints", 18, 400, fill=GRAY))
    parts.append('</svg>')
    (ASSETS / "benchmark-architecture.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_results_svg(summary: dict) -> None:
    width, height = 1600, 900
    variants = [
        ("Control", "control"),
        ("Web GTM-style", "web_gtm"),
        ("sGTM proxy-only", "sgtm_proxy_only"),
        ("sGTM consolidated", "sgtm_consolidated"),
    ]
    metrics = [
        ("Browser requests", "request_count", 12, ""),
        ("JavaScript transfer", "js_transfer_bytes", 150000, " KB"),
        ("Largest Contentful Paint", "lcp", 2400, " ms"),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Median benchmark result comparison</title>',
        '<desc id="desc">Browser requests, JavaScript transfer, and LCP for control, web GTM-style, proxy-only sGTM, and consolidated sGTM variants.</desc>',
        f'<rect width="{width}" height="{height}" fill="{WHITE}"/>',
        svg_text(80, 80, "Proxying changed the endpoint; consolidation changed the workload", 38, 700),
        svg_text(80, 120, "Median values from 15 randomized cold loads per variant.", 20, 400, fill=GRAY),
    ]
    panel_x = [70, 550, 1030]
    for panel_index, (title, field, max_value, suffix) in enumerate(metrics):
        x = panel_x[panel_index]
        y = 180
        w = 430
        h = 590
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="{WHITE}" stroke="{BORDER}" stroke-width="2"/>')
        parts.append(svg_text(x+28, y+48, title, 24, 700))
        chart_y = y + 95
        for i, (label, key) in enumerate(variants):
            value = float(summary["variants"][key][field]["median"])
            yy = chart_y + i * 112
            parts.append(svg_text(x+28, yy+20, label, 17, 600))
            bar_x = x + 28
            bar_y = yy + 38
            bar_w = 270
            parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="28" rx="8" fill="{LIGHT}"/>')
            filled = max(2, bar_w * value / max_value)
            fill = BLUE if key == "sgtm_consolidated" else BLACK
            if key == "control":
                fill = GRAY
            parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{filled:.1f}" height="28" rx="8" fill="{fill}"/>')
            if field == "js_transfer_bytes":
                display = f"{value/1024:.1f}{suffix}"
            elif field == "request_count":
                display = f"{value:.0f}"
            else:
                display = f"{value:,.0f}{suffix}"
            parts.append(svg_text(x+w-28, yy+61, display, 17, 700, "end"))
        parts.append(svg_text(x+28, y+h-32, "Lower is better for this fixture", 15, 400, fill=GRAY))
    parts.append(f'<rect x="70" y="800" width="1390" height="56" rx="14" fill="{LIGHT}"/>')
    parts.append(svg_text(765, 836, "Consolidated vs web GTM-style: −63.6% requests • −88.3% JS transfer • −29.4% LCP", 21, 700, "middle", BLUE))
    parts.append('</svg>')
    (ASSETS / "benchmark-results.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def write_social_preview() -> None:
    image = Image.new("RGB", (1280, 640), WHITE)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 28, 640), fill=BLUE)
    draw.rounded_rectangle((820, 80, 1190, 560), radius=28, fill=LIGHT)
    # Mini architecture graphic.
    for i, bars in enumerate([(5, 4), (5, 4), (1, 1)]):
        yy = 150 + i * 135
        draw.rounded_rectangle((875, yy, 1135, yy + 88), radius=16, fill=WHITE, outline=BORDER, width=2)
        scripts, requests = bars
        draw.text((900, yy + 17), f"{scripts} browser script{'s' if scripts != 1 else ''}", font=load_font(22, True), fill=BLACK)
        draw.text((900, yy + 50), f"{requests} event request{'s' if requests != 1 else ''}", font=load_font(18), fill=GRAY)
        if i == 2:
            draw.rectangle((875, yy, 885, yy + 88), fill=BLUE)
    draw.text((84, 72), "METRICFIXER RESEARCH", font=load_font(22, True), fill=BLUE)
    title_font = load_font(56, True)
    title = "Web GTM vs Server-Side GTM"
    y = 135
    for line in wrap_text(draw, title, title_font, 650):
        draw.text((84, y), line, font=title_font, fill=BLACK)
        y += 68
    draw.text((84, y + 15), "Reproducible benchmark", font=load_font(34, True), fill=BLUE)
    takeaway = "A proxy changes the endpoint. A consolidated architecture removes browser work."
    yy = y + 90
    for line in wrap_text(draw, takeaway, load_font(26), 650):
        draw.text((84, yy), line, font=load_font(26), fill=GRAY)
        yy += 38
    draw.text((84, 555), "60 cold loads • raw data • Playwright runner • documented limits", font=load_font(20), fill=BLACK)
    image.save(ASSETS / "social-preview.png", optimize=True)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    summary = json.loads((ROOT / "data/processed/benchmark_summary.json").read_text(encoding="utf-8"))
    write_architecture_svg()
    write_results_svg(summary)
    write_social_preview()
    (ASSETS / "ALT_TEXT.md").write_text(
        "# Asset alt text\n\n"
        "- `benchmark-architecture.svg`: Four-column diagram comparing the control, web GTM-style, proxy-only server-side GTM, and consolidated server-side GTM benchmark flows.\n"
        "- `benchmark-results.svg`: Bar-chart comparison of median browser requests, JavaScript transfer, and LCP across the four benchmark variants.\n"
        "- `social-preview.png`: Repository preview stating that proxying changes the endpoint while consolidation removes browser work.\n",
        encoding="utf-8",
    )
    print("Generated repository assets.")


if __name__ == "__main__":
    main()
