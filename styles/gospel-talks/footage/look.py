"""The Gospel Talks footage look: clean and cool-neutral (the yellow pulled out of walls, lamps and wood), and the
room behind the speaker softly blurred (a shallow depth of field) while she stays sharp. Tuned on the first episode
(a bright white living room, iPhone HDR tone-mapped to SDR); adjust WB / YELLOW / LIFT for a different room.
grade(rgb uint8 HxWx3) -> float32 0..1 ; composite_u8(rgb uint8, alpha uint8, sigma) -> uint8"""
import numpy as np
from scipy.ndimage import gaussian_filter

WB = (0.975, 1.0, 1.045)          # R, G, B gains (display space): whites a touch cool, crisp
YELLOW = (45.0, 22.0, 0.60)       # hue centre (deg), half-width, how much saturation comes out of yellows (walls, lamp)
ORANGE = (26.0, 14.0, 0.15)       # a little out of oranges (the lamp glow, wood, skin's yellow cast)
LIFT = 0.93                       # exposure: v ** LIFT (brighter, clean)
SAT = 0.97                        # overall saturation


def rgb_to_hsv(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(-1), c.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r); gg = m & (mx == g) & ~rr; bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    h *= 60.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    h6 = (h / 60.0) % 6
    i = np.floor(h6).astype(np.int8)
    f = h6 - i
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.empty(h.shape + (3,), np.float32)
    for k, (a, b, c) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[..., 0][m], out[..., 1][m], out[..., 2][m] = a[m], b[m], c[m]
    return out


def bump(h, centre, width):
    d = np.abs(((h - centre + 180) % 360) - 180)
    return np.clip(1 - d / width, 0, 1) ** 1.5


def grade(rgb):
    c = rgb.astype(np.float32) / 255.0
    c = np.clip(c * np.array(WB, np.float32), 0, 1)
    h, s, v = rgb_to_hsv(c)
    s = s * SAT * (1 - YELLOW[2] * bump(h, YELLOW[0], YELLOW[1])) * (1 - ORANGE[2] * bump(h, ORANGE[0], ORANGE[1]))
    v = v ** LIFT
    return np.clip(hsv_to_rgb(h, s, v), 0, 1)


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
