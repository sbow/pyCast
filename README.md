# pyCast Slideshow!
#### Shaun Bowman
#### Jan 11 2021
## Purpose
pyCast is a python chromecast repository. It casts images from a directory to the chromecast.
 Note, NOT secure! Use behind a firewall - creates a low security webserver on client machine to serve images to chromecast.
## Launch command:
python pyCast.py --show-debug --directory '/home/shaun/Pictures/iCloud' --media-flag '*.JPEG' --media-tag 'image/jpeg'

## Other commands:
#### List available commands
python pyCast.py --help
#### Select images at random
--do-random
#### Specify directory
--directory '/path/toMy/photos'
#### Show debug info at command line
--show-debug
#### Specify friendly name of Chromecast
--cast 'OfficeChromecast'
