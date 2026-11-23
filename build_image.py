#!/usr/bin/env python3
"""news-image-20261122 v2 — THE WORLD IN ONE DAY: Sunday 22 November 2026.

Deterministic broadsheet front page, 1024x1024 PNG. Stdlib + PIL only.
No network, no randomness, no timestamps. Drawn at 2x and downscaled
with LANCZOS. 37 stories: 3 leads + 13 cards + 21 briefs, 7 regions.
Every lead carries a certainty tag (REPORTED / CLAIM / FORECAST) and the
briefs use the same labels.
"""
import os
from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersampling factor
W, H = 1024 * S, 1024 * S  # canvas at 2x

PAPER = (247, 243, 232)
NAVY = (20, 38, 74)
MAPNAVY = (13, 27, 52)
RED = (163, 30, 34)
INK = (26, 26, 26)
GREY = (107, 107, 107)
CREAM = (247, 243, 232)
LIGHT = (233, 227, 210)
GOLD = (176, 141, 58)
LAND = (126, 156, 196)
PIN = (224, 49, 49)

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    """size in final (1x) px; scaled internally."""
    return ImageFont.truetype(FD + name, int(size * S))


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def tw(d, text, fnt):
    """text width in 1x px."""
    return d.textlength(text, font=fnt) / S


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(d, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, max_w, fill, lh, max_lines=None):
    lines = wrap(d, text, fnt, max_w)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and tw(d, lines[-1] + "…", fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        if lines:
            lines[-1] = lines[-1] + "…"
    for ln in lines:
        d.text((x * S, y * S), ln, font=fnt, fill=fill)
        y += lh
    return y


def fit_font(d, text, fn, size, max_w, min_size=5.5):
    f = fn(size)
    while tw(d, text, f) > max_w and size > min_size:
        size -= 0.5
        f = fn(size)
    return f


def rect(d, x0, y0, x1, y1, **kw):
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], **kw)


def line(d, pts, **kw):
    d.line([(x * S, y * S) for x, y in pts], **kw)


def ellipse(d, x0, y0, x1, y1, **kw):
    d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], **kw)


def poly(d, pts, **kw):
    d.polygon([(x * S, y * S) for x, y in pts], **kw)


def txt(d, x, y, s, fnt, fill=INK):
    d.text((x * S, y * S), s, font=fnt, fill=fill)


def txt_c(d, cx, y, s, fnt, fill=INK):
    d.text(((cx - tw(d, s, fnt) / 2) * S, y * S), s, font=fnt, fill=fill)


def txt_r(d, xr, y, s, fnt, fill=INK):
    d.text(((xr - tw(d, s, fnt)) * S, y * S), s, font=fnt, fill=fill)


# ---------------------------------------------------------------- stories
# Leads: (num, kicker, tag, region, place, headline, body, source, scene)
LEADS = [
    (1, "COP31: NO DEAL", "REPORTED", "EUROPE", "ANTALYA, TÜRKIYE · CLIMATE",
     "COP31 collapses: no deal in Antalya",
     "The final text — 94 paragraphs, no fossil-fuel mention, the $120bn "
     "adaptation target dropped — is rejected by the EU, UK, Norway, "
     "Panama and island states.",
     "Reuters · BBC · AP", "cop"),
    (2, "CLAIM VS DENIAL", "CLAIM", "MIDDLE EAST", "MANAMA, BAHRAIN · IRAN",
     "Iran claims strikes on US bases in Bahrain",
     "The IRGC says its missiles hit two US Patriot radars at Al-Riffa "
     "and Awali. Bahrain says an industrial site burned, no casualties; "
     "the US denies any damage to its forces.",
     "Al Jazeera · Reuters · IRGC statement", "radar"),
    (3, "186 DRONES OVERNIGHT", "REPORTED", "EUROPE", "KYIV REGION, UKRAINE · WAR",
     "Russia fires 186 drones; a Kyiv-region block is destroyed",
     "Air defences down or jam 161 of 186 strike drones, 72 of them "
     "jet-powered. A drone destroys a five-storey block in Dymer: "
     "five dead, 14 unaccounted for.",
     "Ukrainian Air Force · Reuters", "drones"),
]

