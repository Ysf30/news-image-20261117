"""Build the news-image-20261117 v2 front page (1024x1024 PNG, PIL only).

Dense newspaper front page: masthead + dateline, illustrated lead story,
a world-map strip with story dots, a "day in figures" band, a 3x10 grid of
30 short stories (31 stories + 4 ticker items in total), ticker footer.
All text is rendered with PIL so every letter is crisp. Deterministic:
same bytes on every run.
"""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 252, 247)
INK = (17, 17, 17)
RED = (158, 27, 27)
MUTED = (85, 85, 85)
NAVY = (31, 58, 95)
WATER = (120, 160, 200)
BAND = (240, 237, 228)
MAPBG = (232, 240, 248)
LAND = (110, 128, 145)

SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def spaced(text, n=1):
    return (" " * n).join(list(text))


def draw_bridge(d, x0, y0, x1, y1):
    """Compact schematic suspension bridge, broken middle span, over water."""
    d.rectangle([x0, y0, x1, y1], fill=MAPBG)
    deck_y = y0 + 38
    for yy in range(y0 + 54, y1 - 4, 9):
        d.line([x0 + 12, yy, x1 - 12, yy], fill=WATER, width=2)
    for tx in (x0 + 150, x1 - 170):
        d.rectangle([tx, y0 + 6, tx + 14, deck_y], fill=NAVY)
    mid = (x0 + x1) // 2
    d.rectangle([x0 + 18, deck_y, mid - 52, deck_y + 8], fill=NAVY)
    d.rectangle([mid + 52, deck_y, x1 - 18, deck_y + 8], fill=NAVY)
    d.polygon([(mid - 50, deck_y + 6), (mid - 8, deck_y + 6),
               (mid - 20, deck_y + 26), (mid - 54, deck_y + 22)], fill=NAVY)
    d.polygon([(mid + 8, deck_y + 6), (mid + 50, deck_y + 6),
               (mid + 54, deck_y + 22), (mid + 20, deck_y + 26)], fill=NAVY)

    def cable(ax, bx):
        pts = []
        for i in range(21):
            t = i / 20
            x = ax + (bx - ax) * t
            y = y0 + 4 + (deck_y - y0 - 4) * (4 * t * (1 - t)) * 0.9
            pts.append((x, y))
        d.line(pts, fill=NAVY, width=2)
    cable(x0 + 18, x0 + 157)
    cable(x0 + 157, mid - 52)
    cable(mid + 52, x1 - 163)
    cable(x1 - 163, x1 - 18)
    for cx, cy, r in ((mid - 24, y0 + 18, 6), (mid + 6, y0 + 12, 7), (mid + 28, y0 + 20, 5)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(180, 180, 180))


# ---- world map: coarse continent polygons in (lon, lat) ----
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 80), (-80, 73),
     (-70, 62), (-60, 47), (-75, 35), (-80, 25), (-90, 20), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-145, 60), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, -5), (-50, -5), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-80, -20), (-80, -5)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (48, 10), (40, -5), (35, -20), (30, -35), (20, -35),
     (15, -20), (12, -5), (9, 4), (-8, 5), (-15, 10)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 58), (10, 57), (18, 56),
     (21, 54), (28, 45), (23, 40), (19, 42), (12, 44), (3, 43), (-2, 37)],
    [(30, 36), (35, 42), (45, 40), (50, 45), (60, 50), (70, 55), (80, 60),
     (90, 65), (100, 70), (110, 75), (130, 72), (150, 70), (160, 60),
     (155, 50), (140, 40), (130, 35), (120, 30), (110, 20), (105, 10),
     (100, 8), (95, 15), (90, 22), (85, 20), (80, 15), (75, 8), (70, 20),
     (60, 25), (55, 26), (50, 30), (45, 28), (40, 32), (35, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (150, -27),
     (146, -20), (142, -15), (140, -12), (135, -12), (130, -13), (125, -14),
     (120, -20), (114, -22)],
]
LABELS = [
    ("N. AMERICA", -100, 56), ("S. AMERICA", -60, -14), ("EUROPE", 14, 60),
    ("AFRICA", 28, -8), ("ASIA", 88, 56), ("OCEANIA", 134, -24),
]
DOTS = [
    (30.5, 50.5), (56.5, 26.5), (50.6, 26.2), (34.5, 31.5), (139.7, 35.7),
    (2.3, 48.9), (-77, 38.9), (86.1, 55.4), (73.1, 33.7), (45, 12.8),
    (36.8, -1.3), (127, 37.5),
]


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=MAPBG)

    def proj(lon, lat):
        x = x0 + (lon + 170) / 360.0 * (x1 - x0)
        y = y0 + (75 - lat) / 130.0 * (y1 - y0)
        return (x, y)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    f_lab = font(SANS_B, 9)
    for text, lon, lat in LABELS:
        x, y = proj(lon, lat)
        d.text((x - d.textlength(text, font=f_lab) / 2, y - 5), text,
               font=f_lab, fill=(70, 70, 70))
    for lon, lat in DOTS:
        x, y = proj(lon, lat)
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=RED,
                  outline=(255, 255, 255), width=1)


