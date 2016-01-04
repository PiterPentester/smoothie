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

        def get_target(line):
            """
                Returns a formatted target (client or ap)
                Ignoring invalid lines.
            """
            stripped = line[0].strip()
            if stripped.startswith("BSSID") or stripped.startswith("Station"):
                return False

            if len(line) == 7:
                return {
                    'type': 'client',
                    'ssid': line[0],
                    'power': line[3],
                    'bssid': line[5],
                    'probes': line[-1].split(',')
                }
            elif len(line) == 15:
                return {
                    'type': 'access_point',
                    'bssid': line[0],
                    'channel': line[3],
                    'privacy': line[5],
                    'cipher': line[6],
                    'auth': line[7],
                    'power': line[8],
                    'essid': line[13],
                    'key': line[14]
                }
            else:
                return False

        while 'wifi' not in self.mongo_document:
            # Wait for the user to choose a wifi network.
            time.sleep(10)

        # Get monitor interface
        moniface = self.get_moniface()

        self.update({'$set': {'monitor': moniface}})

        # Now we list the clients
        if self.start_airodump():
            self.tmp = tempfile.NamedTemporaryFile(delete=False)

            proc = subprocess.Popen(['airodump-ng', moniface, '-w',
                                     self.tmp.name,
                                     '--output-format', 'csv'],
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE)

            self.update({'$set': {'airodump_pid': proc.pid}})
        try:
            with open("{}-01.csv".format(self.tmp.name), 'rb') as csvfile:
                reader = csv.reader(csvfile)
                targets = []
                for target in reader:
                    if target:
                        targets.append(get_target(target))
                # Esto no es un diccionario es una lista!!!
                targets_b = self.mongo_document['targets']
                res = targets_b + [x for x in targets if x not in targets_b]
                self.update({'$set': {'targets': res}})
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
