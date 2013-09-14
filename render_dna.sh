#!/bin/sh
DIR=$( cd "$( dirname "$0" )" && pwd )
. $DIR/config.sh
$BLENDER_PATH \
  -b $DIR/test1.blend \
  -P $DIR/render_dna.py -- dna=$1 out=$2
