import json, wave, sys, numpy as np
from faster_whisper import WhisperModel
d = sys.argv[1]
w = wave.open(d + '/a16.wav'); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768.0
sil = [tuple(map(float, p.split('-'))) for p in open(d + '/sil.txt').read().split() if '-' in p and p.split('-')[1]]
ch, t = [], 0.0
for s, e in sil:
    if s - t > 0.15: ch.append((t, s))
    t = e
ch.append((t, len(a) / sr))
m = WhisperModel('medium', device='cpu', compute_type='int8')
out = []
for s, e in ch:
    seg = a[int(max(0, s - .05) * sr):int((e + .05) * sr)].astype(np.float32)
    txt = ' '.join(x.text.strip() for x in m.transcribe(seg, language='es', beam_size=5, condition_on_previous_text=False)[0])
    out.append({'s': round(s, 3), 'e': round(e, 3), 't': txt})
    print(f'{s:8.3f}-{e:8.3f} {txt}', flush=True)
json.dump(out, open(d + '/chunks.json', 'w'), indent=1, ensure_ascii=False)
