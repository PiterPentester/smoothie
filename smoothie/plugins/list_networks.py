#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    List networks
"""

from smoothie.plugins.base import SmoothiePlugin
import subprocess
import tempfile
import logging
import psutil
import time
import csv
import os
import re


def get_target(line):
    """
        Returns a formatted target (client or ap)
        Ignoring invalid lines.
    """
    if not line:
        return False

    stripped = line[0].strip()
    if stripped.startswith("BSSID") or stripped.startswith("Station"):
        return False

    if len(line) == 7:
        return {
            'type': 'client',
            'ssid': line[0].strip(),
            'power': line[3].strip(),
            'bssid': line[5].strip(),
            'probes': [a.strip() for a in line[-1].split() if a]
        }
    elif len(line) == 15:
        return {
            'type': 'access_point',
            'bssid': line[0].strip(),
            'channel': line[3].strip(),
            'privacy': line[5].strip(),
            'cipher': line[6].strip(),
            'auth': line[7].strip(),
            'power': line[8].strip(),
            'essid': line[13].strip(),
            'key': line[14].strip()
        }
    else:
        return False


class ListNetworks(SmoothiePlugin):
    """
        List networks.
        This plugin:
            - Puts the selected network interface in monitor mode
            - Retrieves the monitor interface
            - Starts an analysis with airodump-ng in channel hoping
              mode
            - Teardown clears interface and kills airodump
    """
    def get_moniface(self):
        """
            Get monitor interface.
            If it's already done, don't re-run
        """

        if 'monitor' not in self.mongo_document:
            wifi = self.mongo_document['wifi']
            env = os.environ.copy()
            env['MON_PREFIX'] = 'smoothie'
            ret = subprocess.check_output(
                ['airmon-ng', 'start', wifi],
                env=env)
            for asg in re.finditer(r'(.*) on (.*)\)', ret):
                return asg.group(2)
        else:
            return self.mongo_document['monitor']

    def start_airodump(self):
        """
            Checks if airodump-ng should be started.
        """
        if 'airodump_pid' in self.mongo_document:
            return not psutil.pid_exists(self.mongo_document['airodump_pid'])
        else:
            return True

    def callback(self):
        """
            - Put the selected network on monitor mode
            - Scan for networks
            - Add networks and clients into target array.
        """
        while 'wifi' not in self.mongo_document:
            # Wait for the user to choose a wifi network.
            time.sleep(10)

        # Get monitor interface
        moniface = self.get_moniface()

        self.update({'$set': {'monitor': moniface}})
        self.tmp = False

        # Now we list the clients
        if self.start_airodump():
            self.tmp = tempfile.NamedTemporaryFile(delete=False)

            proc = subprocess.Popen(['airodump-ng', moniface, '-w',
                                     self.tmp.name,
                                     '--output-format', 'csv'],
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE)

            self.update({'$set': {'airodump_pid': proc.pid,
                                  'tmpfile': self.tmp.name}})
        try:
            name = False
            if not self.tmp:
                name = self.mongo_document['tmpfile']
            else:
                name = self.tmp.name

            if not os.path.exists("{}-01.csv".format(name)):
                return

            with open("{}-01.csv".format(name), 'rb') as csvfile:
                reader = csv.reader(csvfile)

                clients = []
                aps = []

                for target in reader:
                    target_ = get_target(target)
                    if target_:
                        type_ = target_.pop('type')
                        if type_ == "client":
                            clients.append(target_)
                        else:
                            aps.append(target_)

                # Esto no es un diccionario es una lista!!!
                cl_b = self.mongo_document['clients']
                aps_b = self.mongo_document['aps']
                r_clients = cl_b + [x for x in clients if x not in cl_b]
                r_aps = aps_b + [x for x in aps if x not in aps_b]

                self.update({'$set': {'clients': r_clients, 'aps': r_aps}})

        except Exception as err:
            logging.exception(err)
            time.sleep(1)

    def teardown(self):
        """
            Cleanses airodump-ng process and brings monitor interface down
        """
        psutil.Process(self.mongo_document['airodump_pid']).kill()
        subprocess.check_call(['airmon-ng', 'stop',
                               self.mongo_document['monitor']])
        return True
