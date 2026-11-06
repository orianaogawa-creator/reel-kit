"""Frame-exact a-roll for Part 5: full frame (no crop), no colour change, exactly n frames per piece."""
import json, subprocess, sys, os
import os
P = os.environ.get('PROJ', '.')  # project folder: proj/, ov/, tools/
from concurrent.futures import ThreadPoolExecutor
E = json.load(open(P + '/proj/edl.json'))
SRC = os.environ['SRC']
def frames(f):
    return int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
                               '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip())
def one(k):
    p = E[k]; n = p['frames']; out = f'{P}/proj/seg/{k:02d}.mp4'
    if os.path.exists(out) and frames(out) == n: return k
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-threads', '4', '-ss', f"{p['in']:.3f}", '-t', f"{n / 30 + 0.2:.3f}", '-i', SRC, '-map', '0:v:0',
                    '-vf', 'scale=1080:1920:flags=lanczos,fps=30,tpad=stop_mode=clone:stop_duration=0.2', '-frames:v', str(n),
                    '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', out], check=True)
    got = frames(out)
    if got != n: sys.exit(f'{k}: {got} != {n}')
    print(k, n, flush=True); return k
with ThreadPoolExecutor(4) as ex: list(ex.map(one, range(len(E))))
open(P + '/proj/seg/list.txt', 'w').write(''.join(f"file '{k:02d}.mp4'\n" for k in range(len(E))))
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', P + '/proj/seg/list.txt', '-c', 'copy',
                P + '/proj/aroll.mp4'], check=True)
print('total', frames(P + '/proj/aroll.mp4'), 'want', sum(p['frames'] for p in E))