# Cards: (num, region, place, headline, body, source, scene)
CARDS = [
    (4, "ASIA-PACIFIC", "HONG KONG · ELECTION",
     "Hong Kong elects its Election Committee",
     "856 candidates, 723 seats in 31 subsectors; 5,640 voters cast "
     "ballots, turnout 98.79%.", "info.gov.hk", "ballot"),
    (5, "OCEANIA", "WELLINGTON · CRICKET",
     "India declare 720/9 — a record in New Zealand",
     "Rahul 136, Pant 128, Gill 98: the highest Test total ever on New "
     "Zealand soil, 352 ahead.", "ESPNcricinfo", "cricket"),
    (6, "AMERICAS", "LAS VEGAS · FORMULA 1",
     "Verstappen takes the Las Vegas GP",
     "35 lead changes and 352 overtakes in 50 laps; Verstappen holds "
     "off Norris by 0.639s, Piastri third.", "Formula1.com", "f1"),
    (7, "AMERICAS", "SAN ANTONIO · NBA",
     "Wembanyama scores 50 as the Spurs roll on",
     "50 points and 19 rebounds in a 114–91 win over New Orleans — "
     "his first 50-point night.", "Reuters", "nba"),
    (8, "EUROPE", "GULF OF FINLAND · SEA",
     "Russian cargo ship Sparta II still burning",
     "Hit by drones on Saturday, the ship drifts into Finnish waters; "
     "16 crew evacuated. Towing begins Sunday.", "Reuters", "ship"),
    (9, "MIDDLE EAST", "TEHRAN · ENERGY",
     "Iran begins rationing electricity",
     "Rolling cuts of up to two hours a day start Sunday as war damage "
     "to gas plants bites. A hard winter looms.", "RFE/RL", "power"),
    (10, "AMERICAS", "BRASÍLIA · HEALTH",
     "Bolsonaro in intensive care",
     "The ex-president, 71, is stable with a bowel obstruction at DF "
     "Star hospital, breathing on his own.", "Reuters", "medic"),
    (11, "AMERICAS", "WASHINGTON · CYBER",
     "FBI probes apparent hack of its crime database",
     "Intruders are suspected of reaching the NCIC, the warrant-check "
     "system. Scope unknown; Trump: “not good”.", "AP", "cyber"),
    (12, "EUROPE", "BRUSSELS · TRAVEL",
     "Belgian controllers join Monday strike",
     "All Brussels flights 07:00–21:00 are cancelled as controllers "
     "join a national strike: 429 flights hit.", "AFP", "plane"),
    (13, "ASIA-PACIFIC", "MANIPUR · POISONING",
     "Toxic-liquor toll reaches 19 in Manipur",
     "19 dead and about 600 in hospital in Chandel after suspected "
     "spurious liquor; six arrested.", "The Hindu", "bottle"),
    (14, "ASIA-PACIFIC", "CIKANDE · FIRE",
     "Candy-factory fire: 3 dead, 36 missing",
     "Fire sweeps a candy factory in Cikande, Indonesia; three dead "
     "and 36 workers still missing.", "Reuters", "factory"),
    (15, "AMERICAS", "JUNÍN · QUAKE",
     "Peru quake toll: 1 dead, 16 hurt",
     "The M6.7 quake in Junín left 152 homes uninhabitable; the toll "
     "was updated on Sunday.", "INDECI", "quake"),
    (16, "EUROPE", "SPACE · ESA–JAXA",
     "BepiColombo reaches Mercury",
     "After an 8-year flight the ESA–JAXA probe enters Mercury's "
     "orbit; a thruster glitch is reported.", "AP", "orbit"),
]

# Briefs: (num, region, text, source, tag)
BRIEFS = [
    (17, "EUROPE", "Estonia to shut five Russia border crossings from 1 Dec", "Reuters", "REPORTED"),
    (18, "EUROPE", "Denmark expels Russian defence attaché over alleged plot", "Guardian", "REPORTED"),
    (19, "ASIA-PACIFIC", "Nepal PM Shah lands in Delhi on first state visit", "IANS", "REPORTED"),
    (20, "ASIA-PACIFIC", "Chinese bomber turns back 170 km off the Philippines", "AP", "REPORTED"),
    (21, "ASIA-PACIFIC", "M5.9 quake strikes 898 km off Palawan", "EMSC", "REPORTED"),
    (22, "ASIA-PACIFIC", "Japan poll: record 92% feel friendly to South Korea", "Yonhap", "REPORTED"),
    (23, "ASIA-PACIFIC", "Taiwan live-fire drills begin", "Focus Taiwan", "REPORTED"),
    (24, "AFRICA", "Somalia expels UAE ambassador, recalls its own", "Wires", "REPORTED"),
    (25, "AFRICA", "RSF accused of killing civilians in West Kordofan", "Claims", "CLAIM"),
    (26, "AFRICA", "Kenya discharges its last Ebola patient", "Wires", "REPORTED"),
    (27, "OCEANIA", "Marles rejects a US report on AUKUS subs", "ABC", "REPORTED"),
    (28, "OCEANIA", "Melbourne marks 70 years since the 1956 Olympics opened", "ABC", "REPORTED"),
    (29, "MIDDLE EAST", "Hamas seeks urgent talks after aid-vehicle strike", "Al Jazeera", "REPORTED"),
    (30, "MIDDLE EAST", "Trump seeks a ‘permanent’ Iran deal; talks go on", "Al Jazeera", "REPORTED"),
    (31, "MIDDLE EAST", "Eisenkot invites Likud to coalition talks", "Straits Times", "REPORTED"),
    (32, "MIDDLE EAST", "Lebanon: Aoun demands Israeli withdrawal", "Al Jazeera", "REPORTED"),
    (33, "WORLD", "Nvidia faces SEC accounting probe; Huang to testify", "NYT", "REPORTED"),
    (34, "WORLD", "Bitcoin back above $60,000 after Saturday's flush", "Market data", "REPORTED"),
    (35, "WORLD", "Gold holds near $3,553", "Reuters", "REPORTED"),
    (36, "EUROPE", "Monday's Brussels strike grounds 429 flights", "AFP", "FORECAST"),
    (37, "ASIA-PACIFIC", "Nepal PM Shah meets Modi on Monday in Delhi", "IANS", "FORECAST"),
]

