import json, re, subprocess, sys
import os
P = os.environ.get('PROJ', '.')  # project folder: proj/, ov/, tools/
D = open(P + '/ov/data.js').read()
HL = json.loads(re.search(r'const HL=(.*?);\n', D).group(1))
S = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sfx') + '/'
gain = sys.argv[1]
ev = []
for h in HL:
    soft = h['id'] in ('ora1', 'ora2', 'ora3', 'amen')
    if h['id'] in ('ora1', 'amen'): ev.append(('chime.mp3', h['from'] + .1, .28))
    elif not soft: ev.append(('whoosh-short.mp3', h['from'], .12))
    for l in h['lines']:
        for w in l:
            if w['g'] and w['w'] != '·': ev.append(('pop.mp3', w['t'], .10 if soft else .15))
args, fc, lab = ['-i', P + '/proj/voice.wav'], f'[0:a]volume={gain}dB,alimiter=limit=0.8:attack=3:release=60:level=false,aresample=48000[v];', '[v]'
for k, (f, t, v) in enumerate(ev):
    args += ['-i', S + f]
    fc += f'[{k + 1}:a]aresample=48000,adelay={max(0, int(t * 1000))}:all=1,volume={v}[s{k}];'; lab += f'[s{k}]'
fc += f'{lab}amix=inputs={len(ev) + 1}:normalize=0:duration=first,alimiter=limit=0.84:level=false[a]'
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', *args, '-filter_complex', fc, '-map', '[a]', '-c:a', 'pcm_s24le', P + '/proj/master.wav'], check=True)
print(len(ev), 'sfx')
