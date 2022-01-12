# pyCast Slideshow! :neckbeard::godmode::basecamp::100:

## Purpose
pyCast is a python chromecast repository. It casts images from a directory to the chromecast.
 :warning: Note, NOT secure! :warning: Use behind a firewall - creates a low security webserver on client machine to serve images to chromecast.

## Play a slideshow on the chromecast
This program allows the user to cast images to their chromecast.
The images are of a particular type ie: ".JPEG" or ".jpg" or ".png",
and contained in a single folder. These parameters are provided,
among others, at command line invocation - or through tuning of
the default parameters in code.

## Arguments
`--show-debug`
    Show debugging information. False if not provided.

`--do-random`
    Select image order at random. Directory order,`me@nix:~/Pictures$ ls'
    if not provided.

`--media-flag '*.jpeg'`
    Indicate via a command line regex file type to show

`--media-tag 'image/jpeg'`
    Indicate http object type

`--cast 'MyKitchenChromecast'`
    Provide friendly name of chromecast

`--directory '/home/barack/SecretPix'`
    Provide absolute path to directory for slideshow

`--pause 69`
    Number of seconds to hold each image in slideshow

## Returns
does not return. Ctrl-C to exit, or launch with "&" and kill process

## Examples
```console
yourName@yourComputer:~$ python pyCast.py --show-debug --media-flag '*.JPEG' --media-tag 'image/jpeg'
--cast 'YourChromecast' --directory '/home/yourName/Pictures' --do-random
```

