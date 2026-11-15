#!/bin/bash
# Master an Edits export to a 1080x1920 H.264 reel at about -14 LUFS, optionally mixing a music bed.
# usage: master.sh <edits_export.mp4> <out.mp4> [music_file] [music_gain_db, default -20]
set -euo pipefail
IN="$1"; OUT="$2"; MUSIC="${3:-}"; MG="${4:--20}"
J=$(ffmpeg -hide_banner -i "$IN" -vn -af "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
LN="loudnorm=I=-14:TP=-1.5:LRA=7:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=false"
V=(-vf "scale=1080:1920:flags=lanczos" -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -profile:v high -color_primaries bt709 -color_trc bt709 -colorspace bt709)
A=(-c:a aac -b:a 192k -ar 48000 -movflags +faststart)
if [ -z "$MUSIC" ]; then
  ffmpeg -v error -y -i "$IN" "${V[@]}" -af "$LN" "${A[@]}" "$OUT"
else
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
  FO=$(python3 -c "print(max(0,$D-2))")
  # voice is mastered first, music is ducked under it with a sidechain, then the two are summed and limited
  ffmpeg -v error -y -i "$IN" -stream_loop -1 -i "$MUSIC" -filter_complex \
   "[0:a]$LN,asplit=2[v1][v2];[1:a]atrim=0:$D,volume=${MG}dB,afade=t=in:d=0.5,afade=t=out:st=$FO:d=2[m];[m][v2]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md];[v1][md]amix=inputs=2:normalize=0,alimiter=limit=0.84[a]" \
   -map 0:v -map "[a]" "${V[@]}" "${A[@]}" "$OUT"
fi
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
