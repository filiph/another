#!/bin/sh
/Applications/Blender/blender.app/Contents/MacOS/blender \
  -b /Users/filiph/dev/blender/test1.blend \
  -P /Users/filiph/dev/blender/phenotyperender.py -- dna=$1 out=$2
