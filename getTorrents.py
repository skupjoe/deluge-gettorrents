#!/usr/bin/env python

# '''
# getTorrents.py
#
# Prints Deluge torrent information for downloading or paused torrents
# matching specific labels (in this case, "music" & "pth", only).
#
# Optionally, allows output to TSV. (CSV files don't work well with torrent
# names that have commas.)
#
# '''

from deluge.ui.client import client
from twisted.internet import reactor
from datetime import datetime
from operator import itemgetter
import argparse
import json
import csv
import sys
import os

host = None
port = None
user = None
passw = None

reload(sys)
sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser(
        description='Makes a local connection to Deluge and lists \
            or writes torrent information.',
        formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='Display torrents that are in all states.'
)
parser.add_argument(
        '-d', '--downloading',
        action='store_true',
        help='Display torrents that are in a Downloading state.'
)
parser.add_argument(
        '-s', '--seeding',
        action='store_true',
        help='Display torrents that are in a Seeding state.'
)
parser.add_argument(
        '-p', '--paused',
        action='store_true',
        help='Display torrents that are in a Paused state.'
)
parser.add_argument(
        '-o', '--output',
        nargs='?',
        const=os.getcwd(),
        metavar='PATH',
        help='Output path for TSV generation. (default: ./)'
)
conngroup = parser.add_argument_group("Connection")
conngroup.add_argument(
        '-u', '--user',
        help='Specify username for connection.'
)


args = parser.parse_args()
tsv_path = args.output
today = datetime.today()


if not (args.downloading or args.paused or args.seeding or args.all):
    parser.error("Insufficient arguments provided. Use -a, -d, -s, or -p")

if args.all and (args.downloading or args.paused or args.seeding):
    parser.error("Invalid argument selection. Only use -a.")


def on_connect_fail(result):
    print "Connection failed!"
    print "result:", result


def on_connect_success(connection_id):

    report = []

    def get_torrents(torrents):
        torr_str = json.dumps(torrents, indent=4, sort_keys=True)
        torr_obj = json.loads(torr_str)
        s_torr_obj = sorted(torr_obj.values(), key=itemgetter('time_added'))
        for index, entry in enumerate(s_torr_obj):
            hashval = entry['hash']
            name = entry['name']
            label = entry['label']
            state = entry['state']
            size = entry['total_size']
            added = datetime.fromtimestamp(entry['time_added'])
            age = (today - added).days
            report.append([added, age, label, state, hashval, size, name])
        return report

    def print_torrents(report):
        for index, entry in enumerate(report, 1):
            print '%d :: %s :: %s :: %s :: %s :: %s :: %d :: %s' % \
                (index, entry[0], entry[1], entry[2],
                    entry[3], entry[4], entry[5], entry[6])

    def generate_tsv(report):
        filename = 'torrent_report_{}.txt'.format(
            datetime.strftime(today, '%Y%m%d%H%M'))
        with open(tsv_path + '/' + filename, 'wb') as tsvfile:
            csvwriter = csv.writer(
                tsvfile, quotechar='"', delimiter='\t', skipinitialspace=True,
                dialect='excel-tab', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow(
                ['Added', 'Days Old', 'Label', 'State', 'Hash', 'Size', 'Name']
                )
            for row in report:
                csvwriter.writerow(row)

    def disconnect(connection_id):
        client.disconnect()
        reactor.stop()

    try:
        if args.all is True:
            torrents = client.core.get_torrents_status(
                {'label': ('music', 'pth')},
                ['name', 'total_size', 'label', 'state', 'hash', 'time_added'],
                diff=False)
            torrents.addCallback(get_torrents)
        if args.seeding is True:
            torrents = client.core.get_torrents_status(
                {'state': 'Seeding', 'label': ('music', 'pth')},
                ['name', 'total_size', 'label', 'state', 'hash', 'time_added'],
                diff=False)
            torrents.addCallback(get_torrents)
        if args.downloading is True:
            torrents = client.core.get_torrents_status(
                {'state': "Downloading", 'label': ('music', 'pth')},
                ['name', 'total_size', 'label', 'state', 'hash', 'time_added'],
                diff=False)
            torrents.addCallback(get_torrents)
        if args.paused is True:
            torrents = client.core.get_torrents_status(
                {'state': "Paused", 'label': ('music', 'pth')},
                ['name', 'total_size', 'label', 'state', 'hash', 'time_added'],
                diff=False)
            torrents.addCallback(get_torrents)
        if tsv_path:
            torrents.addCallback(generate_tsv)
        else:
            torrents.addCallback(print_torrents)
        torrents.addCallback(disconnect)
    except Exception as e:
        print('Caught this error: ' + repr(e))
        reactor.stop()


if __name__ == '__main__':
    # make deferred object from deluge connection
    d = client.connect("localhost", 58846, "<username>", "<password>")
    d.addCallback(on_connect_success)
    d.addErrback(on_connect_fail)
    reactor.run()