# Region tally, counted from the lists above (BepiColombo is an ESA-led
# mission, counted under Europe): sums to 37.
TALLY = [("EUROPE", 8, (38, 84, 143)), ("ASIA-PACIFIC", 9, (176, 141, 58)),
         ("MIDDLE EAST", 6, (163, 30, 34)), ("AMERICAS", 5, (58, 124, 68)),
         ("AFRICA", 3, (146, 96, 36)), ("OCEANIA", 3, (94, 62, 128)),
         ("WORLD", 3, (90, 90, 90))]

STATS = [("186", "drones fired overnight"), ("161", "downed or suppressed"),
         ("0", "fossil-fuel mentions in text"), ("856", "candidates in Hong Kong"),
         ("720/9", "India's record Test total"), ("50", "Wembanyama points")]

TIMELINE = [("02:00", "COP31 final text out"), ("03:00", "objections close"),
            ("06:00", "approval plenary"), ("08:00", "Kyiv: 161 of 186 drones downed"),
            ("10:00", "Hong Kong polls close")]

DATECHECK = ("The Peru quake itself struck Fri 20 Nov (toll updated Sun) · "
             "‘El Chapo Isidro’ captured Fri night · COP31 carbon-market "
             "decisions adopted Fri · Nvidia's 14% share fall was Fri 20 Nov.")

LEGEND = ("REPORTED = carried by the day's wires · CLAIM = one side's "
          "account · FORECAST = still to happen")

# Map pins: story num -> (lat, lon, jitter_x, jitter_y) in 1x px
PINS = {
    1: (36.88, 30.70, 0, 0), 2: (26.23, 50.59, 3, 2), 3: (50.45, 30.52, 0, 0),
    4: (22.32, 114.17, 0, 0), 5: (-41.29, 174.78, 0, 0), 6: (36.17, -115.14, 0, 0),
    7: (29.42, -98.49, 0, 0), 8: (59.90, 25.00, -4, -3), 9: (35.69, 51.39, 4, 0),
    10: (-15.79, -47.88, 0, 0), 11: (38.90, -77.04, 0, 0), 12: (50.85, 4.35, -3, 3),
    13: (24.80, 93.94, 0, 0), 14: (-6.28, 106.45, 0, 0), 15: (-11.54, -75.21, 0, 0),
    16: (49.87, 8.65, 4, -4), 17: (59.44, 24.75, 5, 3), 18: (55.68, 12.57, 0, 0),
    19: (28.61, 77.21, -4, -2), 20: (14.60, 120.90, 0, 0), 21: (10.50, 118.50, 3, 3),
    22: (35.68, 139.69, 0, 0), 23: (25.03, 121.57, 4, 4), 24: (2.05, 45.32, 0, 0),
    25: (11.80, 29.80, 0, 0), 26: (-1.29, 36.82, 0, 0), 27: (-35.28, 149.13, 0, 0),
    28: (-37.81, 144.96, -4, 3), 29: (31.50, 34.47, -5, 2), 30: (25.28, 51.53, 6, 5),
    31: (31.77, 35.21, 1, -4), 32: (33.89, 35.50, -4, -5), 33: (40.71, -74.00, 0, -3),
    34: (40.00, -73.50, 4, 4), 35: (51.50, -0.13, 3, -3), 36: (50.85, 4.35, 5, -4),
    37: (28.61, 77.21, 5, 4),
}

# Dot-matrix world map: row -> list of (first, last) land columns, 92 cols.
MAP_ROWS = {
    0: [(8, 14), (34, 38), (60, 66), (72, 80)],
    1: [(6, 16), (33, 39), (56, 84)],
    2: [(5, 18), (33, 40), (54, 86)],
    3: [(4, 20), (34, 40), (52, 88)],
    4: [(3, 22), (35, 39), (50, 90)],
    5: [(2, 24), (35, 38), (48, 90)],
    6: [(2, 25), (35, 37), (46, 90)],
    7: [(3, 26), (35, 36), (45, 90)],
    8: [(4, 27), (34, 35), (45, 89)],
    9: [(5, 28), (44, 45), (46, 88)],
    10: [(6, 29), (44, 45), (46, 86)],
    11: [(7, 30), (44, 45), (46, 84)],
    12: [(8, 30), (45, 82)],
    13: [(9, 30), (46, 80), (83, 85)],
    14: [(10, 30), (46, 78), (82, 85)],
    15: [(10, 29), (45, 50), (51, 76), (79, 84)],
    16: [(11, 28), (43, 74), (75, 79)],
    17: [(11, 26), (43, 78)],
    18: [(12, 24), (44, 75)],
    19: [(14, 19), (44, 74)],
    20: [(15, 20), (45, 73)],
    21: [(17, 20), (45, 72)],
    22: [(18, 20), (46, 71)],
    23: [(19, 28), (46, 57), (70, 73)],
    24: [(23, 30), (46, 57), (68, 71), (73, 78)],
    25: [(23, 31), (47, 56), (69, 79)],
    26: [(24, 32), (47, 56), (72, 80)],
    27: [(24, 33), (47, 55), (73, 80)],
    28: [(25, 34), (47, 55), (74, 80)],
    29: [(25, 34), (47, 55)],
    30: [(25, 33), (48, 54)],
    31: [(25, 33), (48, 54), (74, 84)],
    32: [(26, 33), (48, 54), (73, 85)],
    33: [(26, 32), (48, 53), (73, 86)],
    34: [(26, 32), (48, 53), (74, 86)],
    35: [(27, 31), (49, 52), (74, 85)],
    36: [(27, 31), (49, 52), (75, 84)],
    37: [(27, 30), (49, 51), (76, 83)],
    38: [(27, 30), (49, 51), (77, 82)],
    39: [(27, 29), (78, 81)],
    40: [(27, 29), (89, 90)],
    41: [(27, 28), (88, 89)],
    42: [(27, 28), (87, 88)],
    43: [(27, 28)],
    44: [(27, 28)],
    45: [(27, 27)],
}


