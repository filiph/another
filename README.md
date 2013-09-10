# Another Death of Art

## Install

1) Install pre-requisites (see below).
1) Check out code from here (git).
2) Copy `gimp/apply-painting.scm` file to the Gimp plugins directory. (It ought to be `~/.gimp-2.x/scripts` on Unix and `~/Library/Application Support/GIMP/2.x/plug-ins` on Mac.)
2) Put `gimp/gimpressionist_preset` to gimpressionist Preset directory.


## Run

To run, execute this on the command line:

    python3 runner.py

This will make the first generation of phenotypes and start the voting
process, showing each phenotype. Use `y` and `n` to vote, `space` to
skip voting on that particular phenotype. Close by hitting `escape`.

Rendering of the artwork runs on the background. (It runs the
`dnarender.sh` script and provides it with the DNA in binary string
fromat and the output filename as 2 command line arguments.)

### Prerequisites

* Python 3
* PyGame
* Blender
* Gimp