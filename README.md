# reel-kit

An AI agent skill that turns one talking-head clip into a finished vertical video, in your own style. Give it a
take; it cuts the edit, writes the captions, builds the motion graphics and lays the sound, then shows you a
storyboard to comment on before anything renders.

Works with Claude Code and Codex. Runs on your computer, on your footage. Free and open source.

## What it makes
- A clean edit of one take: dead air out, the last good take of every line, J-cuts on every join, two framings
  from one camera, lip sync checked before and after the render.
- Captions that land on the words, in your fonts and colours.
- Words and numbers behind your head (you stay in front of the type).
- Hand-built motion-graphic cards for the numbers in your script: charts that draw, figures that roll, data kept
  to scale.
- Sound effects under every visual moment, mixed under your voice to streaming loudness (-14 LUFS).
- A storyboard first: every beat with real frames, what moves, what you hear, and what the agent needs from you.
  Leave notes on any beat. Nothing renders until you say go.

## Two modes
- **Hi-fi**: produced. A sit-down take, full-screen data cards, type behind your head.
- **Lo-fi**: selfie. A phone take where you never leave the frame; screenshots and clips land on top of you or
  behind your head, captions light up word by word, native-looking text boxes carry the hook and the call to action.

## Your style, not ours
The first time you run it, the agent builds your style pack:
1. **Have a brand file?** A brand guide, a DESIGN.md, a PDF or your website. It reads your fonts and colours.
2. **No?** Send 2 or 3 links to videos whose style you like. It studies them: pace, captions, colour, motion.
3. **Neither?** Four quick questions.

Then it shows you a style board, your type and colours with captions on a frame of your own footage and a few
cards in your look, and asks if it looks like you. Change anything, any time: "update my style".

The pack lives in `~/reel-kit/style/`, outside the skill, so updates never touch it. Each video keeps a copy of
the style it was made with.

## Install
You need a Mac or Linux computer (Windows is untested; WSL should work), plus ffmpeg, Node 18+ and Python 3.10+.
The setup script checks all of it and prints the exact fix for anything missing.

**Claude Code**
```sh
git clone https://github.com/justynberk/reel-kit ~/.claude/skills/reel-kit
python3 ~/.claude/skills/reel-kit/setup/setup.py
```
Then type `/reel-kit` in Claude Code.

**Codex** (CLI, IDE extension or app)
```sh
git clone https://github.com/justynberk/reel-kit ~/.agents/skills/reel-kit
python3 ~/.agents/skills/reel-kit/setup/setup.py
```
Then type `$reel-kit`, or ask Codex to edit your clip with reel-kit. Codex runs commands in a sandbox that blocks
the browser the kit renders with, so give the session Full access (the permissions menu in the app, or
`codex --sandbox danger-full-access`); setup tells you if it can't render.

**Claude Cowork** (desktop app): download `reel-kit.zip` from the latest release, then Customize > Skills, + >
Create skill > Upload a skill. Turn on code execution and file creation. Rendering needs Cowork's sandbox to install ffmpeg and
Node; if it can't, use Claude Code.

**ChatGPT**: skills there run in OpenAI's hosted sandbox, which can't install the video tools or reach your
footage. Use Codex with the same account instead.

To update later: `git -C ~/.claude/skills/reel-kit pull` (or the Codex path), then run setup again.

Setup takes a few minutes the first time: it creates the kit's own Python environment, downloads GSAP and the
render browser, and checks everything else. All of it goes in `~/reel-kit/`, next to your style and your projects,
never inside the skill folder. Run it again any time; it only fixes what's missing.

## Make a video
1. Run the skill with your clip, the mode and what it's about:
   `/reel-kit hi-fi ~/Videos/take.mov, about this article: <link>`
2. The agent cuts the take, plans every beat, builds the cards, and sends you the storyboard with a list of
   anything it needs from you (a screen recording, a screenshot of your dashboard), or "nothing needed".
3. Leave notes on the storyboard. Send what it asked for. Say go.
4. The finished video and a phone-size copy land next to your clip.

The storyboard opens as a Claude artifact with inline comments when you use Claude, or as a local page on your
computer anywhere else (your notes save to a file the agent reads).

## Extend it (optional)
Everything above works out of the box with real footage, real screenshots and the kit's own sound effects. Connect
any of these to your agent to go further; the skill uses what it finds and skips what it doesn't.

| Add-on | Unlocks | How |
|---|---|---|
| [Higgsfield](https://higgsfield.ai) MCP | Generated images and video for beats no real footage can show, plus music and sound effects | Add `https://mcp.higgsfield.ai/mcp` as an MCP server or connector and sign in |
| [ChatCut](https://chatcut.io) | Original music for each video and a sound-effects library | Install ChatCut's plugin or connector and sign in |
| [ElevenLabs](https://github.com/elevenlabs/elevenlabs-mcp) MCP | Generated sound effects from a description | Add the official ElevenLabs MCP server with your API key |
| [Suno](https://suno.com), or any track you own | Your own music under the video | Download the track, drop it in the project's `audio/` folder, tell the agent to use it |

Music is off by default. Most creators add a track when they post (Instagram, Edits, TikTok, CapCut), where it
can be a licensed trending sound. Generated images are used sparingly and tagged on the storyboard so you can cut
any of them before the render.

## What's inside
```
SKILL.md              the instructions every agent reads
modes/                hi-fi and lo-fi: how each edit is structured
onboarding/           style setup: ONBOARDING.md, refs.py (studies inspiration videos), board.py (the style board)
pipeline/             cut, transcribe, cutout, build, mix, storyboard, QA, render (Python)
kit/                  the composition's CSS, the card template and brief, the style token contract
cards/                the motion-graphic card library (LIBRARY.md), each card driven by your tokens
audio/sfx/            sound effects, synthesized from scratch for this kit (CC0)
storyboard/           the review page and a local server for hosts without artifacts
examples/             a reference edit.py for each mode, and three sample style packs
setup/                setup.py and package.py
```

## Credits and licenses
reel-kit is MIT licensed (see `LICENSE`). It stands on:
- [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0): renders the video from HTML. Run through
  npx, pinned to one version.
- [GSAP](https://gsap.com) (GreenSock standard license, free): the animation timeline. Downloaded by setup, not
  included here.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (MIT): word-level transcription.
- [Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting) (GPL-3.0): the optional smoother cutout.
  Its model is downloaded only if you run `setup.py --matte`; none of its code is in this repo.
- Fonts come from [Google Fonts](https://fonts.google.com) (SIL Open Font License), fetched for your pack.
- The sound effects are synthesized by `audio/make_sfx.py` and released CC0.
- The $1 bill in the `dollar-split` card is a US government work in the public domain.