# ---------------------------------------------------------------- scenes
def scene_base(d, x, y, w, h, top, bot):
    """vertical gradient band."""
    for i in range(int(h * S)):
        t = i / max(1, int(h * S) - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x * S, y * S + i), ((x + w) * S, y * S + i)], fill=c)


def sc_cop(d, x, y, w, h):
    scene_base(d, x, y, w, h, (240, 150, 80), (120, 50, 90))
    ellipse(d, x + w * 0.62, y + h * 0.16, x + w * 0.80, y + h * 0.62, fill=(250, 214, 120))
    # skyline silhouette
    sil = (30, 22, 44)
    bx = x + 4
    for bw, bh in [(26, 22), (16, 34), (22, 18), (12, 42), (20, 26), (15, 31),
                   (24, 20), (14, 38), (20, 24), (16, 29), (22, 19)]:
        rect(d, bx, y + h - bh, bx + bw, y + h, fill=sil)
        bx += bw + 3
    # cracked "deal" document
    dx, dy = x + w * 0.08, y + h * 0.14
    rect(d, dx, dy, dx + 34, dy + 44, fill=(245, 240, 225))
    for i in range(4):
        line(d, [(dx + 5, dy + 9 + i * 8), (dx + 29, dy + 9 + i * 8)], fill=(120, 120, 120), width=1)
    line(d, [(dx + 17, dy), (dx + 12, dy + 14), (dx + 20, dy + 26), (dx + 14, dy + 44)],
         fill=RED, width=2)


def sc_radar(d, x, y, w, h):
    scene_base(d, x, y, w, h, (16, 26, 54), (44, 40, 74))
    sil = (10, 12, 24)
    rect(d, x, y + h - 12, x + w, y + h, fill=sil)
    # radar dish on a mast
    cx, cy = x + w * 0.30, y + h - 12
    line(d, [(cx, cy), (cx, cy - 30)], fill=(200, 205, 220), width=2)
    d.arc([(cx - 20) * S, (cy - 52) * S, (cx + 20) * S, (cy - 12) * S],
          start=300, end=120, fill=(220, 225, 240), width=3)
    line(d, [(cx, cy - 30), (cx + 13, cy - 41)], fill=(220, 225, 240), width=2)
    # missile arcs
    for off, col in [(0, (250, 170, 90)), (14, (250, 120, 90))]:
        pts = []
        for i in range(21):
            t = i / 20
            px = x + w * 0.52 + t * w * 0.36
            py = y + 8 + off * 0.4 + (t * t) * (h - 34) - t * 6
            pts.append((px, py))
        line(d, pts, fill=col, width=2)
    # starburst at impact
    ix, iy = x + w * 0.90, y + h - 16
    for ang in range(0, 360, 45):
        import math
        ex = ix + 11 * math.cos(math.radians(ang))
        ey = iy + 11 * math.sin(math.radians(ang))
        line(d, [(ix, iy), (ex, ey)], fill=(255, 190, 80), width=2)
    ellipse(d, ix - 4, iy - 4, ix + 4, iy + 4, fill=(255, 220, 140))


def sc_drones(d, x, y, w, h):
    scene_base(d, x, y, w, h, (14, 22, 46), (52, 44, 66))
    ellipse(d, x + w * 0.84, y + 6, x + w * 0.94, y + 6 + (w * 0.10), fill=(232, 232, 210))
    # apartment block with a destroyed corner
    bx, by, bw, bh = x + w * 0.58, y + h * 0.30, w * 0.36, h * 0.70
    rect(d, bx, by, bx + bw, y + h, fill=(38, 36, 52))
    poly(d, [(bx + bw * 0.55, by), (bx + bw, by), (bx + bw, by + bh * 0.42),
             (bx + bw * 0.78, by + bh * 0.30), (bx + bw * 0.66, by + bh * 0.46),
             (bx + bw * 0.55, by + bh * 0.22)], fill=(14, 22, 46))
    for r in range(3):
        for c in range(4):
            wx = bx + 6 + c * (bw - 12) / 4
            wy = by + 7 + r * (bh - 12) / 3
            if (r * 4 + c) % 3 != 1:
                rect(d, wx, wy, wx + 6, wy + 5, fill=(250, 205, 110))
    rect(d, bx + bw * 0.55, y + h - 6, bx + bw, y + h, fill=(70, 60, 66))  # rubble
    # drones
    for dx, dy, sc in [(0.10, 0.20, 1.0), (0.26, 0.38, 0.75), (0.40, 0.14, 0.6)]:
        cx, cy = x + w * dx, y + h * dy
        r = 7 * sc
        line(d, [(cx - r, cy - r * 0.5), (cx + r, cy + r * 0.5)], fill=(210, 215, 230), width=2)
        line(d, [(cx - r, cy + r * 0.5), (cx + r, cy - r * 0.5)], fill=(210, 215, 230), width=2)
        ellipse(d, cx - 2, cy - 2, cx + 2, cy + 2, fill=(255, 90, 90))


