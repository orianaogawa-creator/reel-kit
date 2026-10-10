#!/usr/bin/env python3
"""Setup: checks what reel-kit needs on this computer and installs its own pieces. Safe to run again any time.

Run with any Python 3.10+:  python3 setup/setup.py [--check] [--matte]
  --check  report only, change nothing
  --matte  also install PyTorch for pipeline/matte.py (smoother cutouts for lo-fi, about 1 GB)

Prints one STATUS line per piece. A MISSING line ends with the exact fix for this computer. Ends with READY or
NOT READY. Standard library only, so it runs before anything else is installed. Everything it installs goes in
$REEL_KIT_HOME (default ~/reel-kit: .venv/, vendor/, models/), next to the style pack and projects, never inside
the skill folder.
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser(os.environ.get("REEL_KIT_HOME", "~/reel-kit"))
WIN = os.name == "nt"
VENV = os.path.join(HOME, ".venv")                     # everything setup makes lives in HOME: the skill folder may be read-only
VENV_PY = os.path.join(VENV, "Scripts", "python.exe") if WIN else os.path.join(VENV, "bin", "python")
HF = ["npx.cmd" if WIN else "npx", "-y", "hyperframes@0.8.139"]
GSAP_VERSION = "3.15.0"
GSAP_URL = f"https://cdn.jsdelivr.net/npm/gsap@{GSAP_VERSION}/dist/gsap.min.js"
GSAP_PATH = os.path.join(HOME, "vendor", "gsap.min.js")
CHECK = "--check" in sys.argv
OS = "macos" if sys.platform == "darwin" else "windows" if WIN else "linux"
FIX = {
    "ffmpeg": {"macos": "brew install ffmpeg", "linux": "sudo apt install ffmpeg",
               "windows": "winget install --id Gyan.FFmpeg -e   (then reopen the terminal)"},
    "node": {"macos": "brew install node", "linux": "install Node 18+ from https://nodejs.org (apt's is often too old)",
             "windows": "winget install --id OpenJS.NodeJS.LTS -e   (then reopen the terminal)"},
    "python": {"macos": "brew install python@3.12", "linux": "sudo apt install python3 python3-venv",
               "windows": "winget install --id Python.Python.3.12 -e"},
}
ok = True
SANDBOX = os.environ.get("CODEX_SANDBOX")   # Codex marks its sandboxed commands; the render browser can't start in it
FULL_ACCESS = ("give this session full access (Codex: Full access in the permissions menu, or start it with "
               "`codex --sandbox danger-full-access`), then run setup again")


def status(name, good, detail="", fix=""):
    global ok
    ok = ok and good
    line = f"STATUS {name:<10} {'OK     ' if good else 'MISSING'} {detail}"
    if not good and fix:
        line += f"\n           fix: {fix}"
    print(line, flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def version_of(cmd):
    try:
        out = run(cmd)
        return (out.stdout + out.stderr).strip()
    except OSError:
        return ""


FRAME = """<!doctype html><html><head><meta charset="utf-8"><title>render test</title></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="1.000" data-fps="30" data-width="1080" data-height="1920"
 style="width:1080px;height:1920px;background:#222"></div>
