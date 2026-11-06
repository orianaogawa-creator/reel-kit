#!/bin/bash
# stills.sh "f1,f2,..." -> proj/stills/NNNN.jpg (a-roll frame + overlay)
cd "${PROJ:-.}"; mkdir -p proj/stills proj/ovst
node tools/cap.js proj/ovst "$1"
for f in ${1//,/ }; do n=$(printf %04d $f)
  ffmpeg -nostdin -loglevel error -y -i proj/aroll.mp4 -i proj/ovst/$n.png -filter_complex "[0:v]select=eq(n\,$f)[a];[a][1:v]overlay=format=auto" -frames:v 1 -q:v 3 proj/stills/$n.jpg
done