def card_scene(d, kind, x, y, w, h):
    if kind == "ballot":
        scene_base(d, x, y, w, h, (150, 40, 44), (90, 26, 40))
        rect(d, x + w / 2 - 17, y + h - 15, x + w / 2 + 17, y + h - 3, fill=(240, 238, 230))
        rect(d, x + w / 2 - 10, y + h - 12, x + w / 2 + 10, y + h - 10, fill=(60, 60, 60))
        rect(d, x + w / 2 - 8, y + 4, x + w / 2 + 10, y + h - 13, fill=(248, 246, 240))
        line(d, [(x + w / 2 - 3, y + h - 20), (x + w / 2 + 2, y + h - 15),
                 (x + w / 2 + 9, y + h - 24)], fill=RED, width=2)
    elif kind == "cricket":
        scene_base(d, x, y, w, h, (70, 140, 70), (40, 96, 44))
        rect(d, x + w * 0.44, y + 4, x + w * 0.56, y + h - 3, fill=(226, 205, 150))
        ellipse(d, x + w * 0.66, y + h * 0.30, x + w * 0.66 + 9, y + h * 0.30 + 9, fill=(178, 30, 40))
        line(d, [(x + w * 0.24, y + h - 4), (x + w * 0.30, y + 6)], fill=(120, 84, 40), width=3)
    elif kind == "f1":
        scene_base(d, x, y, w, h, (40, 40, 52), (18, 18, 26))
        for r in range(2):
            for c in range(8):
                if (r + c) % 2 == 0:
                    rect(d, x + 4 + c * 7, y + 3 + r * 7, x + 11 + c * 7, y + 10 + r * 7,
                         fill=(235, 235, 235))
        poly(d, [(x + w * 0.38, y + h - 6), (x + w * 0.44, y + h - 14),
                 (x + w * 0.66, y + h - 14), (x + w * 0.74, y + h - 6)], fill=(178, 30, 40))
        ellipse(d, x + w * 0.44, y + h - 8, x + w * 0.44 + 8, y + h, fill=(12, 12, 12))
        ellipse(d, x + w * 0.64, y + h - 8, x + w * 0.64 + 8, y + h, fill=(12, 12, 12))
    elif kind == "nba":
        scene_base(d, x, y, w, h, (196, 108, 40), (140, 66, 26))
        ellipse(d, x + w * 0.16, y + h * 0.22, x + w * 0.16 + 17, y + h * 0.22 + 17, fill=(226, 110, 40),
                outline=(90, 40, 10), width=1)
        rect(d, x + w * 0.60, y + 4, x + w * 0.86, y + 9, fill=(240, 240, 240))
        ellipse(d, x + w * 0.63, y + 8, x + w * 0.83, y + 17, outline=(200, 40, 40), width=2)
        line(d, [(x + w * 0.66, y + 16), (x + w * 0.68, y + h - 4)], fill=(240, 240, 240), width=1)
        line(d, [(x + w * 0.80, y + 16), (x + w * 0.78, y + h - 4)], fill=(240, 240, 240), width=1)
    elif kind == "ship":
        scene_base(d, x, y, w, h, (56, 84, 110), (26, 44, 64))
        poly(d, [(x + w * 0.18, y + h - 9), (x + w * 0.80, y + h - 9),
                 (x + w * 0.74, y + h - 3), (x + w * 0.24, y + h - 3)], fill=(24, 24, 30))
        rect(d, x + w * 0.34, y + h - 16, x + w * 0.58, y + h - 9, fill=(120, 40, 40))
        rect(d, x + w * 0.60, y + h - 20, x + w * 0.66, y + h - 9, fill=(200, 200, 200))
        poly(d, [(x + w * 0.44, y + h - 16), (x + w * 0.50, y + h - 27),
                 (x + w * 0.56, y + h - 16)], fill=(250, 130, 40))
        poly(d, [(x + w * 0.47, y + h - 16), (x + w * 0.50, y + h - 22),
                 (x + w * 0.53, y + h - 16)], fill=(255, 200, 80))
        ellipse(d, x + w * 0.40, y + 2, x + w * 0.62, y + 9, fill=(90, 90, 96))
    elif kind == "power":
        scene_base(d, x, y, w, h, (26, 32, 54), (14, 18, 34))
        cx = x + w * 0.34
        line(d, [(cx - 12, y + h - 3), (cx, y + 6), (cx + 12, y + h - 3)], fill=(170, 178, 200), width=2)
        line(d, [(cx - 9, y + 14), (cx + 9, y + 14)], fill=(170, 178, 200), width=2)
        line(d, [(cx - 16, y + 10), (cx + 16, y + 10)], fill=(170, 178, 200), width=1)
        poly(d, [(x + w * 0.62, y + 3), (x + w * 0.54, y + h * 0.55),
                 (x + w * 0.62, y + h * 0.55), (x + w * 0.58, y + h - 4)],
             fill=(255, 205, 60))
    elif kind == "medic":
        scene_base(d, x, y, w, h, (226, 230, 234), (188, 196, 204))
        rect(d, x + w / 2 - 4, y + 5, x + w / 2 + 4, y + h - 5, fill=(196, 40, 44))
        rect(d, x + w / 2 - 11, y + h / 2 - 4, x + w / 2 + 11, y + h / 2 + 4, fill=(196, 40, 44))
    elif kind == "cyber":
        scene_base(d, x, y, w, h, (10, 16, 26), (6, 10, 16))
        f = F_SANS(7)
        for r, bits in enumerate(["1010 1101", "LOCKED", "0101 0010"]):
            txt(d, x + 8, y + 3 + r * 9, bits, f, fill=(80, 200, 120))
        rect(d, x + w * 0.60, y + h * 0.30, x + w * 0.80, y + h - 5, outline=(230, 190, 80), width=2)
        d.arc([(x + w * 0.65) * S, (y + 2) * S, (x + w * 0.75) * S, (y + h * 0.45) * S],
              start=180, end=360, fill=(230, 190, 80), width=2)
    elif kind == "plane":
        scene_base(d, x, y, w, h, (70, 110, 160), (40, 70, 110))
        poly(d, [(x + w * 0.14, y + h * 0.52), (x + w * 0.62, y + h * 0.52),
                 (x + w * 0.72, y + h * 0.36), (x + w * 0.78, y + h * 0.52),
                 (x + w * 0.86, y + h * 0.52), (x + w * 0.80, y + h * 0.62),
                 (x + w * 0.20, y + h * 0.62)], fill=(238, 240, 244))
        line(d, [(x + w * 0.60, y + h * 0.20), (x + w * 0.78, y + h * 0.80)], fill=RED, width=3)
        line(d, [(x + w * 0.78, y + h * 0.20), (x + w * 0.60, y + h * 0.80)], fill=RED, width=3)
    elif kind == "bottle":
        scene_base(d, x, y, w, h, (96, 74, 40), (60, 44, 22))
        rect(d, x + w / 2 - 3, y + 3, x + w / 2 + 3, y + 9, fill=(40, 60, 36))
        poly(d, [(x + w / 2 - 3, y + 9), (x + w / 2 + 3, y + 9), (x + w / 2 + 8, y + 16),
                 (x + w / 2 + 8, y + h - 3), (x + w / 2 - 8, y + h - 3),
                 (x + w / 2 - 8, y + 16)], fill=(52, 84, 44))
        rect(d, x + w / 2 - 8, y + h * 0.52, x + w / 2 + 8, y + h * 0.52 + 8, fill=(238, 230, 205))
        poly(d, [(x + w * 0.70, y + h - 14), (x + w * 0.76, y + h - 4),
                 (x + w * 0.64, y + h - 4)], outline=(255, 190, 60), width=2)
        txt_c(d, x + w * 0.70, y + h - 12, "!", F_SANS_B(8), fill=(255, 190, 60))
    elif kind == "factory":
        scene_base(d, x, y, w, h, (110, 80, 66), (60, 40, 34))
        rect(d, x + w * 0.16, y + h - 13, x + w * 0.62, y + h - 3, fill=(40, 36, 36))
        rect(d, x + w * 0.20, y + h - 22, x + w * 0.26, y + h - 13, fill=(40, 36, 36))
        rect(d, x + w * 0.32, y + h - 25, x + w * 0.38, y + h - 13, fill=(40, 36, 36))
        poly(d, [(x + w * 0.62, y + h - 13), (x + w * 0.72, y + h - 26),
                 (x + w * 0.84, y + h - 13)], fill=(250, 120, 36))
        poly(d, [(x + w * 0.68, y + h - 13), (x + w * 0.72, y + h - 20),
                 (x + w * 0.78, y + h - 13)], fill=(255, 200, 80))
        ellipse(d, x + w * 0.16, y + 1, x + w * 0.44, y + 8, fill=(96, 88, 84))
    elif kind == "quake":
        scene_base(d, x, y, w, h, (150, 124, 92), (104, 84, 58))
        poly(d, [(x + w * 0.16, y + h * 0.48), (x + w * 0.30, y + h * 0.26),
                 (x + w * 0.44, y + h * 0.48)], fill=(120, 44, 36))
        rect(d, x + w * 0.20, y + h * 0.48, x + w * 0.40, y + h - 8, fill=(232, 222, 200))
        pts = [(x + w * 0.50, y + h - 3)]
        cx = x + w * 0.52
        for i, dx in enumerate([6, -4, 7, -5, 6, -3]):
            pts.append((cx + dx, y + h - 6 - i * 4))
            cx += dx
        line(d, pts, fill=(40, 30, 24), width=2)
        line(d, [(x + 4, y + h - 3), (x + w - 4, y + h - 3)], fill=(60, 46, 34), width=2)
    elif kind == "orbit":
        scene_base(d, x, y, w, h, (12, 18, 40), (6, 10, 22))
        ellipse(d, x + w * 0.56, y + h * 0.30, x + w * 0.56 + 19, y + h * 0.30 + 19, fill=(196, 160, 128))
        ellipse(d, x + w * 0.56 + 4, y + h * 0.30 + 5, x + w * 0.56 + 9, y + h * 0.30 + 10, fill=(168, 134, 104))
        d.arc([(x + w * 0.30) * S, (y - 2) * S, (x + w * 0.92) * S, (y + h + 8) * S],
              start=20, end=200, fill=(150, 180, 230), width=1)
        rect(d, x + w * 0.30, y + h * 0.34, x + w * 0.38, y + h * 0.34 + 6, fill=(210, 214, 224))
        rect(d, x + w * 0.22, y + h * 0.34 + 1, x + w * 0.30, y + h * 0.34 + 5, fill=(80, 110, 190))
        rect(d, x + w * 0.38, y + h * 0.34 + 1, x + w * 0.46, y + h * 0.34 + 5, fill=(80, 110, 190))
        for sx, sy in [(0.12, 0.16), (0.84, 0.12), (0.68, 0.62), (0.08, 0.66)]:
            ellipse(d, x + w * sx, y + h * sy, x + w * sx + 2, y + h * sy + 2, fill=(240, 240, 250))


