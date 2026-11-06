import json, sys
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, info = m.transcribe(src, language=None, word_timestamps=True, vad_filter=False, beam_size=5,
    initial_prompt="Promesas de Dios para ti. Dios, Jesús, Espíritu Santo, la Biblia, la Palabra.")
print('lang', info.language, info.language_probability, flush=True)
W, S = [], []
for s in segs:
    S.append({'start': round(s.start, 2), 'end': round(s.end, 2), 'text': s.text.strip()})
    print(f'{s.start:7.2f}-{s.end:7.2f} {s.text.strip()}', flush=True)
    W += [{'text': w.word.strip(), 'start': round(w.start, 3), 'end': round(w.end, 3)} for w in s.words]
json.dump(W, open(out + '_words.json', 'w'), indent=1, ensure_ascii=False)
json.dump(S, open(out + '_segs.json', 'w'), indent=1, ensure_ascii=False)
