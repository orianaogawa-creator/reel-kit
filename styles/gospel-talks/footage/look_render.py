"""The footage look for this video, applied after the cutout: the airy grade (work/look.cube, from work/look.py)
on every frame, and the room behind the speaker softly blurred while she stays sharp (her alpha from
the kit's cutout, assets/subject.webm). Writes, frame for frame with the cut:
  public/clean.mp4     graded, background blurred, subject sharp (the composition's footage)
  public/subject.webm  the graded speaker with her alpha (the cutout windows put her over the type behind her head)
The originals stay in assets/ (aroll.mp4, subject.webm). Kit files untouched.
Run: PY -I work/look_render.py <project> [sigma]"""
import multiprocessing as mp
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import look  # noqa: E402

W, H = 1080, 1920
TAGS = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
SIGMA = 7.0


def frames(path):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                               "stream=nb_read_frames", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip())


def work(item):
    a, m = item
    return look.composite_u8(np.frombuffer(a, np.uint8).reshape(H, W, 3), np.frombuffer(m, np.uint8).reshape(H, W), SIGMA).tobytes()


def main():
    global SIGMA
    project = os.path.abspath(sys.argv[1])
    SIGMA = float(sys.argv[2]) if len(sys.argv) > 2 else SIGMA
    cube = os.path.join(HERE, "look.cube")
    aroll, subject = os.path.join(project, "assets", "aroll.mp4"), os.path.join(project, "assets", "subject.webm")
    out_c, out_s = os.path.join(project, "public", "clean.mp4"), os.path.join(project, "public", "subject.webm")
    tmp_c, tmp_s = out_c + ".tmp.mp4", out_s + ".tmp.webm"
    n = frames(aroll)
    if frames(subject) != n:
        sys.exit("the cutout and the cut differ in frame count: re-run the cutout")
    # the workers fork first, so none of them holds a copy of the pipes below (an encoder would never see EOF)
    pool = mp.get_context("fork").Pool(3)
    # graded picture (BT.709 in and out, so the round trip keeps the colours), and her alpha from the VP9 side track
    dec_a = subprocess.Popen(["ffmpeg", "-v", "error", "-i", aroll, "-vf",
                              f"scale=in_color_matrix=bt709:in_range=tv,format=rgb24,lut3d=file={cube}:interp=tetrahedral",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    dec_m = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", subject, "-vf", "alphaextract",
                              "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    enc_c = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30",
                              "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                              "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-g", "10", "-keyint_min", "10",
                              *TAGS, "-movflags", "+faststart", tmp_c], stdin=subprocess.PIPE)
    enc_s = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30",
                              "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuva420p",
                              "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "18", "-b:v", "0", "-deadline", "good",
                              "-cpu-used", "4", "-row-mt", "1", "-auto-alt-ref", "0", *TAGS, tmp_s], stdin=subprocess.PIPE)

    def source():                             # every frame read once; the graded speaker goes straight to her encoder
        for _ in range(n):
            a, m = dec_a.stdout.read(W * H * 3), dec_m.stdout.read(W * H)
            enc_s.stdin.write(np.dstack([np.frombuffer(a, np.uint8).reshape(H, W, 3),
                                         np.frombuffer(m, np.uint8).reshape(H, W)]).tobytes())
            yield a, m

    for k, out in enumerate(pool.imap(work, source(), chunksize=4)):
        enc_c.stdin.write(out)
        if k % 300 == 0:
            print(f"look: frame {k}/{n}", flush=True)
    pool.close()
    pool.join()
    for p in (enc_c, enc_s):
        p.stdin.close()
        p.wait()
    for p in (dec_a, dec_m):
        p.wait()
    if frames(tmp_c) != n or frames(tmp_s) != n:
        sys.exit(f"FRAME MISMATCH after the look: {frames(tmp_c)} / {frames(tmp_s)} vs {n}")
    os.replace(tmp_c, out_c)
    os.replace(tmp_s, out_s)
    print(f"look: wrote {out_c} and {out_s} ({n} frames, background blur sigma {SIGMA})")


if __name__ == "__main__":
    main()
