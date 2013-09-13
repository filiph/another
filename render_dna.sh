#!/bin/sh
. ./config.sh
$BLENDER_PATH \
  -b /home/filiph/dev/another/test1.blend \
  -P /home/filiph/dev/another/render_dna.py -- dna=$1 out=$2
