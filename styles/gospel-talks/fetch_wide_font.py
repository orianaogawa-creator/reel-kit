"""Download Archivo Expanded Black (Archivo at width 125, weight 900) from Google Fonts as a TTF, the headline face of
the Gospel Talks formula. The kit's style.py fetches only the pack's three roles at normal width, so this one face
is fetched here. Archivo is under the SIL Open Font License 1.1 (fonts.google.com/specimen/Archivo).
Run: python3 fetch_wide_font.py <folder> [<folder> ...]   -> <folder>/ArchivoExpanded-900.ttf in each"""
import os
import re
import shutil
import sys
import urllib.request

CSS = "https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@125,900"
UA = "Wget/1.21"          # Google serves plain TTF files to this agent

if len(sys.argv) < 2:
    sys.exit(__doc__)
css = urllib.request.urlopen(urllib.request.Request(CSS, headers={"User-Agent": UA}), timeout=30).read().decode()
url = re.search(r"url\((https://[^)]+\.ttf)\)", css).group(1)
first = None
for folder in sys.argv[1:]:
    os.makedirs(folder, exist_ok=True)
    out = os.path.join(folder, "ArchivoExpanded-900.ttf")
    if first:
        shutil.copy(first, out)
    else:
        urllib.request.urlretrieve(url, out)
        first = out
    print("wrote", out)
