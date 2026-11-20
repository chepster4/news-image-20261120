#!/usr/bin/env python3
"""The Daily World - Friday, 20 November 2026.

A one-page newspaper front page summing up the day's world news in a
single image: Kyiv bridges hit, Cyclone Akvan landfall, the AI sell-off,
and 37 more stories from 20 November 2026.

Drawn from scratch with the Python standard library only (no Pillow, no
external fonts): text is rendered from a built-in 5x7 bitmap font, shapes
from a small raster library, PNG encoded with zlib/struct.

Writes entry.png to $MAKEFUN_OUTPUT_DIR (default "out").
Deterministic: identical bytes on every run.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (24, 24, 24)
RED = (178, 38, 30)
BLUE = (29, 78, 137)
DARK = (34, 48, 60)
SEA = (213, 225, 231)
LAND = (233, 223, 191)
LANDLINE = (176, 164, 130)
GREY = (122, 120, 112)
LIGHT = (238, 234, 222)
ORANGE = (224, 122, 26)
FIRE = (240, 180, 40)
GOLD = (201, 162, 39)
GREEN = (46, 125, 70)
NIGHT = (18, 32, 54)
NIGHT2 = (28, 52, 84)
STEEL = (96, 130, 158)
SAND = (222, 205, 160)
TEAL = (42, 110, 110)
PALE = (208, 222, 230)
RIVER = (16, 42, 67)

# 5x7 bitmap font: each glyph is 7 rows of 5 bits.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "\u2022": ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
}

buf = bytearray(W * H * 3)
buf[:] = bytes(PAPER) * (W * H)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        s = (yy * W + x0) * 3
        buf[s:s + (x1 - x0) * 3] = row


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def circle_outline(cx, cy, r, c):
    steps = max(24, int(2 * math.pi * r))
    for i in range(steps):
        a = 2 * math.pi * i / steps
        px(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c)


def poly(pts, c):
    if not pts:
        return
    ys = [p[1] for p in pts]
    y0 = max(0, min(ys))
    y1 = min(H - 1, max(ys))
    n = len(pts)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x0, yy0 = pts[i]
            x1, yy1 = pts[(i + 1) % n]
            if (yy0 <= y < yy1) or (yy1 <= y < yy0):
                if yy1 != yy0:
                    xs.append(x0 + (y - yy0) * (x1 - x0) / (yy1 - yy0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            xa = int(xs[k] + 0.5)
            xb = int(xs[k + 1] + 0.5)
            if xb > xa:
                rect(xa, y, xb - xa, 1, c)


def text(s, x, y, scale, c):
    for ch in s:
        g = FONT.get(ch)
        if g is None:
            g = FONT[" "]
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "1":
                    rect(x + col * scale, y + row * scale, scale, scale, c)
        x += 6 * scale


def tw(s, scale):
    return len(s) * 6 * scale - scale


def center(s, y, scale, c, x0=0, x1=W):
    text(s, x0 + (x1 - x0 - tw(s, scale)) // 2, y, scale, c)


def wrap(s, maxchars):
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        if cur == "":
            cur = wd
        elif len(cur) + 1 + len(wd) <= maxchars:
            cur = cur + " " + wd
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- stories

TOP3 = [
    {
        "kicker": "UKRAINE - WAR",
        "head": ("BRIDGES HIT IN", "BIGGEST BARRAGE"),
        "deck": "RUSSIA FIRES 110+ MISSILES AND 400 DRONES; 3 BRIDGES HIT, 8 KILLED",
        "art": "kyiv",
    },
    {
        "kicker": "INDIA - WEATHER",
        "head": ("CYCLONE AKVAN", "HITS ODISHA"),
        "deck": "STORM CROSSES COAST NEAR GOPALPUR; 300,000 EVACUATED, NO DEATHS",
        "art": "akvan",
    },
    {
        "kicker": "MARKETS - AI",
        "head": ("AI SELLOFF SINKS", "MARKETS"),
        "deck": "NIKKEI -4.8%, SOFTBANK -16%; S&P 500 DOWN 2% FOR A FIFTH DAY",
        "art": "markets",
    },
]

SMALL = [
    {
        "kicker": "THE HAGUE",
        "head": ("WORLD COURT: MYANMAR", "GUILTY OF GENOCIDE"),
        "deck": "ICJ RULES MYANMAR COMMITTED GENOCIDE AGAINST THE ROHINGYA - A FIRST.",
        "art": "scales",
    },
    {
        "kicker": "RIYADH",
        "head": ("HOUTHI MISSILE HITS", "RIYADH TOWER"),
        "deck": "SAUDI WEALTH FUND TOWER DAMAGED IN THE CAPITAL'S FINANCIAL DISTRICT.",
        "art": "tower",
    },
    {
        "kicker": "ANTALYA",
        "head": ("COP31: FOSSIL", "PHASE-OUT DROPPED"),
        "deck": "FINAL-DAY DRAFT DROPS ANY CALL TO END FOSSIL FUELS AS TALKS DEADLOCK.",
        "art": "globe",
    },
    {
        "kicker": "BRUSSELS",
        "head": ("UK AND EU STRIKE", "RESET DEAL"),
        "deck": "SECOND SUMMIT OF THE RENEWED PARTNERSHIP DEEPENS TIES IN BRUSSELS.",
        "art": "stars",
    },
    {
        "kicker": "GAMES",
        "head": ("GTA 6 TOPS", "$2.3 BILLION"),
        "deck": "LAUNCH SALES PASS $2.3BN - THE BIGGEST ENTERTAINMENT DEBUT ON RECORD.",
        "art": "game",
    },
    {
        "kicker": "GAZA",
        "head": ("ISRAEL CROSSES GAZA", "YELLOW LINE"),
        "deck": "TROOPS CROSS THE CEASEFIRE BOUNDARY IN CENTRAL GAZA, A FIRST SINCE THE TRUCE.",
        "art": "gaza",
    },
    {
        "kicker": "THE GULF",
        "head": ("IRAN WAR ENTERS", "NINTH MONTH"),
        "deck": "TANKER ATTACKS IN HORMUZ INTENSIFY; A TANKER BURNS AFTER HITTING A MINE.",
        "art": "tanker",
    },
    {
        "kicker": "KENYA",
        "head": ("LAST EBOLA PATIENT", "GOES HOME"),
        "deck": "KENYA DISCHARGES ITS FINAL EBOLA PATIENT, 37 DAYS AFTER THE FIRST CASE.",
        "art": "virus",
    },
]

LISTED = [
    (12, "BERLIN: EUROPE READY TO TALK"),
    (13, "KERCH BRIDGE HIT A THIRD TIME"),
    (14, "RUSSIAN MISSILE STRAYS INTO POLAND"),
    (15, "MERZ: NO NEW YALTA OVER EUROPE"),
    (16, "DENMARK BACKS GREENLAND-US DEAL"),
    (17, "ESTONIA SHUTS BORDER WITH RUSSIA"),
    (18, "TRUMP PUTS IRAN DECISION OFF TO 2027"),
    (19, "IMF: PUBLIC DEBT NEARS 100% OF GDP"),
    (20, "ITALY FINES META 805M EUROS"),
    (21, "FAA GROUND STOP STRANDS 1.5M FLYERS"),
    (22, "WHITE HOUSE FIRES CYBER CHIEF"),
    (23, "US AUCTIONS DEEP-SEA MINING LEASES"),
    (24, "BUKELE REGISTERS FOR THIRD TERM"),
    (25, "US AND VENEZUELA SIGN DEFENCE DEAL"),
    (26, "SENEGAL BOAT SINKS; DOZENS MISSING"),
    (27, "SUDAN DRONE STRIKE KILLS 10 AT MINE"),
    (28, "YOUTH STRIKE IN 25 COUNTRIES"),
    (29, "ITALY STRIKES OVER LIVING COSTS"),
    (30, "NEW YORK: CLOSE RIKERS BY 2032"),
    (31, "VOYAGER 1: ONE LIGHT-DAY FROM EARTH"),
    (32, "VAN GOGH SELLS FOR RECORD $190.4M"),
    (33, "FIJI DECLARES DISASTER IN DROUGHT"),
    (34, "SEOUL COURT FREES EX-PM HAN"),
    (35, "HAITI POLICE KILL 34 GANG MEMBERS"),
    (36, "HMS VENGEANCE ENDS 217-DAY PATROL"),
    (37, "ELLA LANGLEY SWEEPS CMA AWARDS"),
    (38, "MOROCCO TO BUILD DEFENCE INDUSTRY"),
    (39, "'SUPERMOUNTAINS' UNDER ANTARCTICA"),
    (40, "VATICAN TREE UP IN ST PETER'S SQUARE"),
]

NUMBERS = [
    ("110+", "MISSILES AT UKRAINE"),
    ("400+", "DRONES IN ONE NIGHT"),
    ("300,000", "EVACUATED IN ODISHA"),
    ("-4.8%", "NIKKEI FALLS IN A DAY"),
    ("$2.3BN", "GTA 6 LAUNCH SALES"),
    ("217", "DAYS UNDER WATER"),
]

# ---------------------------------------------------------------- pictures

def burst(cx, cy, r, c1, c2):
    circle(cx, cy, r, c1)
    circle(cx, cy, r // 2, c2)
    for k in range(8):
        a = math.pi * k / 4
        line(cx, cy, int(cx + (r + 7) * math.cos(a)), int(cy + (r + 7) * math.sin(a)), c1)


def draw_kyiv(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    for sx, sy in [(20, 10), (60, 18), (110, 8), (150, 14), (200, 10), (250, 16),
                   (280, 8), (40, 30), (90, 26), (180, 28), (230, 24), (300, 30)]:
        rect(x + sx, y + sy, 2, 2, LIGHT)
    circle(x + w - 42, y + 20, 10, LIGHT)
    circle(x + w - 45, y + 17, 9, NIGHT)
    # skyline
    for bx, bw, bh in [(8, 26, 20), (40, 18, 30), (64, 30, 16), (250, 22, 24), (278, 24, 18)]:
        rect(x + bx, y + h - 34 - bh, bw, bh, (8, 12, 20))
        rect(x + bx + 5, y + h - 34 - bh + 6, 3, 3, GOLD)
        rect(x + bx + bw - 9, y + h - 34 - bh + 12, 3, 3, GOLD)
    # river
    rect(x, y + h - 20, w, 20, RIVER)
    rect(x + 20, y + h - 14, 120, 2, STEEL)
    rect(x + 160, y + h - 8, 130, 2, STEEL)
    # bridge deck and towers
    rect(x + 10, y + h - 36, w - 20, 5, (10, 10, 12))
    t1 = x + int(w * 0.32)
    t2 = x + int(w * 0.68)
    rect(t1, y + h - 62, 6, 26, (10, 10, 12))
    rect(t2, y + h - 62, 6, 26, (10, 10, 12))
    line(t1 + 3, y + h - 62, x + 10, y + h - 36, (60, 60, 66))
    line(t1 + 3, y + h - 62, x + w // 2, y + h - 36, (60, 60, 66))
    line(t2 + 3, y + h - 62, x + w // 2, y + h - 36, (60, 60, 66))
    line(t2 + 3, y + h - 62, x + w - 10, y + h - 36, (60, 60, 66))
    # explosions and smoke
    burst(x + int(w * 0.36), y + 34, 8, ORANGE, FIRE)
    burst(x + int(w * 0.72), y + 26, 7, ORANGE, FIRE)
    burst(x + int(w * 0.52), y + 44, 5, ORANGE, FIRE)
    circle(x + int(w * 0.30), y + 20, 6, GREY)
    circle(x + int(w * 0.78), y + 14, 7, GREY)
    circle(x + int(w * 0.52), y + 32, 5, GREY)
    rect(t1 + 20, y + h - 40, 8, 4, ORANGE)
    rect(t2 - 26, y + h - 40, 6, 4, ORANGE)


def draw_akvan(x, y, w, h):
    rect(x, y, w, 38, PALE)
    rect(x, y + 38, w, h - 38, STEEL)
    # cyclone spiral
    cx, cy = x + int(w * 0.62), y + 46
    for r in (8, 16, 24, 32):
        circle_outline(cx, cy, r, LIGHT)
    circle(cx, cy, 6, PALE)
    line(cx - 32, cy - 4, cx - 8, cy - 10, LIGHT)
    line(cx + 10, cy + 8, cx + 32, cy + 2, LIGHT)
    # rain
    for i in range(11):
        rx = x + 8 + i * 28
        line(rx, y + 6, rx - 6, y + 32, (190, 205, 215))
    # coast and town
    poly([(x, y + h), (x, y + h - 30), (x + 70, y + h - 26),
          (x + 120, y + h - 12), (x + 150, y + h), (x, y + h)], SAND)
    for bx, bw, bh in [(12, 12, 10), (30, 10, 14), (48, 14, 9)]:
        rect(x + bx, y + h - 30 - bh + 8, bw, bh, DARK)
    # waves
    for wy in (y + h - 16, y + h - 10, y + h - 5):
        for wx in range(x + 170, x + w - 20, 26):
            line(wx, wy, wx + 12, wy - 3, LIGHT)
            line(wx + 12, wy - 3, wx + 24, wy, LIGHT)


def draw_markets(x, y, w, h):
    rect(x, y, w, h, LIGHT)
    for gy in range(y + 16, y + h - 8, 18):
        line(x + 8, gy, x + w - 8, gy, (210, 205, 192))
    for gx in range(x + 24, x + w - 8, 26):
        line(gx, y + 8, gx, y + h - 8, (210, 205, 192))
    tops = [14, 22, 20, 32, 40, 48, 58, 68]
    for i, tp in enumerate(tops):
        cx = x + 22 + i * 34
        rect(cx - 6, y + tp, 12, 26, RED)
        line(cx, y + tp - 8, cx, y + tp + 26 + 6, RED)
    for i in range(len(tops) - 1):
        x0 = x + 22 + i * 34
        x1 = x + 22 + (i + 1) * 34
        line(x0, y + tops[i] + 4, x1, y + tops[i + 1] + 4, RED)
        line(x0, y + tops[i] + 5, x1, y + tops[i + 1] + 5, RED)
    # down arrow
    ax, ay = x + w - 46, y + h - 30
    poly([(ax, ay), (ax + 26, ay), (ax + 26, ay + 8), (ax + 38, ay + 8),
          (ax + 13, ay + 26), (ax - 12, ay + 8), (ax, ay + 8)], RED)
    text("-4.8%", x + 12, y + h - 24, 3, RED)


def draw_scales(x, y, w, h):
    rect(x, y, w, h, DARK)
    cx = x + w // 2
    line(cx, y + 6, cx, y + h - 8, GOLD)
    line(cx - 26, y + 10, cx + 26, y + 10, GOLD)
    rect(cx - 2, y + h - 8, 4, 4, GOLD)
    for sgn in (-1, 1):
        ex = cx + sgn * 26
        line(ex, y + 10, ex, y + 16, GOLD)
        poly([(ex - 10, y + 16), (ex + 10, y + 16), (ex, y + 26)], GOLD)
    circle(cx, y + 6, 3, GOLD)


def draw_tower(x, y, w, h):
    rect(x, y, w, h, NIGHT2)
    cx = x + w // 2
    rect(cx - 16, y + 16, 32, h - 16, (52, 68, 88))
    rect(cx - 11, y + 8, 22, 10, (52, 68, 88))
    rect(cx - 6, y + 2, 12, 8, (52, 68, 88))
    for wy in (20, 26, 32):
        rect(cx - 10, y + wy, 4, 4, GOLD)
        rect(cx + 6, y + wy, 4, 4, GOLD)
    poly([(cx - 6, y + 8), (cx + 6, y + 8), (cx, y + 1)], ORANGE)
    poly([(cx - 3, y + 8), (cx + 3, y + 8), (cx, y + 4)], FIRE)


def draw_globe(x, y, w, h):
    rect(x, y, w, h, TEAL)
    cx, cy = x + w // 2 - 18, y + h // 2
    circle(cx, cy, 14, GREEN)
    circle(cx - 5, cy - 4, 5, BLUE)
    circle(cx + 5, cy + 5, 4, BLUE)
    circle(cx + 34, cy - 8, 6, GREY)
    circle(cx + 44, cy - 2, 8, GREY)
    circle(cx + 52, cy - 9, 5, GREY)
    text("COP31", x + w - 62, y + h - 12, 1, LIGHT)


def draw_stars(x, y, w, h):
    rect(x, y, w, h, BLUE)
    cx, cy = x + w // 2, y + 15
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        sx = int(cx + 13 * math.cos(a))
        sy = int(cy + 13 * math.sin(a))
        rect(sx - 1, sy - 1, 3, 3, GOLD)
    text("UK - EU", x + (w - tw("UK - EU", 1)) // 2, y + h - 10, 1, LIGHT)


def draw_game(x, y, w, h):
    rect(x, y, w, h, (30, 20, 50))
    circle(x + w - 30, y + 12, 9, ORANGE)
    for bx, bw, bh in [(10, 20, 14), (34, 14, 20), (52, 22, 11), (78, 16, 18),
                       (98, 20, 12), (122, 14, 16), (140, 24, 10), (168, 18, 15)]:
        rect(x + bx, y + h - bh, bw, bh, (8, 8, 14))
    text("GTA VI", x + 12, y + 8, 3, LIGHT)


def draw_gaza(x, y, w, h):
    rect(x, y, w, h, SAND)
    rect(x, y + 18, w, 3, GOLD)
    line(x + 20, y + 4, x + w - 30, y + h - 6, GREEN)
    line(x + w - 30, y + h - 6, x + w - 44, y + h - 8, GREEN)
    line(x + w - 30, y + h - 6, x + w - 32, y + h - 18, GREEN)
    for bx, bw, bh in [(16, 18, 10), (44, 14, 14), (180, 20, 12)]:
        rect(x + bx, y + h - bh, bw, bh, DARK)


def draw_tanker(x, y, w, h):
    rect(x, y, w, h, STEEL)
    rect(x, y + h - 12, w, 4, (200, 215, 225))
    rect(x + 34, y + 16, w - 68, 10, (20, 20, 24))
    rect(x + 34, y + 26, w - 68, 4, RED)
    rect(x + w - 62, y + 6, 18, 10, LIGHT)
    poly([(x + w // 2 - 6, y + 16), (x + w // 2 + 6, y + 16),
          (x + w // 2, y + 4)], ORANGE)
    circle(x + w // 2 + 12, y + 2, 5, GREY)
    circle(x + w // 2 + 22, y + 5, 4, GREY)


def draw_virus(x, y, w, h):
    rect(x, y, w, h, (220, 240, 220))
    cx, cy = x + w // 2 - 24, y + h // 2
    for k in range(8):
        a = math.pi * k / 4
        line(cx, cy, int(cx + 19 * math.cos(a)), int(cy + 19 * math.sin(a)), GREEN)
    circle(cx, cy, 12, GREEN)
    circle(cx - 4, cy - 3, 3, LIGHT)
    rect(x + w - 34, y + 6, 22, 22, LIGHT)
    rect(x + w - 27, y + 9, 8, 16, RED)
    rect(x + w - 31, y + 13, 16, 8, RED)


ART = {
    "kyiv": draw_kyiv,
    "akvan": draw_akvan,
    "markets": draw_markets,
    "scales": draw_scales,
    "tower": draw_tower,
    "globe": draw_globe,
    "stars": draw_stars,
    "game": draw_game,
    "gaza": draw_gaza,
    "tanker": draw_tanker,
    "virus": draw_virus,
}

# ---------------------------------------------------------------- world map

EURASIA = [
    (-10, 36), (-9, 38), (-9, 42), (-4, 44), (-2, 47), (-1, 49), (1, 51),
    (4, 53), (7, 54), (8, 57), (6, 59), (6, 61), (10, 63), (13, 66),
    (17, 69), (21, 70), (26, 71), (30, 70), (34, 68), (38, 66), (42, 66),
    (46, 68), (50, 69), (54, 68), (58, 69), (62, 70), (66, 71), (70, 72),
    (74, 73), (78, 72), (82, 73), (86, 74), (90, 75), (94, 76), (98, 76),
    (102, 76), (106, 75), (110, 74), (114, 73), (118, 72), (122, 72),
    (126, 71), (130, 71), (134, 71), (138, 72), (142, 72), (146, 71),
    (150, 70), (154, 70), (158, 69), (162, 68), (166, 67), (170, 66),
    (173, 65), (178, 65), (178, 63), (173, 62), (169, 60), (164, 60),
    (160, 58), (158, 54), (157, 51), (155, 48), (152, 45), (148, 42),
    (144, 40), (141, 38), (139, 35), (136, 34), (133, 34), (131, 33),
    (129, 33), (127, 35), (126, 38), (124, 39), (121, 38), (120, 34),
    (121, 31), (120, 27), (118, 25), (115, 23), (112, 21), (109, 18),
    (108, 13), (106, 10), (104, 8), (102, 7), (100, 7), (99, 10),
    (97, 14), (95, 16), (93, 18), (91, 21), (89, 22), (87, 21),
    (85, 19), (83, 17), (81, 14), (80, 10), (78, 8), (76, 9), (75, 12),
    (73, 16), (71, 20), (69, 22), (67, 24), (65, 25), (62, 25), (59, 25),
    (57, 26), (55, 26), (53, 27), (51, 28), (49, 30), (47, 30), (44, 29),
    (41, 30), (39, 31), (37, 31), (36, 33), (35, 36), (33, 36), (30, 36),
    (28, 37), (26, 38), (24, 37), (23, 36), (22, 37), (20, 39), (18, 40),
    (16, 38), (15, 40), (13, 42), (11, 44), (9, 44), (6, 43), (3, 43),
    (1, 41), (-1, 38), (-3, 37), (-6, 36), (-8, 37), (-10, 36),
]
AFRICA = [
    (-17, 15), (-17, 20), (-16, 24), (-14, 28), (-10, 31), (-6, 34),
    (-2, 35), (2, 36), (7, 37), (10, 37), (12, 34), (16, 32), (20, 32),
    (24, 31), (29, 31), (32, 31), (34, 28), (35, 24), (36, 20), (38, 18),
    (39, 15), (41, 11), (44, 11), (48, 11), (51, 12), (51, 10), (48, 6),
    (45, 2), (42, -2), (40, -6), (39, -10), (37, -14), (35, -18),
    (33, -22), (31, -26), (28, -31), (24, -34), (20, -35), (18, -33),
    (16, -29), (14, -24), (12, -18), (12, -13), (10, -6), (9, -1),
    (9, 4), (4, 6), (-2, 5), (-8, 4), (-12, 8), (-15, 11), (-17, 15),
]
NORTH_AMERICA = [
    (-168, 66), (-164, 60), (-158, 58), (-152, 60), (-144, 60), (-137, 58),
    (-132, 54), (-128, 50), (-124, 44), (-124, 38), (-120, 34), (-114, 29),
    (-109, 24), (-105, 20), (-101, 18), (-97, 16), (-94, 17), (-91, 14),
    (-87, 13), (-83, 9), (-80, 8), (-77, 8), (-79, 9), (-82, 10),
    (-84, 14), (-86, 16), (-87, 21), (-90, 21), (-92, 18), (-95, 19),
    (-97, 22), (-97, 26), (-94, 29), (-90, 29), (-86, 30), (-82, 28),
    (-81, 26), (-80, 31), (-78, 34), (-76, 37), (-74, 39), (-72, 41),
    (-70, 43), (-68, 44), (-66, 45), (-64, 44), (-60, 46), (-56, 48),
    (-55, 52), (-60, 55), (-65, 58), (-68, 58), (-72, 62), (-78, 62),
    (-82, 64), (-86, 66), (-92, 66), (-96, 69), (-102, 68), (-110, 68),
    (-118, 70), (-126, 70), (-135, 69), (-145, 70), (-155, 71), (-162, 70),
    (-168, 66),
]
GREENLAND = [
    (-58, 64), (-54, 60), (-46, 60), (-40, 62), (-34, 66), (-28, 68),
    (-22, 70), (-20, 72), (-24, 74), (-32, 76), (-44, 77), (-56, 75),
    (-60, 70), (-58, 64),
]
SOUTH_AMERICA = [
    (-77, 7), (-76, 10), (-72, 12), (-68, 11), (-64, 10), (-60, 8),
    (-55, 6), (-52, 5), (-50, 0), (-46, -2), (-42, -4), (-38, -6),
    (-35, -8), (-37, -12), (-39, -16), (-41, -22), (-46, -26), (-49, -29),
    (-53, -33), (-57, -38), (-60, -40), (-63, -42), (-65, -45), (-67, -49),
    (-69, -52), (-71, -54), (-73, -50), (-73, -44), (-73, -38), (-72, -30),
    (-71, -22), (-72, -18), (-75, -15), (-78, -10), (-80, -6), (-81, -3),
    (-80, 0), (-79, 3), (-77, 7),
]
AUSTRALIA = [
    (113, -22), (114, -28), (115, -33), (118, -35), (122, -34), (126, -32),
    (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (143, -39),
    (146, -39), (149, -37), (151, -34), (153, -30), (153, -27), (152, -24),
    (150, -22), (148, -20), (146, -19), (143, -16), (142, -12), (141, -14),
    (140, -17), (138, -16), (136, -14), (135, -12), (133, -11), (131, -12),
    (129, -14), (127, -14), (124, -16), (121, -18), (118, -20), (115, -21),
    (113, -22),
]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-2, 50), (-5, 50)]
JAPAN = [
    (130, 31), (132, 33), (134, 34), (137, 35), (139, 35), (140, 38),
    (141, 40), (142, 42), (144, 44), (142, 44), (140, 41), (139, 38),
    (137, 36), (135, 34), (132, 33), (130, 31),
]
MADAGASCAR = [
    (44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (45, -25),
    (43, -22), (43, -18), (44, -16),
]

CONTINENTS = [EURASIA, AFRICA, NORTH_AMERICA, GREENLAND, SOUTH_AMERICA,
              AUSTRALIA, UK, JAPAN, MADAGASCAR]

DOTS = [
    (30.5, 50.5, "KYIV", 1, 0),
    (84.9, 19.3, "ODISHA", 0, 1),
    (46.7, 24.7, "RIYADH", 0, 1),
    (4.3, 52.1, None, 0, 0),
    (30.7, 36.9, None, 0, 0),
    (4.35, 50.85, None, 0, 0),
    (34.5, 31.5, None, 0, 0),
    (56.3, 26.6, None, 0, 0),
    (36.8, -1.3, None, 0, 0),
    (36.4, 45.4, None, 0, 0),
    (13.4, 52.5, None, 0, 0),
    (-74.0, 40.7, None, 0, 0),
    (127.0, 37.5, "SEOUL", 1, 0),
    (178.4, -17.7, None, 0, 0),
    (-89.2, 13.7, None, 0, 0),
    (-17.4, 14.7, None, 0, 0),
]


def draw_map(mx, my, mw, mh):
    rect(mx, my, mw, mh, SEA)

    def proj(lon, lat):
        return (int(mx + (lon + 180.0) / 360.0 * mw),
                int(my + (80.0 - lat) / 138.0 * mh))

    for cont in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in cont]
        poly(pts, LAND)
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            line(x0, y0, x1, y1, LANDLINE)
    for lon, lat, label, lx, ly in DOTS:
        dx, dy = proj(lon, lat)
        circle(dx, dy, 5, PAPER)
        circle(dx, dy, 3, RED)
        if label:
            tx = dx + 7 if lx else dx - 7 - tw(label, 1)
            ty = dy - 9 if ly == 0 else dy + 6
            text(label, tx, ty, 1, INK)


def draw_numbers(bx, by, bw, bh):
    rect(bx, by, bw, bh, LIGHT)
    rect(bx, by, bw, 2, RED)
    rect(bx, by, 2, bh, INK)
    rect(bx + bw - 2, by, 2, bh, INK)
    rect(bx, by + bh - 2, bw, 2, INK)
    cols = 2
    rows = 3
    cw = bw // cols
    rh = bh // rows
    for i, (num, label) in enumerate(NUMBERS):
        cx = bx + (i % cols) * cw
        cy = by + (i // cols) * rh
        text(num, cx + 10, cy + 8, 3, RED)
        text(label, cx + 10, cy + 28, 1, INK)
        if i % cols == 1:
            line(cx, cy + 4, cx, cy + rh - 4, GREY)
        if i // cols > 0:
            line(bx + 6, cy, bx + bw - 6, cy, GREY)


# ---------------------------------------------------------------- page

def draw_page():
    # top rule + dateline
    rect(24, 8, 976, 3, INK)
    text("FRIDAY, 20 NOVEMBER 2026", 24, 14, 2, INK)
    center("THE WORLD IN ONE PAGE", 14, 2, INK)
    right = "40 STORIES - 7 REGIONS"
    text(right, 1000 - tw(right, 2), 14, 2, INK)
    rect(24, 32, 976, 2, INK)
    # masthead
    center("THE DAILY WORLD", 36, 8, INK)
    center("ALL THE WORLD'S NEWS THAT FITS ON ONE PAGE", 96, 2, RED)
    rect(24, 114, 976, 3, INK)
    rect(24, 119, 976, 1, INK)
    # top 3 stories
    xs = [24, 356, 688]
    for col, story in enumerate(TOP3):
        x = xs[col]
        ART[story["art"]](x, 124, 312, 92)
        text(story["kicker"], x, 220, 1, RED)
        text(story["head"][0], x, 230, 3, INK)
        text(story["head"][1], x, 252, 3, INK)
        yy = 278
        for ln in wrap(story["deck"], 26):
            text(ln, x, yy, 2, INK)
            yy += 16
    rect(24, 330, 976, 2, INK)
    # stories 4-11: two rows of four
    sx = [24, 272, 520, 768]
    for idx, story in enumerate(SMALL):
        row = idx // 4
        col = idx % 4
        x = sx[col]
        y = 336 + row * 104
        ART[story["art"]](x, y, 232, 38)
        text(story["kicker"], x, y + 42, 1, RED)
        text(story["head"][0], x, y + 52, 2, INK)
        text(story["head"][1], x, y + 66, 2, INK)
        yy = y + 84
        for ln in wrap(story["deck"], 38):
            text(ln, x, yy, 1, INK)
            yy += 8
    rect(24, 544, 976, 2, INK)
    # map band header
    rect(24, 550, 976, 18, INK)
    text("WHERE IT HAPPENED", 30, 553, 2, PAPER)
    right = "THE DAY IN NUMBERS"
    text(right, 1000 - 6 - tw(right, 2), 553, 2, PAPER)
    # map + numbers
    draw_map(24, 574, 648, 122)
    draw_numbers(688, 574, 312, 122)
    rect(24, 700, 976, 2, INK)
    # numbered list 12-40
    text("THE REST OF THE DAY", 24, 706, 2, INK)
    right = "STORIES 12-40"
    text(right, 1000 - tw(right, 2), 706, 2, RED)
    left_items = LISTED[:15]
    right_items = LISTED[15:]
    for i, (num, head) in enumerate(left_items):
        yy = 726 + i * 16
        text(str(num) + ".", 24, yy, 2, RED)
        text(head, 24 + tw(str(num) + ". ", 2), yy, 2, INK)
    for i, (num, head) in enumerate(right_items):
        yy = 726 + i * 16
        text(str(num) + ".", 520, yy, 2, RED)
        text(head, 520 + tw(str(num) + ". ", 2), yy, 2, INK)
    rect(24, 968, 976, 2, INK)
    # footer
    center("DATE CHECK - FRIDAY, 20 NOVEMBER 2026", 974, 2, INK)
    center("SOURCES: AP \u2022 REUTERS \u2022 AFP \u2022 BBC \u2022 CNN \u2022 CNBC \u2022 IMD \u2022 NASA \u2022 SOTHEBY'S \u2022 IMF",
           992, 1, GREY)
    center("DRAWN FROM REPORTING. NO PHOTOGRAPHS USED. THE DAILY WORLD.",
           1002, 1, GREY)


def write_png(path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    draw_page()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = write_png(path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
