# Gospel Talks by Ori: style pack

Ori's style for reel-kit, built from the Gospel Talks brand sheet: soft, coastal, calm. The headline formula is
wide caps + one italic word. First used on the episode "Let the Word Diagnose You" (hi-fi).

| file | what it is |
|---|---|
| `style.json` | the pack: fonts, colours, caption settings, modes (`kit/STYLE_PACK.md`) |
| `STYLE.md` | the style in words: type, colour rules, footage, what never to do |
| `brand-extra.css` | the two expressive faces as tokens for cards: `--font-wide`, `--font-italic`, `.wide`, `.ital` |
| `caption-look.html` | an effect (layer `over`) that loads Archivo Expanded in the composition and styles the captions |
| `fetch_wide_font.py` | downloads Archivo Expanded Black from Google Fonts (the one face `style.py` can't fetch) |
| `footage/` | the footage look: a bright, airy grade (matched to Ori's beach photo) and a softly blurred background behind the speaker |

## Fonts and colours
- Headlines: Archivo Expanded Black, caps. Emphasis word: Instrument Serif Italic. Labels: JetBrains Mono, caps,
  spaced. Body and captions: Archivo.
- The pack's `caption` role is Instrument Serif Italic. In hi-fi that role is otherwise unused, so it carries the
  italic emphasis word (`--font-italic`).
- Canvas `#EFE8D8` (main ground), Breeze `#CED8E2` and Mist `#C6D2CE` (soft grounds), Lagoon `#8A9E9F`
  (shapes and circles, never text), Marine `#6D7AA4` (the hero colour, once per screen), Slate `#555E6D` (text).

## Use it
1. Make it the current pack (keep a copy of the one there first):
   ```
   cp styles/gospel-talks/style.json styles/gospel-talks/STYLE.md ~/reel-kit/style/
   ~/reel-kit/.venv/bin/python pipeline/style.py ~/reel-kit/style/style.json
   ```
2. New project as usual (`pipeline/new.py`). Then add the caption look and its font:
   ```
   mkdir -p <project>/fx/look
   cp styles/gospel-talks/caption-look.html <project>/fx/look/fx.html
   python3 styles/gospel-talks/fetch_wide_font.py <project>/fx/look <project>/style/fonts
   cp styles/gospel-talks/brand-extra.css <project>/style/
   ```
   and in `edit.py` add `dict(id="look", layer="over", at=0.0, end="end")` to `FX`.
3. Cards: copy `<project>/style/brand-extra.css` and `<project>/style/fonts/` into each card folder and link
   `brand-extra.css` after `card.css`. Use `.wide` for the caps line and `.ital` for the one italic word.
4. Footage look, after `cut.py` and `cutout.py` (needs the cutout for the whole cut):
   ```
   cp styles/gospel-talks/footage/look.py styles/gospel-talks/footage/look_render.py <project>/work/
   ~/reel-kit/.venv/bin/python styles/gospel-talks/footage/mkcube.py <project>/work <project>/work/look.cube
   ~/reel-kit/.venv/bin/python -I <project>/work/look_render.py <project> 7
   ```
   It writes `public/clean.mp4` (graded, background blurred, the speaker sharp) and `public/subject.webm` (the graded
   speaker for the cutout windows); the originals stay in `assets/`. The last number is the blur strength (7 is
   "a little blur"). The grade was tuned for a bright white room; adjust `MIDS`, `BANDS` and `CREAM` in `look.py` for
   another room, then rebuild the cube.
