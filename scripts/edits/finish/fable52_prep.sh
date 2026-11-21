#!/bin/zsh
# Footage -> cut review for one reel. Usage: fable52_prep.sh <main|trial> <video files...>
# trial: pass the trial take file(s) AND the main take file(s); shared beats reuse main takes.
set -euo pipefail
R=$1; shift
REPO=$HOME/Desktop/codebases/content_os; PY=$REPO/.venv/bin/python
REEL=$HOME/Movies/ContentOS/fable52-$R
export PATH="$HOME/.conda-envs/content-os-tools/bin:$PATH"
mkdir -p $REEL/raw
for f in "$@"; do cp -n "$f" $REEL/raw/; done
cd $REPO
$PY -m content_os.pipeline run $REEL --until judge_cuts
$PY -m content_os.visuals render $REEL
echo "cut review: $REEL/work/cut_review.html  |  then: $PY -m content_os.pipeline approve $REEL cut_review"
