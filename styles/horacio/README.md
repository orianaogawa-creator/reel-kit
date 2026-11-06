# Horacio: style pack

The look for Horacio's talking-head reels ("Promesas de Dios para ti"): a yapping edit with bold, aesthetic but
masculine type. First used on "Pensamientos Cautivos" (Nov 2026). `ref-hook.jpg` and `ref-title.jpg` show it.
Every video for him uses this pack unchanged; only the words change.

## The rules
- **Footage is never touched.** No colour, grade, zoom, crop, blur or filters. The only processing is scaling to
  1080x1920 for delivery. The keyframes live on the type, not on the picture.
- **Cut:** best (last clean) take of each line. Every repeat and false start goes, and pauses over 0.32 s shrink
  to 0.2 s (`edl.py` `tighten`). Target 2:00 or less. Drop greetings ("Hola") and side remarks first.
- **Language:** Spanish. Titles and captions are in Spanish, with accents corrected (`qué`, `cuándo`, `Párate`).
- **Hook (0 to 5.2 s):** a small kicker "PROMESAS DE DIOS PARA TI", then a 3-line question in Anton 104 px whose
  last line is the gold payoff (e.g. `¿QUÉ PENSAMIENTO / TE ESTÁ ROBANDO / *LA PAZ?*`). Lines land 0.45 s apart.
- **Top titles, one per idea:**
  - A kicker in Oswald 600, 36 px, caps, tracked .2em, white, with two short gold lines that draw out from it.
  - Then 1 to 3 lines in Anton 98 px, caps, white, with the key word or words in gold `#FFC54D`.
  - Each word punches in on the moment it is spoken: it starts at 1.55x (1.9x for gold), blurred, and settles
    with a back-ease.
  - A gold underline then sweeps under the last line. The block slowly pushes in by 3.5% while it is up, and
    lifts and fades over 0.28 s when the next idea starts.
  - Big one-word moments ("ORA CONMIGO", "AMÉN") use size 2 (150 px).
  - Scripture gets the reference as its kicker (e.g. "2 Corintios 10:5").
- **No boxes or scrims.** Readability comes from the dark halo shadow (`--halo`, `--goldhalo`), which reads on a
  bright car roof.
- **Safe zone:** titles sit at x 140 to 940 with their top at 250 px or lower, and must stay above his head
  (about 640 px). Use at most 3 Anton lines.
- **Captions:**
  - Placement: on the chest at top 1330 px, 1 to 3 words per chunk.
  - Type: Oswald 700, 74 px, caps, white.
  - Key words are gold. Words not yet spoken show at 62% opacity.
  - Each chunk rises in over 0.14 s.
- **Sound:** a whoosh (`whoosh-short`, 0.12) as each idea comes in and a pop (0.15) on every gold word. The
  prayer section is softer: pops at 0.10, no whooshes, and a chime on the prayer opening and on "Amén". Voice is
  at about -15 LUFS (`mix.py 15`), with a limiter.
- **Delivery:** 1080x1920, 30 fps, HEVC 2-pass at about 28 MB (under 30 MB).

## Files
| file | what it is |
|---|---|
| `ov/index.html` | the overlay: titles, hook and captions; deterministic `render(t)` |
| `ov/fonts/` | Anton, Oswald, Cormorant Garamond (woff2, Google Fonts, OFL) |
| `tools/tx.py` | faster-whisper `medium`, auto language, word timestamps: `tx.py <wav> <out-prefix>` |
| `tools/chunks.py` | per-silence-chunk transcript to find exact take boundaries |
| `tools/edl.py` | the beats: `(id, line, [(in, out)])` in source seconds, with pause tightening |
| `tools/voice.py`, `tools/aroll.py` | sample-exact voice and frame-exact a-roll (no colour change) |
| `tools/words.py` | word fixes, caption chunks, `EMPH` gold words, `HOOK` and titles (`L`, `LW`, `ttl`) |
| `tools/cap.js` | Playwright capture of the overlay to transparent PNGs |
| `tools/mix.py` | sound effects under the voice -> `proj/master.wav` |
| `tools/stills.sh` | still frames with the overlay, for checking the layout |
| `sfx/` | pop, whoosh-short, chime |

## Use it
```
cp -r styles/horacio ~/reel-edits/<slug> && cd ~/reel-edits/<slug> && mkdir -p proj/seg proj/text
export PROJ=$PWD SRC=/path/to/clip.mov ; PY=<venv with faster-whisper>/bin/python
ffmpeg -i "$SRC" -vn -ac 1 -ar 16000 proj/a16.wav ; ffmpeg -i "$SRC" -vn -ac 1 -ar 48000 proj/a48.wav
ffmpeg -i proj/a16.wav -af silencedetect=noise=-38dB:d=0.3 -f null - 2>&1 \
  | grep -o 'silence_\(start\|end\): [0-9.]*' | awk '{printf "%s%s", $2, (NR%2?"-":" ")}' > proj/sil.txt
$PY -I tools/tx.py proj/a16.wav proj/raw && $PY -I tools/chunks.py proj   # read both, pick the takes
# edit B in tools/edl.py, then:
python3 tools/edl.py && python3 tools/voice.py && python3 tools/aroll.py
$PY -I tools/tx.py proj/voice16.wav proj/cut                               # output-time words
# edit T, EMPH, HOOK and H in tools/words.py (indices from proj/cut_words.json), then:
python3 tools/words.py && tools/stills.sh 60,600,1200                      # check layout
node tools/cap.js proj/text && python3 tools/mix.py 15
ffmpeg -i proj/aroll.mp4 -framerate 30 -i proj/text/%04d.png -i proj/master.wav \
  -filter_complex "[1:v]format=rgba[t];[0:v][t]overlay=format=auto,format=yuv420p[v]" -map "[v]" -map 2:a \
  -c:v libx264 -crf 14 -c:a aac -b:a 256k -shortest out/master.mp4
```
The `edl.py` and `words.py` here still hold the "Pensamientos Cautivos" beats as a worked example. Replace them
for each new video.