<script src="vendor/gsap.min.js"></script>
<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = gsap.timeline({ paused: true }).to({}, { duration: 1 });</script>
</body></html>"""


def render_test():
    """launch the render browser for real: one frame of a one-second composition. READY has to mean it can render"""
    import glob
    import tempfile
    d = tempfile.mkdtemp(prefix="reel-kit-render-test-")
    os.makedirs(os.path.join(d, "vendor"))
    shutil.copy(GSAP_PATH, os.path.join(d, "vendor", "gsap.min.js"))
    shutil.copy(os.path.join(KIT, "kit", "hyperframes.json"), d)
    with open(os.path.join(d, "index.html"), "w") as fh:
        fh.write(FRAME)
    r = run(HF + ["snapshot", "--at", "0.5", "--no-end", "--describe", "false"], cwd=d)
    good = r.returncode == 0 and bool(glob.glob(os.path.join(d, "snapshots", "frame-*.png")))
    out = r.stdout + r.stderr
    if good:
        status("render", True, "the render browser launched and drew a frame")
    elif "MachPortRendezvousServer" in out or "Failed to launch the browser" in out:
        status("render", False, "BLOCKED: this agent's sandbox stops the render browser from starting", FULL_ACCESS)
    else:
        status("render", False, "the test frame failed:\n" + out[-1200:], f"cd {d} && {' '.join(HF)} snapshot --at 0.5")
    if good:
        shutil.rmtree(d, ignore_errors=True)


def find_python():
    """this Python if it is 3.10+, else the newest python3.1x on PATH (or Homebrew's), else None"""
    if sys.version_info >= (3, 10):
        return sys.executable
    names = ["python3.13", "python3.12", "python3.11", "python3.10"] + (["py"] if WIN else [])
    extra = ["/opt/homebrew/bin/python3", "/usr/local/bin/python3"]
    for c in [shutil.which(n) for n in names] + [p for p in extra if os.path.exists(p)]:
        if not c:
            continue
        m = re.search(r"Python 3\.(\d+)", version_of([c, "--version"]))
        if m and int(m.group(1)) >= 10:
            return c
    return None


def main():
    print(f"reel-kit setup on {OS} ({platform.machine()}), kit at {KIT}", flush=True)
    if SANDBOX:
        net = " with the network off" if os.environ.get("CODEX_SANDBOX_NETWORK_DISABLED") else ""
        print(f"note: running inside Codex's sandbox ({SANDBOX}){net}. Rendering launches a headless browser, which "
              f"this sandbox blocks: {FULL_ACCESS}", flush=True)
    if OS == "macos" and not shutil.which("brew"):
        print("note: the macOS fixes below use Homebrew (https://brew.sh)", flush=True)

    # Python 3.10+ for the kit's environment (a stock Mac's python3 is 3.9: look for a newer one first)
    base = find_python()
    status("python", bool(base), (version_of([base, "--version"]) + f" ({base})") if base else platform.python_version(),
           FIX["python"][OS])

    # ffmpeg / ffprobe, with the VP9 encoder the cutout needs
    have = shutil.which("ffmpeg") and shutil.which("ffprobe")
    detail = version_of(["ffmpeg", "-version"]).split("\n")[0][:60] if have else ""
    status("ffmpeg", bool(have), detail, FIX["ffmpeg"][OS])
    if have and "libvpx-vp9" not in version_of(["ffmpeg", "-hide_banner", "-encoders"]):
        print("note: this ffmpeg has no VP9 encoder (libvpx); cutouts behind the speaker need it", flush=True)

    # Node 18+
    v = version_of(["node", "--version"]) if shutil.which("node") else ""
    m = re.match(r"v(\d+)", v)
    status("node", bool(m and int(m.group(1)) >= 18), v, FIX["node"][OS])

    # the kit's own Python environment
    reqs = os.path.join(KIT, "setup", "requirements.txt")
    if not os.path.exists(VENV_PY) and not CHECK and base:
        print(f"creating .venv with {base} ...", flush=True)
        os.makedirs(HOME, exist_ok=True)
        subprocess.run([base, "-m", "venv", VENV], check=True)
    if os.path.exists(VENV_PY) and not CHECK:
        print("installing Python packages (numpy, scipy, pillow, faster-whisper, yt-dlp) ...", flush=True)
        r = subprocess.run([VENV_PY, "-m", "pip", "install", "-q", "--upgrade", "pip"], capture_output=True)
        r = subprocess.run([VENV_PY, "-m", "pip", "install", "-q", "-r", reqs], capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-1500:], flush=True)
    probe = run([VENV_PY, "-c", "import numpy, scipy, PIL, faster_whisper"]) if os.path.exists(VENV_PY) else None
    status("venv", bool(probe and probe.returncode == 0), VENV_PY,
           f"python3 {os.path.join(KIT, 'setup', 'setup.py')}")

    # GSAP (standard license, downloaded here rather than committed)
    if not os.path.exists(GSAP_PATH) and not CHECK:
        os.makedirs(os.path.dirname(GSAP_PATH), exist_ok=True)
        try:
            urllib.request.urlretrieve(GSAP_URL, GSAP_PATH)
        except OSError as e:
            print(f"GSAP download failed: {e}", flush=True)
    good = os.path.exists(GSAP_PATH) and f"GSAP {GSAP_VERSION}" in open(GSAP_PATH, errors="ignore").read(400)
    status("gsap", good, GSAP_VERSION, f"download {GSAP_URL} to {GSAP_PATH}")

    # HyperFrames (renders the video in headless Chrome) and its Chrome
    if shutil.which("npx" if not WIN else "npx.cmd"):
        hv = version_of(HF + ["--version"])
        status("hyperfrm", "0.8.139" in hv, "hyperframes 0.8.139",
               FULL_ACCESS if SANDBOX else "check your internet connection, then run setup again")
        if not CHECK:
            print("making sure the render browser is installed ...", flush=True)
            r = run(HF + ["browser", "ensure"])
            if r.returncode:
                print((r.stdout + r.stderr)[-800:], flush=True)
        chrome = run(HF + ["browser", "path"])
        status("chrome", chrome.returncode == 0 and bool(chrome.stdout.strip()), "found" if chrome.returncode == 0 else "",
               FULL_ACCESS if SANDBOX else f"{' '.join(HF)} browser ensure")
        if chrome.returncode == 0 and os.path.exists(GSAP_PATH):
            render_test()
    else:
        status("hyperfrm", False, "needs Node first", FIX["node"][OS])

    # the transcription model (downloaded once, about 1.5 GB, into the Hugging Face cache)
    if os.path.exists(VENV_PY):
        have = run([VENV_PY, "-c", "from faster_whisper.utils import download_model; download_model('medium', local_files_only=True)"])
        if have.returncode and not CHECK:
            print("downloading the transcription model (Whisper medium, about 1.5 GB, once) ...", flush=True)
            subprocess.run([VENV_PY, "-c", "from faster_whisper.utils import download_model; download_model('medium')"])
            have = run([VENV_PY, "-c", "from faster_whisper.utils import download_model; download_model('medium', local_files_only=True)"])
        status("whisper", have.returncode == 0, "medium", "check your internet connection, then run setup again")

    # optional: smoother cutouts
    if "--matte" in sys.argv and os.path.exists(VENV_PY):
        if not CHECK:
            cmd = [VENV_PY, "-m", "pip", "install", "-q", "torch"]
            if OS == "linux" and not shutil.which("nvidia-smi"):
                cmd += ["--index-url", "https://download.pytorch.org/whl/cpu"]
            print("installing PyTorch (about 1 GB) ...", flush=True)
            subprocess.run(cmd)
        t = run([VENV_PY, "-c", "import torch; print(torch.__version__)"])
        status("matte", t.returncode == 0, t.stdout.strip(), "python3 setup/setup.py --matte")

    # the creator's style (made by onboarding, not by setup)
    pack = os.path.join(HOME, "style", "style.json")
    print(f"STATUS style      {'OK     ' if os.path.exists(pack) else 'NONE YET'} "
          f"{pack if os.path.exists(pack) else 'the first video starts with onboarding (onboarding/ONBOARDING.md)'}",
          flush=True)
    print("READY" if ok else "NOT READY: apply the fixes above, then run setup again", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
