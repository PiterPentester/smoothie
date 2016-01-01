#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    List networks
"""

from rq import use_connection, get_current_job
from bson import ObjectId
import subprocess
import tempfile
import pymongo
import psutil
import time
import csv
import os
import re

MONGOCLIENT = pymongo.MongoClient()
DB = MONGOCLIENT.smoothie.attacks

use_connection()


def monitor_mode(wifi):
    """
        Gets a wireless interface and creates
        a smoothieN monitor interface using airmon-ng.
    """

    env = os.environ.copy()
    env['AIRMON_PREFIX'] = 'smoothie'
    ret = subprocess.check_output(
        ['airmon-ng', 'start', wifi],
        env=env)

    for asg in re.finditer(r'(.*) on (.*)\)', ret):
        return asg.group(2)


def get_moniface(mongo_document):
    """
        Get monitor interface.
        If it's already done, don't re-run
    """
    if 'monitor' not in mongo_document:
        return monitor_mode(mongo_document['wifi'])
    else:
        return mongo_document['monitor']


def get_mongo_document(mongo_id):
    """ reload mongo document """
    return DB.find_one({'_id': mongo_id})


def start_airodump(mongo_document):
    """
        Checks if airodump-ng should be started.
    """
    if 'airodump_pid' in mongo_document:
        return not psutil.pid_exists(mongo_document['airodump_pid'])
    else:
        return True


def get_target(line):
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


def main():
    """
        Adds networks as a type of client.
    """
    job = get_current_job()

    while job.meta['run']:
        job = get_current_job()
        mongo_id = ObjectId(job.meta['mongo_id'])
        mongo_document = DB.find_one({'_id': mongo_id})

        while 'wifi' not in mongo_document:
            # Wait for the user to choose a wifi network.
            time.sleep(1)
            mongo_document = get_mongo_document(mongo_id)

        # Get monitor interface
        moniface = get_moniface(mongo_document)

        DB.update({'_id': mongo_id}, {'$set': {'monitor': moniface}})
        mongo_document = get_mongo_document(mongo_id)

        # Now we list the clients
        if start_airodump(mongo_document):
            tmp = tempfile.NamedTemporaryFile(delete=False)
            try:
                os.remove("{}-01.csv".format(tmp))
            except:
                pass

            proc = subprocess.Popen(['airodump-ng', moniface, '-w', tmp.name,
                                     '--output-format', 'csv'],
                                    stdout=subprocess.PIPE, shell=True)

            DB.update({'_id': mongo_id}, {'$set': {
                'airodump_pid': proc.pid}})
        try:
            with open("{}-01.csv".format(tmp), 'rb') as csvfile:
                reader = csv.reader(csvfile)
                targets = []
                for target in reader:
                    targets.append(get_target(target))

                # Esto no es un diccionario es una lista!!!
                targets_b = mongo_document['targets']
                res = targets_b + [x for x in targets if x not in targets_b]

                DB.update({'_id': mongo_id},
                          {'$set': {'targets': res}})
        except:
            pass
