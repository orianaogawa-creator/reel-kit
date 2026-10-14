"""The Gospel Talks footage look, matched to Ori's beach photo (bright and airy): whites clean with a touch of cream,
skin peach rather than orange, mids a little brighter, blues pastel and a touch toward periwinkle, greens sage, blacks
a clean charcoal; the room behind the speaker softly blurred (a shallow depth of field) while she stays sharp. Tuned on
the first episode (a bright white living room, iPhone HDR tone-mapped to SDR); for another room adjust MIDS, BANDS
and CREAM. grade(rgb uint8 HxWx3) -> float32 0..1 ; composite_u8(rgb uint8, alpha uint8, sigma) -> uint8"""
import numpy as np
from scipy.ndimage import gaussian_filter

MIDS = 0.26                  # brighter mids: L += MIDS * x^1.5 * (1 - x) * 100   (x = L / 100; blacks and whites stay put)
SAT = 0.93                   # overall chroma
CMAX = 50.0                  # strong colours roll off softly: C -> CMAX * tanh(C / CMAX)
#            hue centre, half-width (deg), chroma scale, hue shift (deg), lightness (+L)
BANDS = [(48.0, 30.0, 0.90, 0.0, 1.0),      # skin and oranges: peach, not orange; a little brighter
         (88.0, 18.0, 0.70, 0.0, 0.0),      # yellows (lamp glow, wood)
         (130.0, 35.0, 0.72, -6.0, 1.5),    # greens toward sage
         (262.0, 40.0, 1.02, 4.0, 0.5)]     # blues: pastel, a touch toward periwinkle (the window)
CREAM = 0.72                 # near-whites keep only this much of their warm tint (clean, a touch of cream)
CHARCOAL = 0.45              # near-blacks keep only this much of their tint (no purple in the black shirt)

_M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]], np.float64)
_MI = np.linalg.inv(_M)
_WP = np.array([0.95047, 1.0, 1.08883])


def _to_lab(c):
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    xyz = lin @ _M.T / _WP
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return 116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])


def _from_lab(L, a, b):
    fy = (L + 16) / 116
    f = np.stack([fy + a / 500, fy, fy - b / 200], -1)
    xyz = np.where(f > 6 / 29, f ** 3, 3 * (6 / 29) ** 2 * (f - 4 / 29)) * _WP
    lin = np.clip(xyz @ _MI.T, 0, None)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def _smooth(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _band(h, centre, width):
    d = np.abs(((h - centre + 180) % 360) - 180)
    return 0.5 + 0.5 * np.cos(np.pi * np.clip(d / width, 0, 1))      # raised cosine: 1 at the centre, 0 at the edge


def grade(rgb):
    c = rgb.astype(np.float64) / 255.0
    L, a, b = _to_lab(c)
    C = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a)) % 360
    colour = _smooth(C, 3.0, 14.0)                  # hue moves only act on real colour, never on near-greys
    scale = np.full_like(C, SAT)
    dh = np.zeros_like(C)
    dL = np.zeros_like(C)
    for centre, width, s, shift, lift in BANDS:
        w = _band(h, centre, width) * colour
        scale *= 1 + (s - 1) * w
        dh += shift * w
        dL += lift * w * _smooth(L, 15, 45) * (1 - _smooth(L, 85, 98))
    # near-whites: a touch of cream, no yellow; near-blacks: clean charcoal
    warm = _band(h, 70.0, 60.0)
    low_c = 1 - _smooth(C, 8.0, 20.0)
    scale *= 1 + (CREAM - 1) * warm * low_c * _smooth(L, 70, 90)
    scale *= 1 + (CHARCOAL - 1) * low_c * (1 - _smooth(L, 20, 42))
    C2 = CMAX * np.tanh(C / CMAX) * scale
    h2 = np.radians(h + dh)
    x = L / 100.0
    L2 = L + MIDS * 100 * np.power(np.clip(x, 0, 1), 1.5) * (1 - x) + dL
    out = _from_lab(np.clip(L2, 0, 100), C2 * np.cos(h2), C2 * np.sin(h2))
    return np.clip(out, 0, 1).astype(np.float32)


def composite(fg, alpha, bg, sigma=7.0):
    """fg, bg: float 0..1 HxWx3 (graded); alpha 0..1 HxW (the speaker). Background blurred by normalized convolution
    over the background only (no dark halo of the speaker smeared into it), at half resolution for speed."""
    H, W = alpha.shape
    m = (1.0 - alpha).astype(np.float32)
    h2, w2 = H // 2, W // 2
    mb = m.reshape(h2, 2, w2, 2).mean((1, 3))
    cb = (bg * m[..., None]).reshape(h2, 2, w2, 2, 3).mean((1, 3))
    s2 = sigma / 2.0
    num = np.stack([gaussian_filter(cb[..., k], s2, mode='nearest') for k in range(3)], -1)
    den = gaussian_filter(mb, s2, mode='nearest')[..., None]
    blur = num / np.maximum(den, 1e-3)
    blur = np.repeat(np.repeat(blur, 2, 0), 2, 1)          # back to full size (smooth anyway)
    a = alpha[..., None]
    out = a * fg + (1 - a) * blur
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


def composite_u8(a, m, sigma=7.0):
    """composite() for speed: a HxWx3 uint8 (graded), m HxW uint8 alpha (255 = the speaker). The background blur
    (normalized over the background only) runs at half size; the blend is exact per pixel."""
    inv = (255 - m).astype(np.float32)
    aw = a.astype(np.float32) * inv[..., None]
    def half(x):                                  # sum of each 2x2 block, by strided views (fast)
        return x[0::2, 0::2] + x[1::2, 0::2] + x[0::2, 1::2] + x[1::2, 1::2]
    inv_h, aw_h = half(inv), half(aw)
    s2 = sigma / 2.0
    den = np.maximum(gaussian_filter(inv_h, s2, mode='nearest'), 1.0)
    blur = np.empty(aw_h.shape, np.float32)
    for k in range(3):
        blur[..., k] = gaussian_filter(aw_h[..., k], s2, mode='nearest') / den
    blur = blur.repeat(2, 0).repeat(2, 1)
    blur += (a.astype(np.float32) - blur) * (m.astype(np.float32)[..., None] * (1.0 / 255.0))
    return np.clip(blur + 0.5, 0, 255).astype(np.uint8)
