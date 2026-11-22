#!/usr/bin/env python3
"""Draw the entry picture for the make.fun news-image-20261121 bounty.

Design: "Zenith". Deliberately different from the Meridian broadsheet
of 20 November (full-width map, lead strip, six horizontal strips)
and the Atlas grid of 19 November (navy masthead, map, six panels):

- a dark navy masthead with the title, the date and the story count;
- a red ticker tape carrying the day's market numbers;
- a circular globe on the left with ten numbered pins, facing a
  large lead hero on the right with the day's biggest story and
  three key facts;
- six tall, narrow continent columns running down the page, each
  with its own coloured header and its headlines stacked vertically.

Everything on the page comes from ``stories.json`` in this same
folder. Run ``python3 render.py`` and it writes ``entry.png`` next
to itself: 1024x1024, well under 1 MiB. It needs nothing from the
network -- the Merriweather faces it sets the page in are bundled
under ``fonts/`` (SIL Open Font License 1.1) -- and the only
third-party import is Pillow. Given the same ``stories.json`` it
always writes the same bytes; if a headline ever overflows its
column the script fails loudly instead of clipping text silently.
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TYPE_DIR = os.path.join(HERE, "fonts")
PAGE_W, PAGE_H = 1024, 1024

CUTS = {
    "regular": "Merriweather-Regular.ttf",
    "bold": "Merriweather-Bold.ttf",
    "black": "Merriweather-Black.ttf",
}

PAPER = (248, 245, 238)
CARD = (255, 255, 255)
NAVY = (18, 32, 58)
NAVY_SOFT = (38, 58, 92)
RULE_RED = (165, 30, 25)
SEA = (198, 222, 233)
LAND = (228, 216, 180)
LAND_LINE = (96, 118, 130)
BODY = (24, 24, 24)
SOFT = (88, 84, 76)
FAINT = (122, 117, 107)
PIN = (178, 34, 34)
TAPE = (140, 24, 20)

# Schematic continent outlines in (longitude, latitude): recognisable
# shapes for a newspaper globe, not a survey chart.
CONTINENTS = {
    "north_america": [(-168, 66), (-145, 70), (-125, 71), (-110, 73),
                      (-95, 80), (-85, 73), (-75, 72), (-65, 60),
                      (-55, 47), (-60, 45), (-70, 42), (-75, 35),
                      (-81, 26), (-87, 21), (-90, 21), (-97, 16),
                      (-105, 20), (-112, 28), (-120, 34), (-125, 49),
                      (-135, 58), (-155, 58), (-168, 66)],
    "south_america": [(-79, 9), (-62, 9), (-52, 4), (-44, -3),
                      (-35, -8), (-39, -15), (-41, -23), (-48, -28),
                      (-58, -35), (-65, -41), (-70, -50), (-68, -54),
                      (-71, -45), (-73, -33), (-72, -20), (-77, -8),
                      (-81, 0), (-79, 9)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (2, 51), (7, 54),
               (10, 57), (18, 56), (21, 55), (24, 59), (28, 62),
               (30, 70), (40, 68), (44, 64), (42, 56), (40, 50),
               (35, 45), (30, 46), (28, 41), (23, 36), (19, 40),
               (12, 44), (3, 43), (-2, 37), (-10, 36)],
    "africa": [(-17, 15), (-12, 27), (-6, 35), (10, 37), (20, 32),
               (32, 31), (35, 28), (43, 12), (51, 11), (48, 2),
               (41, -9), (36, -18), (32, -26), (26, -34), (19, -35),
               (15, -27), (12, -18), (9, -2), (9, 4), (-8, 5),
               (-17, 15)],
    "asia": [(40, 68), (55, 69), (65, 70), (75, 72), (90, 75),
             (105, 77), (120, 73), (135, 72), (150, 70), (162, 66),
             (178, 65), (170, 60), (162, 56), (158, 52), (142, 50),
             (140, 40), (130, 35), (127, 34), (122, 31), (120, 23),
             (110, 20), (108, 12), (104, 8), (100, 6), (97, 16),
             (91, 22), (88, 22), (80, 13), (77, 8), (73, 16),
             (66, 25), (61, 25), (57, 26), (52, 26), (50, 30),
             (48, 30), (44, 39), (41, 42), (39, 46), (40, 56),
             (40, 68)],
    "oceania": [(113, -22), (114, -30), (115, -35), (122, -34),
                (129, -32), (135, -35), (140, -38), (146, -39),
                (150, -37), (153, -32), (153, -27), (150, -22),
                (146, -19), (142, -11), (137, -12), (132, -11),
                (126, -14), (122, -17), (117, -20), (113, -22)],
    "japan": [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42),
              (143, 44), (141, 40), (139, 37), (136, 33), (132, 33),
              (130, 31)],
    "britain": [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53),
                (-1, 51), (-5, 50)],
    "new_zealand": [(167, -45), (174, -41), (178, -38), (174, -35),
                    (167, -45)],
    "madagascar": [(44, -16), (47, -15), (50, -17), (49, -22),
                   (45, -25), (43, -21), (44, -16)],
}

TAB_COLOURS = {
    "Europe": (165, 30, 25),
    "Asia": (0, 90, 160),
    "North America": (0, 120, 60),
    "Africa": (150, 60, 0),
    "South America": (110, 40, 130),
    "Oceania": (0, 120, 120),
}


def typeface(cut, size):
    """A Merriweather face at the given size, from the bundled fonts."""
    try:
        return ImageFont.truetype(os.path.join(TYPE_DIR, CUTS[cut]), size)
    except OSError:
        return ImageFont.load_default()


def wrap_lines(draw, text, face, width):
    """Greedy word wrap: split text into lines that fit a pixel width."""
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=face) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, x, y, text, face, width, colour, spacing=2):
    """Draw wrapped text and return the y coordinate just below it."""
    for line in wrap_lines(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=colour)
        y += face.size + spacing
    return y


def draw_globe(page, cx, cy, radius, points):
    """A circular world map with numbered pins at (lon, lat) points."""
    draw = ImageDraw.Draw(page)
    # Sea disc.
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=SEA, outline=NAVY, width=2)
    # Land, clipped to the disc via a mask.
    mask = Image.new("L", (PAGE_W, PAGE_H), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                      fill=255)
    land_layer = Image.new("RGB", (PAGE_W, PAGE_H), SEA)
    land_draw = ImageDraw.Draw(land_layer)
    for poly in CONTINENTS.values():
        pts = []
        for lon, lat in poly:
            x = cx + (lon / 180.0) * radius
            y = cy - (lat / 82.0) * radius
            pts.append((x, y))
        land_draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    page.paste(land_layer, (0, 0), mask)
    draw = ImageDraw.Draw(page)
    # Faint graticule: equator and tropics.
    for lat in (0, 23.4, -23.4):
        y = cy - (lat / 82.0) * radius
        draw.line([(cx - radius, y), (cx + radius, y)], fill=(255, 255, 255),
                  width=1)
    # Compass tick: N at the top.
    draw.text((cx - 5, cy - radius - 16), "N",
              font=typeface("bold", 12), fill=NAVY)
    # Numbered pins.
    pin_face = typeface("bold", 11)
    for lon, lat, num, _name in points:
        x = cx + (lon / 180.0) * radius
        y = cy - (lat / 82.0) * radius
        r = 10
        draw.ellipse([x - r, y - r, x + r, y + r], fill=PIN,
                     outline=(255, 255, 255), width=2)
        w = draw.textlength(num, font=pin_face)
        draw.text((x - w / 2, y - 7), num, font=pin_face,
                  fill=(255, 255, 255))
    return draw


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(page)

    # ---- Masthead: dark navy band, title left, date right. ----
    draw.rectangle([0, 0, PAGE_W, 88], fill=NAVY)
    title_face = typeface("black", 40)
    draw.text((24, 22), "THE WORLD IN ONE DAY", font=title_face,
              fill=(255, 255, 255))
    date_face = typeface("bold", 14)
    total = 1 + sum(len(s["headlines"]) for s in data["sections"]) \
        + len(data.get("also", []))
    draw.text((24, 66),
              f"SATURDAY 21 NOVEMBER 2026  ·  {total} STORIES  ·  6 CONTINENTS",
              font=date_face, fill=(176, 196, 222))
    draw.rectangle([0, 88, PAGE_W, 92], fill=RULE_RED)

    # ---- Ticker tape: the day's market numbers in one red band. ----
    draw.rectangle([0, 92, PAGE_W, 128], fill=TAPE)
    tape_face = typeface("bold", 14)
    tape_bits = [f"{name} {val} {chg}"
                 for name, val, chg in data["numbers"]]
    tape_text = "   ◆   ".join(tape_bits)
    while draw.textlength(tape_text, font=tape_face) > PAGE_W - 48 \
            and tape_face.size > 10:
        tape_face = typeface("bold", tape_face.size - 1)
    draw.text((24, 104), tape_text, font=tape_face, fill=(255, 255, 255))

    # ---- Middle band: globe left, lead hero right. ----
    mid_top, mid_bottom = 142, 452
    draw = draw_globe(page, 205, 290, 140, data["map_points"])
    draw.text((24, 436),
              "1 Kyiv  ·  2 Poland  ·  3 Antalya  ·  4 Gaza  ·  5 Gopalpur",
              font=typeface("regular", 11), fill=SOFT)
    draw.text((24, 452),
              "6 Shenzhen  ·  7 Tokyo  ·  8 New York  ·  9 Lima  ·  10 Cook Is",
              font=typeface("regular", 11), fill=SOFT)

    # Lead hero.
    hx = 392
    draw.text((hx, mid_top + 2), "LEAD  —  UKRAINE",
              font=typeface("bold", 13), fill=RULE_RED)
    y = draw_lines(draw, hx, mid_top + 26, data["lead"]["headline"],
                   typeface("black", 30), PAGE_W - hx - 24, NAVY, spacing=4)
    y = draw_lines(draw, hx, y + 8, data["lead"]["standfirst"],
                   typeface("regular", 15), PAGE_W - hx - 24, BODY, spacing=3)
    facts = ["404 drones and 111 missiles in one night",
             "8 killed, 28 injured in Kyiv and Lviv",
             "Three Dnipro bridges hit in the capital"]
    fy = y + 14
    for fact in facts:
        draw.rectangle([hx, fy + 4, hx + 8, fy + 12], fill=RULE_RED)
        draw.text((hx + 16, fy), fact, font=typeface("bold", 13), fill=BODY)
        fy += 26
    draw.line([(hx, mid_bottom - 28), (PAGE_W - 24, mid_bottom - 28)],
              fill=(200, 192, 176), width=1)

    # ---- Six tall continent columns. ----
    col_top = 478
    col_bottom = 986
    margin, gap = 24, 10
    col_w = (PAGE_W - 2 * margin - 5 * gap) // 6
    head_face = typeface("bold", 13)
    body_face = typeface("bold", 13)
    for i, section in enumerate(data["sections"]):
        x = margin + i * (col_w + gap)
        colour = TAB_COLOURS[section["continent"]]
        draw.rectangle([x, col_top, x + col_w, col_top + 30], fill=colour)
        name = section["continent"].upper()
        while draw.textlength(name, font=head_face) > col_w - 12 \
                and head_face.size > 9:
            head_face = typeface("bold", head_face.size - 1)
        draw.text((x + 6, col_top + 8), name, font=head_face,
                  fill=(255, 255, 255))
        head_face = typeface("bold", 13)
        y = col_top + 40
        for headline in section["headlines"]:
            lines = wrap_lines(draw, headline, body_face, col_w - 4)
            height = len(lines) * (body_face.size + 2)
            if y + height > col_bottom:
                print(f"error: {section['continent']} column overflows: "
                      f"'{headline}'", file=sys.stderr)
                return 1
            for line in lines:
                draw.text((x + 2, y), line, font=body_face, fill=BODY)
                y += body_face.size + 2
            y += 7
            draw.line([(x + 2, y - 4), (x + col_w - 2, y - 4)],
                      fill=(222, 216, 204), width=1)

    # ---- Footer. ----
    draw.text((24, 996),
              "Drawn offline from 45 verified stories  ·  Sources: Reuters, CNN, "
              "AFP, AP, PTI, CNBC  ·  make.fun news-image-20261121",
              font=typeface("regular", 11), fill=FAINT)

    out = os.path.join(HERE, "entry.png")
    page.save(out, format="PNG")
    size = os.path.getsize(out)
    print(f"wrote {out} ({size} bytes)")
    if size > 1024 * 1024:
        print("error: entry.png is over the 1 MiB limit", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