LEAD_SCENES = {"cop": sc_cop, "radar": sc_radar, "drones": sc_drones}
MX, RX = 14, 1010
CW = RX - MX


def tag_chip(d, x, y, tag):
    col = {"REPORTED": (38, 84, 143), "CLAIM": (163, 30, 34),
           "FORECAST": (146, 96, 36)}[tag]
    f = F_SANS_B(6.5)
    w = tw(d, tag, f) + 8
    rect(d, x, y, x + w, y + 10, fill=col)
    txt(d, x + 4, y + 1.5, tag, f, fill=(255, 255, 255))
    return w


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top strip + masthead
    rect(d, 0, 0, 1024, 17, fill=NAVY)
    txt(d, MX, 4, "THE WORLD IN ONE DAY", F_SANS_B(9), fill=CREAM)
    txt_r(d, RX, 4.5, "37 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
          F_SANS(8), fill=(200, 205, 220))
    txt_c(d, 512, 21, "Sunday 22 November 2026", F_SERIF_B(37), fill=NAVY)
    sub = ("COP31 collapses with no deal · Iran claims strikes on US bases "
           "in Bahrain · 186 drones over Ukraine overnight")
    txt_c(d, 512, 66, sub, fit_font(d, sub, F_SERIF, 12.5, CW), fill=RED)

    # ---- stat strip
    y = 84
    rect(d, MX, y, RX, y + 33, outline=NAVY, width=1)
    sw = CW / 6
    for i, (num, lab) in enumerate(STATS):
        x = MX + i * sw
        if i:
            line(d, [(x, y + 3), (x, y + 30)], fill=(190, 190, 180), width=1)
        txt_c(d, x + sw / 2, y + 2, num, F_SERIF_B(17), fill=NAVY)
        txt_c(d, x + sw / 2, y + 22, lab, fit_font(d, lab, F_SANS, 7.5, sw - 8), fill=GREY)

    # ---- region tally bar
    y = 122
    x = MX
    total = sum(n for _, n, _ in TALLY)
    for name, n, col in TALLY:
        wseg = CW * n / total
        rect(d, x, y, x + wseg - 1, y + 13, fill=col)
        lab = "%s %d" % (name, n)
        txt_c(d, x + wseg / 2, y + 2.5, lab, fit_font(d, lab, F_SANS_B, 7.5, wseg - 6),
              fill=(255, 255, 255))
        x += wseg

    # ---- UTC timeline
    y = 141
    txt(d, MX, y, "THE DAY IN UTC", F_SANS_B(8.5), fill=NAVY)
    tx = MX + 108
    for t, ev in TIMELINE:
        txt(d, tx, y, t, F_SANS_B(9), fill=RED)
        tx += tw(d, t, F_SANS_B(9)) + 3
        f = F_SANS(8.5)
        txt(d, tx, y + 0.5, ev, f, fill=INK)
        tx += tw(d, ev, f) + 14

    # ---- leads
    y = 160
    lw = (CW - 24) / 3
    for i, (num, kicker, tag, region, place, head, body, src, scene) in enumerate(LEADS):
        x = MX + i * (lw + 12)
        LEAD_SCENES[scene](d, x, y, lw, 84)
        rect(d, x, y, x + lw, y + 15, fill=RED)
        txt(d, x + 6, y + 3, "%d · %s" % (num, kicker), F_SANS_B(9), fill=(255, 255, 255))
        rect(d, x, y, x + lw, y + 84, outline=(120, 110, 90), width=1)
        yy = y + 88
        tag_chip(d, x, yy, tag)
        txt(d, x + 62, yy + 1, place, F_SANS_B(7.5), fill=RED)
        yy += 13
        yy = draw_wrapped(d, x, yy, head, F_SERIF_B(14.5), lw, NAVY, 17, max_lines=2)
        yy = draw_wrapped(d, x, yy + 1, body, F_SANS(8.5), lw, INK, 11, max_lines=4)
        txt(d, x, yy + 1, "Source: " + src, F_SANS(7), fill=GREY)

    # ---- cards header
    y = 356
    line(d, [(MX, y), (RX, y)], fill=NAVY, width=1)
    txt(d, MX, y + 4, "THE DAY IN THIRTEEN", F_SERIF_B(13), fill=NAVY)
    txt_r(d, RX, y + 6, "stories 4–16", F_SANS(9), fill=GREY)

    # ---- cards grid (5 / 5 / 3)
    y = 378
    cw5 = (CW - 48) / 5
    ch = 86
    for idx, (num, region, place, head, body, src, scene) in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x = MX + col * (cw5 + 12)
        yy0 = y + row * (ch + 8)
        card_scene(d, scene, x, yy0, cw5, 27)
        rect(d, x, yy0, x + cw5, yy0 + 27, outline=(150, 140, 120), width=1)
        yy = yy0 + 30
        kf = fit_font(d, "%d · %s" % (num, place), F_SANS_B, 7, cw5)
        txt(d, x, yy, "%d · %s" % (num, place), kf, fill=RED)
        yy += 10
        yy = draw_wrapped(d, x, yy, head, F_SANS_B(9), cw5, NAVY, 11, max_lines=2)
        yy = draw_wrapped(d, x, yy, body, F_SANS(7.5), cw5, INK, 9.5, max_lines=3)
        txt(d, x, yy0 + ch - 8, src, F_SANS(6.5), fill=GREY)
    return img, d


