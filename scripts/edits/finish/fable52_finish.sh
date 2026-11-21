#!/bin/zsh
# Finish one Fable 5.2 reel after the creator approved the cuts.
# Usage: fable52_finish.sh <main|trial>
# Steps: pipeline render + qa -> music bed (main: drone -> techno at beat 8) -> SFX anchors -> Edits build
# (30 fps, splitAt sections, transitions) -> bed + SFX -> Edits export -> audio-only limiter -> FINAL in deliver/.
set -euo pipefail
R=$1
REPO=$HOME/Desktop/codebases/content_os
PY=$REPO/.venv/bin/python
FIN=$REPO/scripts/edits/finish
MUS=$REPO/music
REEL=$HOME/Movies/ContentOS/fable52-$R
DEL=$HOME/Movies/ContentOS/fable52-deliver
export PATH="$HOME/.conda-envs/content-os-tools/bin:$PATH"
export METAPILOT_TOKEN="$(launchctl getenv METAPILOT_TOKEN)"
cd $REPO

echo "== render + qa ($R)"
$PY -m content_os.pipeline render $REEL
$PY -m content_os.pipeline qa $REEL || echo "QA reported issues: read $REEL/work/qa.md"
CLEAN=$REEL/work/render/final/final_clean.mp4
CUTS=$REEL/work/cuts.json
TOTAL=$(python3 -c "import json;print(json.load(open('$CUTS'))['duration'])")
mkdir -p $DEL/$R
# Edits caches media by path: every rebuild imports under a NEW timestamped name.
TAG=$(date +%H%M%S)
CL=$DEL/$R/clean_$TAG.mp4; BED=$DEL/$R/bed_$TAG.m4a
cp $CLEAN $CL

echo "== music bed"
# Creator's call (19 Nov): one catchy track from second 0; a drone intro read as "not music".
SRC=${MUSIC:-$MUS/music_techno_fest_vibes.mp3}
NODROP_A=$(python3 -c "print($TOTAL+5)"); NODROP_B=$(python3 -c "print($TOTAL+6)")
BED_LUFS=-16 $FIN/make_bed.sh $CL $SRC $BED $TOTAL $NODROP_A $NODROP_B

echo "== SFX anchors"
python3 $FIN/sfx_anchors.py $CUTS $REEL/edits_plan.json $DEL/$R/plan_resolved.json

echo "== Edits build"
python3 $FIN/edits_build_split.py $CL $DEL/$R/plan_resolved.json $CUTS
python3 $FIN/edits_finish.py $DEL/$R/plan_resolved.json $CUTS $BED 0

echo "== Edits export"
OUT=$DEL/$R/edits_export.mp4
python3 -c "
import sys, time; sys.path.insert(0, '$FIN')
from ed import call
print(call('export', {'path': '$OUT'}))
for _ in range(240):
    s = call('exportStatus', {}); print(s); time.sleep(5)
    if isinstance(s, dict) and str(s.get('state', s.get('status', ''))).lower() in ('complete', 'done', 'completed', 'finished') and __import__('os').path.exists('$OUT'): break
"

echo "== audio-only limiter"
ffmpeg -v error -y -i $OUT -map 0:v -map 0:a -c:v copy -af "aresample=192000,alimiter=limit=0.79:attack=1:release=80:level=0,aresample=48000" -c:a aac -b:a 256k $DEL/fable52_${R}_FINAL.mp4
ffmpeg -hide_banner -nostats -i $DEL/fable52_${R}_FINAL.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
ffprobe -v error -show_entries format=duration -of csv=p=0 $DEL/fable52_${R}_FINAL.mp4
echo "== verify sync + music (must pass before handover)"
$REPO/.venv/bin/python $FIN/verify_final.py $DEL/fable52_${R}_FINAL.mp4 $CLEAN
echo "DONE: $DEL/fable52_${R}_FINAL.mp4"
