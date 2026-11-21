#!/bin/zsh
# make_bed.sh <voice_only.mp4> <music.mp3> <out.m4a> <total_s> <drop_from> <drop_to>
# Music bed: loudness -18 LUFS, ducked ~6 dB under speech (ratio 3), silent through the twist, 1.5 s fade-out.
export PATH="$HOME/.local/bin:$PATH"
V=$1; M=$2; O=$3; T=$4; A=$5; B=$6
ENV="if(lt(t,$A-0.15),1,if(lt(t,$A),($A-t)/0.15,if(lt(t,$B),0,if(lt(t,$B+0.05),(t-$B)/0.05,1))))"
ffmpeg -v error -y -i $V -stream_loop -1 -i $M -filter_complex "\
[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:$T,asetpts=PTS-STARTPTS,loudnorm=I=${BED_LUFS:--18}:TP=-2:LRA=11,aresample=48000,volume='$ENV':eval=frame,afade=t=out:st=$(echo "$T-1.6"|bc):d=1.5[m];\
[0:a]aresample=48000,aformat=channel_layouts=stereo[v];[m][v]sidechaincompress=threshold=0.08:ratio=3:attack=20:release=400[out]" \
-map "[out]" -c:a aac -b:a 256k $O
