"""Sample-exact voice track of the cut: every piece is exactly frames/30 s of the 48 kHz source, 10 ms fades."""
import json, subprocess
import os
P = os.environ.get('PROJ', '.')  # project folder: proj/, ov/, tools/
E = json.load(open(P + '/proj/edl.json'))
fc, cat = '', ''
for k, p in enumerate(E):
    d = p['frames'] / 30
    fc += (f"[0:a]atrim=start={p['in']:.4f}:duration={d:.5f},asetpts=PTS-STARTPTS,"
           f"afade=t=in:d=0.01,afade=t=out:st={d - 0.012:.5f}:d=0.012,apad=whole_dur={d:.5f}[a{k}];")
    cat += f'[a{k}]'
fc += f"{cat}concat=n={len(E)}:v=0:a=1[a]"
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', P + '/proj/a48.wav', '-filter_complex', fc,
                '-map', '[a]', '-c:a', 'pcm_s24le', '-ar', '48000', P + '/proj/voice.wav'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', P + '/proj/voice.wav', '-ac', '1', '-ar', '16000',
                P + '/proj/voice16.wav'], check=True)
print(sum(p['frames'] for p in E), 'frames')
