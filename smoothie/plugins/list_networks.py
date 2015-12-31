#!/usr/bin/env python

from rq import use_connection, get_current_job
from bson import ObjectId
import subprocess
import pymongo
import time
import os
import re

MONGOCLIENT = pymongo.MongoClient()
DB = MONGOCLIENT.smoothie.attacks

use_connection()


def main():
    """
        Adds networks as a type of client.
    """
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

        for asg in re.finditer('(.*) on (.*)\)', ret):
            return asg.group(2)

    def get_moniface():
        """
            Get monitor interface.
            If it's already done, don't re-run
        """
        if 'monitor' not in mongo_document:
            return monitor_mode(mongo_document['wifi'])
        else:
            return mongo_document['monitor']

    def get_mongo_document():
        """ reload mongo document """
        return DB.find_one({'_id': mongo_id})

    job = get_current_job()

    while job.meta['run']:
        job = get_current_job()
        mongo_id = ObjectId(job.meta['mongo_id'])
        mongo_document = DB.find_one({'_id': mongo_id})

        while 'wifi' not in mongo_document:
            # Wait for the user to choose a wifi network.
            time.sleep(1)
            mongo_document = get_mongo_document()

        # Get monitor interface
        moniface = get_moniface()

        # Now we list the clients

        DB.update({'_id': mongo_id}, {'monitor': moniface})
        mongo_document = get_mongo_document()
