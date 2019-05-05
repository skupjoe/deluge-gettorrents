# deluge-gettorrents

## About

Prints Deluge torrent information for downloading or paused torrents matching specific labels.
<br><br>

## Usage

./getTorrents.py -h
usage: getTorrents.py [-h] [-a] [-d] [-s] [-p] [-o [PATH]] [-u USER]

Makes a local connection to Deluge and lists or writes torrent information.

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Display torrents that are in all states.
  -d, --downloading     Display torrents that are in a Downloading state.
  -s, --seeding         Display torrents that are in a Seeding state.
  -p, --paused          Display torrents that are in a Paused state.
  -o [PATH], --output [PATH]
                        Output path for TSV generation. (default: ./)

Connection:
  -u USER, --user USER  Specify username for connection.
