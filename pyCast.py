"""
Play a slideshow on the chromecast

This program allows the user to cast images to their chromecast.
The images are of a particular type ie: ".JPEG" or ".jpg" or ".png",
and contained in a single folder. These parameters are provided,
among others, at command line invocation - or through tuning of
the default parameters below.

Arguments
__________

--show-debug : (none)
    Show debugging information. False if not provided.

--do-random : (none)
    Select image order at random. Ls order if not provided.

--media-flag : '*.jpeg'
    Indicate via a command line regex file type to show

--media-tag : 'image/jpeg'
    Indicate http object type

--cast : 'MyKitchenChromecast'
    Provide friendly name of chromecast

--directory : '/home/barack/SecretPix'
    Provide absolute path to directory for slideshow

--pause : 69
    Number of seconds to hold each image in slideshow

Returns
_______

does not return. Ctrl-C to exit, or launch with "&" and kill process

Examples
______
python pyCast.py --show-debug --media-flag '*.JPEG' --media-tag 'image/jpeg'
--cast 'MyChromecast' --directory '/home/dorthy/OzGirlSummerPics' --do-random


"""
# pylint: disable=invalid-name

import argparse
import logging
import sys
import time
import pychromecast
import pprint
import glob
import os
import urllib.parse
import socket
import http.server
import socketserver
import threading
import random

# Authorship information
__author__ = "Shaun Bowman"
__copyright__ = "Copywrong 2022, Mazeltough Project"
__credits__ = ["SoManyCopyPastes... sorry i dont know the names", "Mom"]
__license__ = "MIT"
__version__ = "0.420.69"
__maintainer__ = "Shaun Bowman"
__email__ = "dm@me.com"
__status__ = "AlphaAF"

# Change to the friendly name of your Chromecast
CAST_NAME = 'ShaunsOfficeMonitor'

# Set webserver port
PORT = 8000

# Set time for photo
PAUSE = 120

# Set media type
MEDIA_FLAG = "*.JPEG"
MEDIA_TAG = "image/jpeg"

# Change to an audio or video url
MEDIA_URL ="http://192.168.0.222:8000/Screenshot%20from%202021-01-24%2023-11-40.png"
MEDIA_DIR = "./"
parser = argparse.ArgumentParser(
    description="Play a slideshow on Chromecast using all images of a given "+
    "type in a given directory."
)
parser.add_argument("--show-debug", help="Enable debug log", action="store_true")
parser.add_argument("--do-random", help="Pick media in dir at random, default false",
                    action="store_true")
parser.add_argument(
    "--media-flag", help="Media flag like *.JPEG or *.png", default=MEDIA_FLAG
)
parser.add_argument(
    "--media-tag", help="Media tag like 'image/jpeg' or 'image/png'",
    default=MEDIA_TAG
)
parser.add_argument(
    "--pause", help="Number of seconds per photograph during slideshow",
    default=PAUSE
)
parser.add_argument(
    "--cast", help='Name of cast device (default: "%(default)s")', default=CAST_NAME
)
parser.add_argument(
    "--url", help='Media url (default: "%(default)s")', default=MEDIA_URL
)
parser.add_argument(
    "--directory", help='Directory containing media to cast', default=MEDIA_DIR
)
args = parser.parse_args()

if args.show_debug:
    logging.basicConfig(level=logging.DEBUG)

# Start webserver for current directory
def startServer(args, PORT=8000):
    os.chdir(args.directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("Server started at localhost:" + str(PORT))
        httpd.serve_forever()

# Start new thread for webserver
daemon = threading.Thread(name='daemon_server',
                          target=startServer,
                          args=(args, PORT))
daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
daemon.start()

# Wait for stuff... maybe useless
time.sleep(2)

# Get list of files of specific type, in specific directory
pprint.pprint(glob.glob(args.directory+"/"+MEDIA_FLAG))
filesAndPath = glob.glob(args.directory+"/"+MEDIA_FLAG)
nFiles = len(filesAndPath)
if (nFiles==0):
    pprint.pprint("Error: No files found")
    sys.exit(1)

# Select starting point for slideshow
random.seed()
nRandom = random.random()*nFiles
nStartFile = round(nRandom)

# Build uri of first image for slideshow. This is sent to the chromecast. This
# ends up being a mash up of the host ip address, the webserver port, and the
# file name of the image to be displayed.
fileName = os.path.basename(filesAndPath[nStartFile])
fileUrl = urllib.parse.quote(fileName)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ipAddr = s.getsockname()[0]
fileUri = 'http://'+ipAddr+':'+'8000/'+fileUrl
MEDIA_URL = fileUri

# -- Setup chromecast --
# List chromecasts on the network, but don't connect
services, browser = pychromecast.discovery.discover_chromecasts()
# Shut down discovery
pychromecast.discovery.stop_discovery(browser)
chromecasts, browser = pychromecast.get_listed_chromecasts(
    friendly_names=[args.cast]
)
if not chromecasts:
    print(f'No chromecast with name "{args.cast}" discovered')
    sys.exit(1)

cast = chromecasts[0]
# Start socket client's worker thread and wait for initial status update
cast.wait()
print(f'Found chromecast with name "{args.cast}", attempting to play "{args.url}"')
cast.media_controller.play_media(fileUri, MEDIA_TAG)

# Wait for player_state PLAYING
player_state = None
has_played = False
# -- end Setup chromecast --

# Enter the infinite loop where successive images are displayed via the
# chromecast, by sending it image uri's served by our scripts webserver,
# linking the chromecast to images in our directory.
iPhoto = nStartFile 
iPhotoMax = nFiles-1 
while True:
    try:
        if player_state != cast.media_controller.status.player_state:
            player_state = cast.media_controller.status.player_state
            print("Player state:", player_state)
        if player_state == "PLAYING":
            has_played = True
        if cast.socket_client.is_connected and has_played and player_state != "PLAYING":
            has_played = False
            cast.media_controller.play_media(args.url, "audio/mp3")

        time.sleep(int(args.pause))
        if args.do_random:
            nRandom = random.random()*nFiles
            iPhoto = round(nRandom)
        else:
            iPhoto = iPhoto + 1
            if iPhoto > iPhotoMax:
                iPhoto = 0
        fileName = os.path.basename(filesAndPath[iPhoto])
        fileUrl = urllib.parse.quote(fileName)
        fileUri = 'http://'+ipAddr+':'+'8000/'+fileUrl
        cast.media_controller.play_media(fileUri, MEDIA_TAG)

    except KeyboardInterrupt:
        break

# Shut down discovery
browser.stop_discovery()
