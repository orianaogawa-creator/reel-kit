"""look.py's grade() as a 65-point 3D LUT (.cube, R fastest), so ffmpeg can apply it to every frame.
Run: python3 mkcube.py <folder holding look.py> <out.cube>   (needs numpy and scipy, e.g. the kit's .venv)"""
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import look
N = 65
v = np.linspace(0, 1, N, dtype=np.float32)
b, g, r = np.meshgrid(v, v, v, indexing='ij')          # .cube order: R changes fastest, then G, then B
rgb = np.stack([r, g, b], -1).reshape(-1, 1, 3)
out = look.grade((rgb * 255).round().astype(np.uint8)).reshape(-1, 3)
with open(sys.argv[2], 'w') as fh:
    fh.write('TITLE "let the word: clean cool-neutral"\nLUT_3D_SIZE %d\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n' % N)
    for p in out:
        fh.write('%.6f %.6f %.6f\n' % tuple(p))
print('wrote', sys.argv[2], len(out))
