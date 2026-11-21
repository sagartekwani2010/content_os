#!/bin/zsh
# Footage -> cut review for one reel. Usage: reel_prep.sh <reel-slug> <main|trial> <video files...>
# trial: pass the trial take file(s) AND the main take file(s); shared beats reuse main takes.
set -euo pipefail
SLUG=$1; R=$2; shift 2
REPO=$HOME/Desktop/codebases/content_os; PY=$REPO/.venv/bin/python
REEL=$HOME/Movies/ContentOS/$SLUG-$R
export PATH="$HOME/.conda-envs/content-os-tools/bin:$PATH"
mkdir -p $REEL/raw
for f in "$@"; do cp -n "$f" $REEL/raw/; done
cd $REPO
$PY -m content_os.pipeline run $REEL --until judge_cuts
$PY -m content_os.visuals render $REEL
echo "cut review: $REEL/work/cut_review.html  |  then: $PY -m content_os.pipeline approve $REEL cut_review"
