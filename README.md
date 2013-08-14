# Another Death of Art

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
