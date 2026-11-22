#!/usr/bin/env python3
"""Sunday 22 November 2026 in one image.

A self-contained, stdlib-only poster engine: a pixel canvas, hand-drawn
flat-vector scenes, a 5x7 bitmap font defined below, and a hand-rolled PNG
encoder (zlib + struct). No network, no clock, no randomness: two runs are
byte-identical. Writes entry.png (1024x1024, <= 1 MiB) to
$MAKEFUN_OUTPUT_DIR or the current directory.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
CREAM = (247, 242, 231)
PAPER = (255, 253, 246)
INK = (22, 22, 28)
NAVY = (20, 38, 78)
NAVY2 = (28, 52, 102)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
RED2 = (214, 48, 49)
BLUE = (36, 84, 160)
SKY = (135, 190, 224)
TEAL = (18, 130, 118)
GREEN = (46, 125, 50)
LGREEN = (139, 195, 74)
ORANGE = (224, 122, 26)
YELLOW = (240, 196, 25)
GREY = (110, 110, 112)
LGREY = (222, 222, 216)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
SAND = (222, 184, 120)
BROWN = (122, 82, 42)
SEA = (46, 110, 150)
DARK = (38, 44, 58)

REGION_COLORS = {
    "EUROPE": (36, 84, 160), "ASIA": (178, 34, 34), "N AMERICA": (18, 130, 118),
    "OCEANIA": (224, 122, 26), "AFRICA": (46, 125, 50), "LATIN AM": (123, 72, 160),
    "MID EAST": (150, 96, 20), "GLOBAL": (38, 44, 58),
}

# ------------------------------------------------------------------- font
# 5x7 bitmap font, '#' = ink. Only capitals are drawn; text() uppercases.
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
"2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
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
"?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
"'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
"-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
"/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
"(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
"%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
"&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
"+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
"=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
'"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
"#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
"*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
"_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
"$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
"@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
"[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
"]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
"<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
"^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
"|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
"\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
"{": ("00110", "01000", "01000", "01110", "01000", "01000", "00110"),
"}": ("01100", "00010", "00010", "01110", "00010", "00010", "01100"),
"~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * (6 * scale) - scale


def wrap(s, max_chars):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if len(t) <= max_chars:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c
                i += 3

    def vgrad(self, x, y, w, h, c0, c1):
        for j in range(h):
            t = j / max(1, h - 1)
            c = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
            self.rect(x, y + j, w, 1, c)

    def dither(self, x, y, w, h, c, step=4):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if (xx + yy) % step == 0:
                    self.px(xx, yy, c)

    def outline(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.px(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.px(xx, yy, c)

    def ring(self, cx, cy, r, c, t=1):
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if abs(d - r) <= t:
                    self.px(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        xs = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = xs
        for yy in range(ay, cy + 1):
            if yy < by:
                t0 = (yy - ay) / max(1, by - ay)
                t1 = (yy - ay) / max(1, cy - ay)
                xa, xb = ax + (bx - ax) * t0, ax + (cx - ax) * t1
            else:
                t0 = (yy - by) / max(1, cy - by)
                t1 = (yy - ay) / max(1, cy - ay)
                xa, xb = bx + (cx - bx) * t0, ax + (cx - ax) * t1
            for xx in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
                self.px(xx, yy, c)

    def text(self, x, y, s, c, scale=1):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                cx += 6 * scale
                continue
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + col * scale, y + r * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def ctext(self, cx, y, s, c, scale=1):
        self.text(cx - text_width(s, scale) // 2, y, s, c, scale)

    def para(self, x, y, s, c, scale, max_chars, leading=None):
        if leading is None:
            leading = 7 * scale + 2
        for ln in wrap(s, max_chars):
            self.text(x, y, ln, c, scale)
            y += leading
        return y


# --------------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.buf[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        ch = struct.pack(">I", len(data)) + kind + data
        return ch + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ------------------------------------------------------------ scene helpers
def sun(cv, cx, cy, r, c=YELLOW):
    cv.disc(cx, cy, r, c)
    for k in range(8):
        a = k * 0.785398
        x1 = int(cx + (r + 2) * _cos(a))
        y1 = int(cy + (r + 2) * _sin(a))
        x2 = int(cx + (r + 7) * _cos(a))
        y2 = int(cy + (r + 7) * _sin(a))
        cv.line(x1, y1, x2, y2, c)


def _cos(a):
    return 1 - a * a / 2 + a ** 4 / 24 - a ** 6 / 720


def _sin(a):
    return a - a ** 3 / 6 + a ** 5 / 120 - a ** 7 / 5040


def mountain(cv, x, y, w, h, c, snow=True):
    cv.tri(x, y + h, x + w // 2, y, x + w, y + h, c)
    if snow:
        cv.tri(x + w // 2 - 7, y + 10, x + w // 2, y, x + w // 2 + 7, y + 10, WHITE)


def pine(cv, x, y, h, c=GREEN):
    cv.tri(x - 9, y, x, y - h, x + 9, y, c)
    cv.tri(x - 7, y - h // 2, x, y - h - 4, x + 7, y - h // 2, c)
    cv.rect(x - 1, y, 3, 6, BROWN)


def flag_uk(cv, x, y, w, h):
    cv.rect(x, y, w, h, BLUE)
    cv.rect(x, y + h // 3, w, h // 3, WHITE)
    cv.rect(x + w // 3, y, w // 3, h, WHITE)
    cv.line(x, y, x + w, y + h, RED2)
    cv.line(x + w, y, x, y + h, RED2)
    cv.rect(x, y + h // 2 - 1, w, 3, RED2)
    cv.rect(x + w // 2 - 1, y, 3, h, RED2)


def flag_nl(cv, x, y, w, h):
    cv.rect(x, y, w, h // 3 + 1, RED2)
    cv.rect(x, y + h // 3, w, h // 3 + 1, WHITE)
    cv.rect(x, y + 2 * h // 3, w, h - 2 * h // 3, BLUE)


def flag_jp(cv, x, y, w, h):
    cv.rect(x, y, w, h, WHITE)
    cv.disc(x + w // 2, y + h // 2, h // 3, RED2)


def flag_in(cv, x, y, w, h):
    cv.rect(x, y, w, h // 3 + 1, (255, 153, 51))
    cv.rect(x, y + h // 3, w, h // 3 + 1, WHITE)
    cv.rect(x, y + 2 * h // 3, w, h - 2 * h // 3, (19, 136, 8))
    cv.ring(x + w // 2, y + h // 2, h // 6, NAVY)


def flag_ee(cv, x, y, w, h):
    cv.rect(x, y, w, h // 3 + 1, (0, 114, 206))
    cv.rect(x, y + h // 3, w, h // 3 + 1, BLACK)
    cv.rect(x, y + 2 * h // 3, w, h - 2 * h // 3, WHITE)


def flag_ua(cv, x, y, w, h):
    cv.rect(x, y, w, h // 2 + 1, (0, 91, 187))
    cv.rect(x, y + h // 2, w, h - h // 2, (255, 213, 0))


def flag_mx(cv, x, y, w, h):
    cv.rect(x, y, w // 3 + 1, h, GREEN)
    cv.rect(x + w // 3, y, w // 3 + 1, WHITE)
    cv.rect(x + 2 * w // 3, y, w - 2 * w // 3, RED2)
    cv.disc(x + w // 2, y + h // 2, h // 5, (139, 69, 19))


def waves(cv, x, y, w, h, c=SKY):
    for j in range(0, h, 8):
        for xx in range(x, x + w, 16):
            cv.line(xx, y + j + 3, xx + 8, y + j, c)
            cv.line(xx + 8, y + j, xx + 16, y + j + 3, c)



# -------------------------------------------------------------------- cards
def card_frame(cv, x, y, w, h):
    cv.rect(x, y, w, h, PAPER)
    cv.outline(x, y, w, h, INK, 2)
    cv.rect(x, y, w, 3, RED)


def kicker(cv, x, y, num, region):
    cv.rect(x, y, 26, 12, RED)
    cv.text(x + 3, y + 2, str(num), WHITE, 1)
    cv.text(x + 30, y + 2, region, REGION_COLORS[region], 1)


def lead_card(cv, x, y, w, h, num, region, headline, body, scene):
    card_frame(cv, x, y, w, h)
    kicker(cv, x + 8, y + 8, num, region)
    yy = y + 26
    yy = cv.para(x + 8, yy, headline, INK, 2, (w - 16) // 12, 16)
    sy = yy + 4
    sh = y + h - 62 - sy
    scene(cv, x + 8, sy, w - 16, sh)
    cv.para(x + 8, y + h - 56, body, INK, 1, (w - 16) // 6, 9)


def small_card(cv, x, y, w, h, num, region, headline, body, scene):
    card_frame(cv, x, y, w, h)
    kicker(cv, x + 6, y + 6, num, region)
    yy = y + 22
    yy = cv.para(x + 6, yy, headline, INK, 1, (w - 12) // 6, 9)
    sy = yy + 3
    sh = y + h - 26 - sy
    scene(cv, x + 6, sy, w - 12, sh)
    cv.text(x + 6, y + h - 20, body, GREY, 1)


# -------------------------------------------------------------------- scenes
def scene_cop31(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (16, 60, 110), (90, 170, 210))
    sun(cv, x + w - 34, y + 26, 14)
    cv.disc(x + w // 2, y + h // 2 + 6, 34, SEA)
    cv.disc(x + w // 2 - 12, y + h // 2 - 2, 22, GREEN)
    cv.disc(x + w // 2 + 16, y + h // 2 + 12, 12, LGREEN)
    cv.ring(x + w // 2, y + h // 2 + 6, 34, WHITE, 2)
    cv.rect(x, y + h - 26, w, 26, (60, 48, 36))
    for i in range(6):
        fx = x + 8 + i * (w - 16) // 6
        cv.rect(fx, y + h - 44, 26, 18, PAPER)
        cv.tri(fx, y + h - 44, fx + 13, y + h - 56, fx + 26, y + h - 44, RED2)
        cv.rect(fx + 11, y + h - 26, 4, 8, BROWN)
    cv.dither(x, y, w, 10, WHITE)


def scene_chapo(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (250, 200, 120), (240, 150, 70))
    sun(cv, x + 30, y + 22, 12, (255, 240, 180))
    mountain(cv, x + w - 120, y + 18, 110, h - 40, (120, 70, 40))
    mountain(cv, x + 10, y + 30, 90, h - 52, (150, 90, 50))
    cv.rect(x, y + h - 22, w, 22, (90, 60, 30))
    cv.rect(x, y + h - 34, w, 12, SAND)
    for i in range(5):
        cv.rect(x + 20 + i * 56, y + h - 30, 26, 4, WHITE)
    cv.rect(x + w // 2 - 40, y + h - 66, 80, 32, (200, 170, 130))
    cv.tri(x + w // 2 - 44, y + h - 66, x + w // 2, y + h - 84, x + w // 2 + 44, y + h - 66, (170, 60, 40))
    cv.rect(x + w // 2 + 60, y + h - 96, 60, 10, DARK)
    cv.disc(x + w // 2 + 90, y + h - 96, 9, DARK)
    cv.line(x + w // 2 + 60, y + h - 100, x + w // 2 + 118, y + h - 100, DARK)


def scene_bahrain(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (20, 60, 110), (120, 180, 220))
    cv.rect(x, y + h - 34, w, 34, SEA)
    waves(cv, x, y + h - 30, w, 26, WHITE)
    cv.rect(x + w // 2 - 52, y + 18, 104, h - 52, (220, 220, 205))
    cv.tri(x + w // 2 - 58, y + 18, x + w // 2, y + 2, x + w // 2 + 58, y + 18, NAVY)
    for r in range(4):
        for cc in range(5):
            cv.rect(x + w // 2 - 40 + cc * 17, y + 30 + r * 16, 9, 10, (90, 140, 190))
    cv.rect(x + w // 2 - 60, y + h - 44, 120, 10, DARK)
    # Bahrain flag, bottom left: white serrated band, red field.
    cv.rect(x + 12, y + 8, 30, 18, (206, 17, 38))
    cv.rect(x + 12, y + 8, 10, 18, WHITE)
    for i in range(5):
        cv.tri(x + 12, y + 8 + i * 4, x + 22, y + 10 + i * 4, x + 12, y + 12 + i * 4, WHITE)


def scene_uknl(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, SKY, (220, 235, 245))
    flag_uk(cv, x + 8, y + 8, 64, 40)
    flag_nl(cv, x + w - 72, y + 8, 64, 40)
    cv.rect(x, y + h - 26, w, 26, GREEN)
    cv.disc(x + w // 2 - 22, y + h - 34, 8, (240, 200, 160))
    cv.disc(x + w // 2 + 22, y + h - 34, 8, (240, 200, 160))
    cv.line(x + w // 2 - 22, y + h - 34, x + w // 2, y + h - 52, (240, 200, 160))
    cv.line(x + w // 2 + 22, y + h - 34, x + w // 2, y + h - 52, (240, 200, 160))
    cv.line(x + w // 2 - 14, y + h - 44, x + w // 2 + 14, y + h - 44, INK)


def scene_bridge(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (150, 200, 235), (225, 240, 250))
    sun(cv, x + w - 26, y + 20, 11)
    cv.rect(x, y + h - 24, w, 24, (60, 140, 190))
    waves(cv, x, y + h - 22, w, 18, WHITE)
    cv.line(x + 6, y + h - 24, x + w - 6, y + h - 24, (90, 90, 100))
    for i in range(7):
        px = x + 10 + i * (w - 20) // 6
        cv.line(px, y + h - 24, px, y + 26 + (i % 2) * 6, (90, 90, 100))
    cv.tri(x + 8, y + h - 24, x + w // 2, y + h - 52, x + w - 8, y + h - 24, (200, 60, 50))
    cv.rect(x + w // 2 - 4, y + h - 52, 8, 28, (60, 60, 70))
    cv.rect(x, y + h - 30, w, 6, (60, 60, 70))
    for i in range(4):
        cv.rect(x + 24 + i * 46, y + h - 38, 14, 8, YELLOW)


def scene_estonia(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (190, 210, 225), (235, 238, 240))
    cv.rect(x, y + h - 24, w, 24, GREEN)
    pine(cv, x + 26, y + h - 24, 26)
    pine(cv, x + w - 26, y + h - 24, 30)
    cv.rect(x + w // 2 - 52, y + 10, 104, h - 40, (200, 200, 195))
    for i in range(5):
        cv.line(x + w // 2 - 52 + i * 26, y + 10, x + w // 2 - 52 + i * 26, y + h - 30, INK)
    cv.line(x + w // 2 - 52, y + 16, x + w // 2 + 52, y + 16, INK)
    cv.line(x + w // 2 - 52, y + h - 36, x + w // 2 + 52, y + h - 36, INK)
    flag_ee(cv, x + 8, y + 8, 40, 24)
    cv.rect(x + w - 56, y + h - 52, 48, 22, WHITE)
    cv.outline(x + w - 56, y + h - 52, 48, 22, RED, 2)
    cv.text(x + w - 50, y + h - 44, "STOP", RED, 1)


def scene_japan_india(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (235, 225, 200), (210, 190, 150))
    flag_jp(cv, x + 10, y + 8, 56, 34)
    flag_in(cv, x + w - 66, y + 8, 56, 34)
    cv.rect(x, y + h - 26, w, 26, SAND)
    cv.rect(x + w // 2 - 56, y + h - 52, 112, 22, (70, 80, 70))
    cv.rect(x + w // 2 - 70, y + h - 34, 140, 10, (50, 55, 50))
    cv.line(x + w // 2 + 40, y + h - 48, x + w // 2 + 88, y + h - 56, (50, 55, 50))
    for i in range(5):
        cv.disc(x + w // 2 - 56 + i * 28, y + h - 28, 5, BLACK)
    cv.disc(x + 30, y + h - 44, 6, BROWN)
    cv.disc(x + w - 30, y + h - 44, 6, BROWN)


def scene_nfl(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, NAVY, (60, 90, 160))
    cv.disc(x + w // 2, y + h - 8, 78, GREEN)
    cv.rect(x + w // 2 - 78, y + h - 8, 156, 8, GREEN)
    cv.rect(x, y + 6, w, 22, (0, 90, 50))
    cv.text(x + 8, y + 12, "ESTADIO BANORTE", WHITE, 1)
    cv.text(x + w - 108, y + 12, "MEXICO CITY", YELLOW, 1)
    for i in range(9):
        cv.rect(x + 14 + i * 24, y + h - 44, 12, 30, (200, 200, 200))
        cv.rect(x + 16 + i * 24, y + h - 40, 8, 8, (90, 140, 200))
    cv.disc(x + w // 2, y + h // 2 + 6, 11, (120, 70, 30))
    cv.line(x + w // 2 - 8, y + h // 2 + 6, x + w // 2 + 8, y + h // 2 + 6, WHITE)
    cv.line(x + w // 2 - 8, y + h // 2 + 1, x + w // 2 + 8, y + h // 2 + 1, WHITE)


def scene_william(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (170, 215, 235), (220, 240, 220))
    cv.rect(x, y + h - 18, w, 18, (90, 140, 70))
    for i in range(6):
        pine(cv, x + 16 + i * 36, y + h - 18, 30 + (i % 3) * 8)
    cv.rect(x + w // 2 - 30, y + 10, 60, 44, WHITE)
    cv.outline(x + w // 2 - 30, y + 10, 60, 44, GOLD, 2)
    cv.tri(x + w // 2 - 18, y + 44, x + w // 2, y + 22, x + w // 2 + 18, y + 44, GREEN)
    cv.text(x + w // 2 - 12, y + 16, "10K", GREEN, 1)
    sun(cv, x + w - 24, y + 18, 10)


def scene_aukus(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (40, 90, 140), (20, 50, 90))
    waves(cv, x, y + 8, w, 14, SKY)
    cv.rect(x + 20, y + h // 2 - 6, 150, 22, (40, 44, 58))
    cv.rect(x + 90, y + h // 2 - 22, 44, 18, (40, 44, 58))
    cv.rect(x + 100, y + h // 2 - 34, 6, 12, (40, 44, 58))
    for i in range(4):
        cv.disc(x + 40 + i * 34, y + h // 2 + 5, 4, YELLOW)
    cv.line(x + 20, y + h // 2 - 6, x + 170, y + h // 2 - 6, (120, 130, 150))
    for i in range(6):
        cv.disc(x + 30 + i * 30, y + h - 16, 3, WHITE)
    cv.text(x + 8, y + h - 12, "AUKUS", WHITE, 1)


def scene_zelenskyy(cv, x, y, w, h):
    cv.vgrad(x, y, w, h, (200, 215, 235), (240, 240, 235))
    flag_ua(cv, x + 10, y + 10, 44, 26)
    cv.rect(x + w - 58, y + 10, 48, 26, WHITE)
    cv.rect(x + w - 58, y + 10, 48, 9, BLUE)
    cv.rect(x + w - 58, y + 27, 48, 9, RED2)
    cv.rect(x + w // 2 - 42, y + h - 40, 84, 40, (90, 70, 50))
    cv.rect(x + w // 2 - 48, y + h - 48, 96, 8, DARK)
    cv.disc(x + w // 2, y + h - 66, 14, (240, 200, 160))
    cv.rect(x + w // 2 - 16, y + h - 54, 32, 12, NAVY)
    cv.line(x + w // 2 - 20, y + h - 48, x + w // 2 - 30, y + h - 66, BLACK)
    cv.line(x + w // 2 + 20, y + h - 48, x + w // 2 + 30, y + h - 66, BLACK)
    cv.disc(x + w // 2 - 30, y + h - 68, 4, BLACK)
    cv.disc(x + w // 2 + 30, y + h - 68, 4, BLACK)


# ------------------------------------------------------------------- stories
# (num, region, headline, body) for the 11 illustrated stories.
LEADS = [
    (1, "GLOBAL", "COP31: FINAL DEAL TEXT TABLED",
     "PRESIDENCY SAYS TEXT CAN WIN CONSENSUS. OBJECTIONS BY 03:00 GMT; APPROVAL SESSION AT 06:00 GMT. FOSSIL-FUEL WORDING STILL OUT."),
    (2, "LATIN AM", "CHAPO ISIDRO SEIZED IN RAID",
     "MEXICAN ARMY STORMS SINALOA HIDEOUT; FAUSTO ISIDRO MEZA FLORES HELD. CARTEL SHAKE-UP FEARED AFTER KINGPIN CAPTURE."),
    (3, "MID EAST", "BAHRAIN TAKES IRAN TO THE UN",
     "KINGDOM DEMANDS UN ACTION OVER IRAN ATTACKS. IDF SAYS IT STRUCK SOUTH LEBANON TARGETS OVERNIGHT."),
]
SMALL = [
    (4, "EUROPE", "UK AND DUTCH PLEDGE UKRAINE AID", "BURNHAM AND YTTEN VOW SUPPORT", scene_uknl),
    (5, "ASIA", "MODI OPENS NITISH SETU BRIDGE", "PATNA TO VAISHALI LINK OPENS", scene_bridge),
    (6, "EUROPE", "ESTONIA TO SHUT RUSSIA BORDER", "MOSCOW DECRIES NEW IRON CURTAIN", scene_estonia),
    (7, "ASIA", "JAPAN TO TRAIN LIVE-FIRE IN INDIA", "FIRST LIVE-FIRE USE OF INDIAN RANGES", scene_japan_india),
    (8, "N AMERICA", "NFL GOES TO MEXICO CITY", "49ERS V VIKINGS AT ESTADIO BANORTE", scene_nfl),
    (9, "EUROPE", "WILLIAM COVERS 10,000 FOREST CREW", "INSURANCE FOR TEMPORARY STAFF", scene_william),
    (10, "OCEANIA", "AUKUS IS NEXT TEST FOR AUSTRALIA", "ANALYSIS: PACT STRAINS JAKARTA TIES", scene_aukus),
    (11, "EUROPE", "ZELENSKYY: SHENZHEN LET PUTIN DOWN", "SUMMIT QUITE DISAPPOINTING FOR MOSCOW", scene_zelenskyy),
]
LEAD_SCENES = [scene_cop31, scene_chapo, scene_bahrain]

# (num, region, one-line brief) — 35 briefs, "ALSO ON SUNDAY".
BRIEFS = [
    (12, "N AMERICA", "TRUMP SIGNS LAW ROUNDING CASH PAYMENTS TO NEAREST 5 CENTS"),
    (13, "N AMERICA", "PENTAGON CURBS US-CANADA MILITARY SOCIALISING, REPORTS SAY"),
    (14, "N AMERICA", "FBI PROBES APPARENT HACK OF ITS CRIMINAL DATABASE"),
    (15, "N AMERICA", "TRUMP TOLD EUROPEAN LEADERS OF HEAVY UKRAINE AID, ZELENSKYY SAYS"),
    (16, "N AMERICA", "NAVY SHIPBUILDING PLAN WOULD BUST BUDGET BY BILLIONS, CBO FINDS"),
    (17, "LATIN AM", "LATAM LEADERS MEET UAE ENVOYS AT CAP CANA DIALOGUE"),
    (18, "LATIN AM", "RIVER PLATE V LANUS IN ARGENTINE PLAY-OFFS TONIGHT"),
    (19, "LATIN AM", "TIGRES V AMERICA IN LIGA MX TONIGHT"),
    (20, "MID EAST", "IDF LAUNCHES NEW STRIKES ON SOUTH LEBANON AREAS"),
    (21, "MID EAST", "US BACKS A STRONG, UNITED, RESILIENT KURDISTAN, STATE DEPT SAYS"),
    (22, "MID EAST", "ISRAEL ACCUSES HAMAS OF TIGHTENING ITS GRIP ON GAZA"),
    (23, "ASIA", "AIR INDIA EXTENDS JEDDAH FLIGHT SUSPENSION TO NOVEMBER 24"),
    (24, "ASIA", "NIKKEI: SHENZHEN WAS BRO HUGS, NO DEALS - A WIN FOR BEIJING"),
    (25, "ASIA", "JAPAN WEIGHS SCALING BACK MISSILE AND WARSHIP PURCHASES"),
    (26, "ASIA", "ICMR COMPLETES 100 TECH TRANSFERS, SIGNS 20 LICENCES"),
    (27, "ASIA", "AKVAN AFTERMATH: 14 FLIGHTS CANCELLED AT RANCHI AIRPORT"),
    (28, "AFRICA", "GAMBIA INTERCEPTS 491 WOULD-BE IRREGULAR MIGRANTS"),
    (29, "AFRICA", "LIBYA NATIONAL FINE ARTS EXHIBITION OPENS IN TRIPOLI"),
    (30, "AFRICA", "ECOWAS LAUNCHES WOMEN LEADERSHIP SCHEME FOR GREEN TRANSITION"),
    (31, "AFRICA", "WALMART HEIR PLEDGES $29.2M TO AFRICAN WILDLIFE PARKS"),
    (32, "AFRICA", "COTE D'IVOIRE SNATCH LATE AFCON QUALIFIER DRAW V GAMBIA"),
    (33, "OCEANIA", "CUMMINS KEEPS TEST CAPTAINCY WITH UNANIMOUS SUPPORT"),
    (34, "OCEANIA", "TAIWAN GIVES $20M FOR MARSHALL ISLANDS SME LOANS"),
    (35, "OCEANIA", "USS FRANK CABLE MAKES PORT VISIT TO SAIPAN"),
    (36, "OCEANIA", "VANUATU AND CHINA SIGN DEAL FOR 3,000 SOLAR STREETLIGHTS"),
    (37, "OCEANIA", "NEW ZEALAND TO FUND FEIAWA PARK SEAFRONT STAGE IN 2027"),
    (38, "GLOBAL", "CRUDE OIL FUTURES FALL MORE THAN 3%"),
    (39, "EUROPE", "LIVERPOOL V MANCHESTER UNITED AT ANFIELD TODAY, 16:30 GMT"),
    (40, "EUROPE", "HULL CITY V BRIGHTON IN THE PREMIER LEAGUE TODAY"),
    (41, "EUROPE", "BARCELONA V VILLARREAL IN LA LIGA TODAY"),
    (42, "EUROPE", "ATALANTA V INTER IN SERIE A TONIGHT"),
    (43, "EUROPE", "DUCHESS OF CAMBRIDGE TELLS CANCER JOURNEY IN HEAL FILM"),
    (44, "EUROPE", "FRANCE ACTS ON CHILD SEXUAL ABUSE IN SCHOOLS"),
    (45, "EUROPE", "DENMARK EXPELS RUSSIAN MILITARY ATTACHE OVER ALLEGED PLOT"),
    (46, "EUROPE", "CHILD KILLED IN STRIKE ON KRYVYI RIH, ZELENSKYY HOME CITY"),
]

TIMELINE = [
    ("00:05", "CHAPO SEIZED"),
    ("00:30", "COP31 DEAL TEXT"),
    ("03:00", "OBJECTIONS DUE"),
    ("04:00", "NITISH SETU"),
    ("06:00", "COP31 APPROVAL"),
    ("16:30", "LIVERPOOL V UTD"),
]

NUMBERS = [
    ("200", "DELEGATIONS AT COP31"),
    ("10,000", "FOREST STAFF COVERED"),
    ("3,000", "SOLAR LIGHTS, VANUATU"),
    ("491", "MIGRANTS OFF GAMBIA"),
    ("$29.2M", "WILDLIFE PARKS PLEDGE"),
    ("100", "TECH TRANSFERS, ICMR"),
]

DATE_CHECK = [
    "PERU M6.9 QUAKE - FIRST REPORTED 21 NOV, 00:09 UTC",
    "KYIV MASS ATTACK, 3 BRIDGES HIT - 20 NOV",
    "IRAN STRIKES ON KUWAIT AND BAHRAIN BASES - 19 NOV",
    "ANTHROPIC SHARES FALL 9.5% AFTER IPO - 20 NOV",
    "UK-EU BREXIT RESET DEAL - 20 NOV",
    "SHENZHEN SUMMIT AND ICJ MYANMAR RULING - 19 NOV",
    "POLAND MISSILE AND DRONE INCURSION - 20 NOV",
    "CYCLONE AKVAN LANDFALL - 20 NOV",
]

# (lon, lat) per story number for the map pins and dots.
GEO = {
    1: (30.7, 36.9), 2: (-107.0, 25.0), 3: (50.5, 26.2), 4: (-0.1, 51.5),
    5: (85.1, 25.6), 6: (24.7, 59.4), 7: (77.2, 28.6), 8: (-99.1, 19.4),
    9: (-0.6, 51.5), 10: (149.1, -35.3), 11: (30.5, 50.4),
    12: (-77.0, 38.9), 13: (-79.4, 43.7), 14: (-77.0, 38.9), 15: (-77.0, 38.9),
    16: (-77.0, 38.9), 17: (-68.7, 18.5), 18: (-58.4, -34.6), 19: (-99.1, 19.4),
    20: (35.5, 33.3), 21: (44.4, 36.2), 22: (34.5, 31.5), 23: (77.2, 28.6),
    24: (113.9, 22.3), 25: (139.7, 35.7), 26: (77.2, 28.6), 27: (85.3, 23.3),
    28: (-16.6, 13.4), 29: (13.2, 32.9), 30: (-1.2, 6.7), 31: (28.0, -26.2),
    32: (-4.0, 5.3), 33: (151.2, -33.9), 34: (171.4, 7.1), 35: (145.7, 15.2),
    36: (168.3, -17.7), 37: (174.8, -41.3), 38: (0.0, 20.0), 39: (-2.9, 53.4),
    40: (-0.3, 53.7), 41: (2.1, 41.4), 42: (9.7, 45.7), 43: (-0.1, 51.5),
    44: (2.3, 48.9), 45: (12.6, 55.7), 46: (33.4, 47.9),
}

# Rough land boxes (lon0, lat0, lon1, lat1) for the dotted world map.
LAND = [
    (-168, 15, -55, 70), (-60, 55, -20, 83), (-80, 8, -35, -5),
    (-80, -5, -35, -55), (-12, 36, 40, 70), (-10, 58, 2, 62),
    (-18, 5, 50, 35), (-18, -35, 50, 5), (40, 5, 180, 75),
    (95, -10, 141, 28), (113, -40, 154, -10), (129, 31, 146, 46),
    (166, -47, 178, -34),
]


# Pins are nudged apart where two stories share one spot on the map.
PIN_POS = {1: (27.0, 35.0), 2: (-112.0, 28.0), 5: (88.0, 22.0),
           7: (74.0, 31.0), 9: (-3.2, 55.9)}


def draw_map(cv, x, y, w, h):
    cv.rect(x, y, w, h, (228, 238, 244))
    cv.outline(x, y, w, h, INK, 2)
    cv.text(x + 8, y + 6, "WHERE IT HAPPENED", NAVY, 1)
    mx0, my0, mw, mh = x + 6, y + 20, w - 12, h - 44
    for gx in range(0, mw, 5):
        for gy in range(0, mh, 5):
            lon = -180 + (gx / mw) * 360
            lat = 75 - (gy / mh) * 135
            for (a, b, c2, d) in LAND:
                if a <= lon <= c2 and b <= lat <= d:
                    cv.px(mx0 + gx, my0 + gy, (150, 160, 175))
                    break
    for num in range(12, 47):
        lon, lat = GEO[num]
        px = mx0 + int((lon + 180) / 360 * mw)
        py = my0 + int((75 - lat) / 135 * mh)
        cv.disc(px, py, 2, GREY)
    for num in range(1, 12):
        lon, lat = PIN_POS.get(num, GEO[num])
        px = mx0 + int((lon + 180) / 360 * mw)
        py = my0 + int((75 - lat) / 135 * mh)
        cv.disc(px, py, 7, RED)
        cv.ring(px, py, 7, WHITE, 1)
        lab = str(num)
        cv.text(px - (3 if len(lab) == 1 else 6), py - 3, lab, WHITE, 1)
    cv.text(x + 8, y + h - 18, "RED PINS = ILLUSTRATED STORIES, GREY DOTS = BRIEFS", GREY, 1)


# ------------------------------------------------------------------- render
def render():
    cv = Canvas(W, H, CREAM)
    cv.rect(0, 0, W, 8, NAVY)
    cv.rect(0, H - 8, W, 8, NAVY)

    # ---- masthead
    cv.rect(8, 8, 1008, 104, NAVY)
    cv.rect(8, 8, 1008, 4, GOLD)
    cv.rect(8, 108, 1008, 4, GOLD)
    cv.text(24, 20, "THE WORLD IN ONE PAGE", GOLD, 2)
    cv.text(1024 - 24 - text_width("NO. 22 NOV 2026", 1), 24, "NO. 22 NOV 2026", WHITE, 1)
    cv.ctext(512, 42, "SUNDAY 22 NOVEMBER 2026", WHITE, 4)
    cv.ctext(512, 88, "46 STORIES FROM EVERY REGION  -  COP31 DEAL  *  CHAPO ISIDRO HELD  *  GULF ON EDGE",
             (200, 210, 230), 1)

    # ---- region strip (counts computed from the numbered story list)
    counts = {}
    for _, r, _, _ in LEADS:
        counts[r] = counts.get(r, 0) + 1
    for _, r, _, _, _ in SMALL:
        counts[r] = counts.get(r, 0) + 1
    for _, r, _ in BRIEFS:
        counts[r] = counts.get(r, 0) + 1
    assert sum(counts.values()) == 46, counts
    order = ["EUROPE", "ASIA", "N AMERICA", "OCEANIA", "AFRICA", "LATIN AM", "MID EAST", "GLOBAL"]
    x = 8
    cw = 1008 // len(order)
    for reg in order:
        cv.rect(x, 118, cw - 4, 26, REGION_COLORS[reg])
        cv.ctext(x + (cw - 4) // 2, 126, "%s %d" % (reg, counts[reg]), WHITE, 1)
        x += cw

    # ---- UTC timeline
    cv.rect(8, 150, 1008, 28, PAPER)
    cv.outline(8, 150, 1008, 28, INK, 1)
    cv.text(16, 159, "SUNDAY IN UTC", RED, 1)
    tx = 150
    tw = (1008 - 150) // 6
    for t, label in TIMELINE:
        cv.text(tx, 159, t, NAVY, 1)
        cv.text(tx + 42, 159, label, INK, 1)
        tx += tw

    # ---- three lead stories
    lx = 8
    for i, (num, reg, head, body) in enumerate(LEADS):
        lead_card(cv, lx, 186, 328, 210, num, reg, head, body, LEAD_SCENES[i])
        lx += 336

    # ---- eight more illustrated stories
    sx = 8
    for i, (num, reg, head, body, scene) in enumerate(SMALL[:4]):
        small_card(cv, sx, 404, 244, 136, num, reg, head, body, scene)
        sx += 252
    sx = 8
    for i, (num, reg, head, body, scene) in enumerate(SMALL[4:]):
        small_card(cv, sx, 548, 244, 128, num, reg, head, body, scene)
        sx += 252

    # ---- six numbers
    cv.rect(8, 682, 1008, 32, NAVY2)
    cv.text(16, 697, "SIX NUMBERS", GOLD, 1)
    nx = 150
    nw = (1008 - 150) // 6
    for big, label in NUMBERS:
        cv.text(nx, 686, big, YELLOW, 2)
        cv.text(nx, 702, label, WHITE, 1)
        nx += nw

    # ---- briefs, left column
    cv.text(8, 718, "ALSO ON SUNDAY", RED, 2)
    cv.line(8, 734, 648, 734, RED)
    by = 736
    for num, reg, line in BRIEFS:
        cv.rect(8, by, 22, 8, REGION_COLORS[reg])
        cv.text(10, by, str(num), WHITE, 1)
        cv.text(34, by, line, INK, 1)
        by += 8

    # ---- map, date check, sources, right column
    draw_map(cv, 656, 718, 360, 170)
    dy = 896
    cv.rect(656, dy, 360, 90, (255, 235, 235))
    cv.outline(656, dy, 360, 90, RED, 2)
    cv.text(664, dy + 5, "DATE CHECK - NOT TODAY'S NEWS", RED, 1)
    yy = dy + 17
    for line in DATE_CHECK:
        cv.text(664, yy, line, INK, 1)
        yy += 9
    cv.text(656, 998, "SOURCES: REUTERS, AP, BBC, JAGRAN, NIKKEI,", GREY, 1)
    cv.text(656, 1006, "FOCUS TAIWAN, PANA, DAILY POST, EIN", GREY, 1)
    return cv


def main():
    cv = render()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(cv))
    print("wrote", path)


if __name__ == "__main__":
    main()
