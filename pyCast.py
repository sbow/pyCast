"""
Example on how to use the Media Controller to play an URL.

"""
# pylint: disable=invalid-name

import argparse
import logging
import sys
import time
import zeroconf
import pychromecast

# imports for handling directory to cast
import pprint
import glob
import os
import urllib.parse
import socket
import http.server
import socketserver
import threading

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
    description="Example on how to use the Media Controller to play an URL."
)
parser.add_argument("--show-debug", help="Enable debug log", action="store_true")
parser.add_argument(
    "--show-zeroconf-debug", help="Enable zeroconf debug log", action="store_true"
)
parser.add_argument(
    "--cast", help='Name of cast device (default: "%(default)s")', default=CAST_NAME
)
parser.add_argument(
    "--known-host",
    help="Add known host (IP), can be used multiple times",
    action="append",
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
if args.show_zeroconf_debug:
    print("Zeroconf version: " + zeroconf.__version__)
    logging.getLogger("zeroconf").setLevel(logging.DEBUG)

# Start webserver for current directory
def startServer(args, PORT=8000):
    os.chdir(args.directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("Server started at localhost:" + str(PORT))
        httpd.serve_forever()

daemon = threading.Thread(name='daemon_server',
                          target=startServer,
                          args=(args, PORT))
daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
daemon.start()
time.sleep(2)
pprint.pprint(glob.glob(args.directory+"/"+MEDIA_FLAG))
filesAndPath = glob.glob(args.directory+"/"+MEDIA_FLAG)

fileName = os.path.basename(filesAndPath[10])
fileUrl = urllib.parse.quote(fileName)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
pprint.pprint(s.getsockname()[0])
ipAddr = s.getsockname()[0]
fileUri = 'http://'+ipAddr+':'+'8000/'+fileUrl
pprint.pprint('\n File uri:\n')
pprint.pprint(fileUri)

# List chromecasts on the network, but don't connect
services, browser = pychromecast.discovery.discover_chromecasts()
# Shut down discovery
pychromecast.discovery.stop_discovery(browser)
chromecasts, browser = pychromecast.get_listed_chromecasts(
    friendly_names=[args.cast], known_hosts=args.known_host
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
iPhoto = 0
iPhotoMax = 50
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

        time.sleep(PAUSE)
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
