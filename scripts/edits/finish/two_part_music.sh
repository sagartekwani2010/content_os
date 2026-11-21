#!/bin/bash
# Two-part music: track A until <switch_s>, 2 s crossfade into track B, to <total_s>.
# Usage: two_part_music.sh <trackA> <trackB> <switch_s> <total_s> <out.wav>
set -euo pipefail
FF=${FFMPEG:-$HOME/.conda-envs/content-os-tools/bin/ffmpeg}
A=$1; B=$2; SW=$3; TOT=$4; OUT=$5
LA=$(python3 -c "print($SW+1)"); LB=$(python3 -c "print(max(1,$TOT-$SW+1))")
"$FF" -v error -y -i "$A" -stream_loop -1 -i "$B" -filter_complex \
 "[0:a]atrim=0:$LA,asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[a];[1:a]atrim=0:$LB,asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo[b];[a][b]acrossfade=d=2:c1=tri:c2=tri[o]" \
 -map "[o]" -t "$TOT" "$OUT"
echo "$OUT"