LEAD_KICK = "UKRAINE  •  RUSSIA  —  LEAD STORY"
LEAD_HEAD = "Ukraine strikes Kerch Bridge — span collapses into the strait"
LEAD_SUB = "Russia hits bridges in Kyiv in return as the war's bridge campaign escalates."

FIGURES = [
    ("5,400+", "US measles cases — most since 1991"),
    ("19", "dead in the Kemerovo plane crash"),
    ("1.7M", "displaced in Gaza face winter"),
    ("$120bn", "climate finance a year by 2035"),
]

GRID = [
    ("U.S. – IRAN", "Fourth tanker mined in Strait of Hormuz"),
    ("BAHRAIN", "Iranian drones target US radar base; six shot down"),
    ("U.S. – IRAN", "Trump threatens blockade; Iran to 'pay a price'"),
    ("GAZA", "Allies demand Gaza crossings open for aid"),
    ("JAPAN", "Japan scrambles jets as Russian planes enter airspace"),
    ("FRANCE", "Depardieu drops appeal, pleads guilty in Paris"),
    ("UNITED STATES", "US loses measles-free status after 26 years"),
    ("RUSSIA", "Military plane crashes in Kemerovo; 19 dead"),
    ("MARKETS", "Nvidia posts bumper results after Huang exit"),
    ("SUMMIT", "Trump, Xi and Putin to meet Thursday in Shenzhen"),
    ("UNITED STATES", "Forensic expert: Epstein death was murder"),
    ("YEMEN", "Houthis advance; government troops pull back"),
    ("UKRAINE", "Russian strike on Zaporizhzhia kills 40"),
    ("GAZA", "Israeli strike on Gaza tents kills three"),
    ("CLIMATE", "COP31 draft: faster fossil-fuel phase-out"),
    ("ASIA", "ECO adopts Vision 2035 in Islamabad"),
    ("PAKISTAN", "Petrol and diesel cut by Rs2 a litre"),
    ("CRICKET", "India edge Pakistan in U19 Asia Cup thriller"),
    ("FOOTBALL", "Germany thrash Netherlands 5–0; Wirtz scores twice"),
    ("UKRAINE", "Ukraine holds peace talks with US and Europe"),
    ("UNITED STATES", "Trump says he may meet Kim Jong Un in China"),
    ("EUROPE", "EU–Rwanda migrant return-hub plan sparks row"),
    ("HEALTH", "WHO: Eritrea eliminates trachoma"),
    ("SYRIA", "Syria and EU to restart cooperation deal"),
    ("SOUTH KOREA", "Seoul moves to stop AI-glasses exam cheating"),
    ("BULGARIA", "Gas tanker sinks; all 19 crew rescued"),
    ("FRANCE", "146,000 protest over living costs"),
    ("MOLDOVA", "Moldova closes airspace after Russian drones"),
    ("KENYA", "Kenya opens crypto licensing for $5.4bn market"),
    ("NATO", "Kelluu unveils HALO airship for NATO flank"),
]