TAG_COLORS = {"REPORTED": (38, 84, 143), "CLAIM": (163, 30, 34),
              "FORECAST": (146, 96, 36)}


def finish(img, d):
    # ---- bottom headers
    y = 656
    line(d, [(MX, y), (RX, y)], fill=NAVY, width=1)
    txt(d, MX, y + 4, "ALSO ON SUNDAY 22 NOVEMBER — 21 MORE BRIEFS", F_SANS_B(9), fill=NAVY)
    txt_r(d, RX, y + 4, "WHERE IT HAPPENED — pins match story numbers", F_SANS_B(9), fill=NAVY)

    # ---- briefs (left column)
    bx, bw = MX, 526
    yy = 676
    for num, region, text, src, tag in BRIEFS:
        pre = "%d · %s — " % (num, region)
        pf = F_SANS_B(7.5)
        pw = tw(d, pre, pf)
        txt(d, bx, yy + 0.5, pre, pf, fill=RED)
        rest = "%s (%s) · " % (text, src)
        size = 8.5
        rf = F_SANS(size)
        while pw + tw(d, rest, rf) + tw(d, tag, F_SANS_B(size)) > bw and size > 6.5:
            size -= 0.5
            rf = F_SANS(size)
        txt(d, bx + pw, yy, rest, rf, fill=INK)
        txt(d, bx + pw + tw(d, rest, rf), yy, tag, F_SANS_B(size), fill=TAG_COLORS[tag])
        yy += 13.2

    # ---- world map (right)
    gx, gy, gw, gh = 552, 674, 458, 234
    rect(d, gx, gy, gx + gw, gy + gh, fill=MAPNAVY)
    cell_w, cell_h = gw / 92, gh / 46
    for r, spans in MAP_ROWS.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cx = gx + c * cell_w
                cy = gy + r * cell_h
                rect(d, cx + 0.9, cy + 0.9, cx + cell_w - 0.9, cy + cell_h - 0.9, fill=LAND)
    for num, (lat, lon, jx, jy) in PINS.items():
        px = gx + (lon + 180) / 360 * gw + jx
        py = gy + (84 - lat) / 142 * gh + jy
        ellipse(d, px - 6.5, py - 6.5, px + 6.5, py + 6.5, fill=PIN, outline=(255, 255, 255), width=1)
        lab = str(num)
        f = F_SANS_B(6.5 if len(lab) > 1 else 7.5)
        txt_c(d, px, py - 3.6, lab, f, fill=(255, 255, 255))

    # ---- date-check box (under map)
    dy = 916
    rect(d, gx, dy, gx + gw, 950, outline=RED, width=1)
    txt(d, gx + 6, dy + 3, "DATE CHECK — left out as other days' news:", F_SANS_B(7.5), fill=RED)
    draw_wrapped(d, gx + 6, dy + 13, DATECHECK, F_SANS(7.5), gw - 12, INK, 9.5, max_lines=2)

    # ---- legend + sources
    txt_c(d, 512, 958, LEGEND, F_SANS_B(8.5), fill=NAVY)
    srcs = ("Sources: Reuters, BBC, Al Jazeera, AP, The Guardian, info.gov.hk, ESPNcricinfo, "
            "Formula1.com, RFE/RL. Pictures and map: original, drawn in code.")
    txt_c(d, 512, 971, srcs, fit_font(d, srcs, F_SANS, 7.5, CW), fill=GREY)

    # ---- bottom strip
    rect(d, 0, 986, 1024, 1024, fill=NAVY)
    txt_c(d, 512, 998, "THE WORLD IN ONE DAY · SUNDAY 22 NOVEMBER 2026 · ONE PAGE",
          F_SANS_B(10), fill=CREAM)

    small = img.resize((1024, 1024), Image.LANCZOS)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    small.save(out, optimize=True)
    import hashlib
    data = open(out, "rb").read()
    print("wrote", out)
    print("bytes", len(data))
    print("sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    _img, _d = build()
    finish(_img, _d)
