# Another Death of Art

## Install

1) Install pre-requisites (see below).
2) Check out code from here (git).
3) Copy `gimp/apply-painting.scm` file to the Gimp plugins directory. (It ought to be `~/.gimp-2.x/scripts` on Unix and `~/Library/Application Support/GIMP/2.x/plug-ins` on Mac.)
4) Put `gimp/gimpressionist_preset` to gimpressionist Preset directory.
5) Create a `config.sh` configuration file and fill in your machine's path details. (You can start with `config_sample.sh`.)


## Run

To run, execute this on the command line:

    python3 interface.py

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

# Credits

http://www.flickr.com/photos/argenberg/86967955/sizes/o/
http://www.flickr.com/photos/md9/2479076483/sizes/o/
http://www.flickr.com/photos/8684894@N06/5798544288/sizes/l/
http://www.flickr.com/photos/brenda-starr/3941615637/sizes/o/
http://www.flickr.com/photos/nilsenpics/7977312553/sizes/l/