TICKER = ("ALSO:  Nvidia board forms export panel; Huang to testify  •  "
          "Kennedy Space Center unveils Aero Test Lab coaster  •  "
          "US soldier held in UK on spying claims  •  "
          "Palestinian woman, 72, shot dead in West Bank")


def build(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([12, 12, W - 13, H - 13], outline=INK, width=4)

    # masthead + dateline
    f_mast = font(SERIF_B, 54)
    t = "THE WORLD TODAY"
    d.text(((W - d.textlength(t, font=f_mast)) / 2, 22), t, font=f_mast, fill=INK)
    d.line([28, 92, W - 28, 92], fill=INK, width=3)
    f_date = font(SANS_B, 22)
    t = spaced("TUESDAY 17 NOVEMBER 2026")
    d.text(((W - d.textlength(t, font=f_date)) / 2, 100), t, font=f_date, fill=RED)
    f_note = font(SERIF, 16)
    t = "Every story below happened, or was first reported, on this day."
    d.text(((W - d.textlength(t, font=f_note)) / 2, 128), t, font=f_note, fill=MUTED)
    d.line([28, 152, W - 28, 152], fill=INK, width=2)

    # ---- lead story ----
    y = 160
    f_kick = font(SANS_B, 16)
    d.text((36, y), spaced(LEAD_KICK, 1), font=f_kick, fill=RED)
    y += 24
    f_head = font(SERIF_B, 36)
    for line in wrap(d, LEAD_HEAD, f_head, W - 72)[:2]:
        d.text((36, y), line, font=f_head, fill=INK)
        y += 42
    f_sub = font(SANS, 18)
    for line in wrap(d, LEAD_SUB, f_sub, W - 72)[:2]:
        d.text((36, y), line, font=f_sub, fill=MUTED)
        y += 24
    draw_bridge(d, 36, y + 6, W - 36, y + 82)
    y += 88

    # ---- world map strip ----
    draw_map(d, 36, y, W - 36, y + 52)
    y += 60

    # ---- day in figures ----
    d.line([28, y, W - 28, y], fill=INK, width=2)
    f_num = font(SERIF_B, 23)
    f_lab = font(SANS, 11)
    col_w = (W - 72) // 4
    for i, (num, lab) in enumerate(FIGURES):
        cx = 36 + i * col_w
        nw = d.textlength(num, font=f_num)
        d.text((cx + (col_w - nw) / 2, y + 5), num, font=f_num, fill=INK)
        for j, line in enumerate(wrap(d, lab, f_lab, col_w - 12)[:1]):
            lw = d.textlength(line, font=f_lab)
            d.text((cx + (col_w - lw) / 2, y + 32), line, font=f_lab, fill=MUTED)
    y += 48
    d.line([28, y, W - 28, y], fill=INK, width=1)

    # ---- dense grid: 3 columns x 10 rows ----
    y += 8
    col_w = (W - 72 - 32) // 3
    row_h = 46
    f_gkick = font(SANS_B, 10)
    f_ghead = font(SERIF_B, 15)
    for i, (kick, head) in enumerate(GRID):
        cx = 36 + (i % 3) * (col_w + 16)
        cy = y + (i // 3) * row_h
        d.line([cx, cy, cx + col_w, cy], fill=(170, 170, 170), width=1)
        d.text((cx, cy + 3), spaced(kick, 1), font=f_gkick, fill=RED)
        yy = cy + 14
        for line in wrap(d, head, f_ghead, col_w)[:2]:
            d.text((cx, yy), line, font=f_ghead, fill=INK)
            yy += 17
    y += 10 * row_h

    # ---- ticker ----
    ty = y + 8
    d.rectangle([28, ty, W - 28, ty + 38], fill=BAND)
    f_tick = font(SANS_B, 14)
    lines = wrap(d, TICKER, f_tick, W - 72)[:2]
    for j, line in enumerate(lines):
        d.text((36, ty + 4 + j * 17), line, font=f_tick, fill=INK)
    y = ty + 38
    assert y <= 1006, f"layout overflow: ends at {y}"
    print("layout ends at", y, "stories:", 1 + len(GRID), "+ ticker")

    img.save(path, "PNG", optimize=True)
    print("saved", path)


if __name__ == "__main__":
    build("entry.png")
