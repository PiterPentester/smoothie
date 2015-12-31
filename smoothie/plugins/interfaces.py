#!/usr/bin/env python

from rq import use_connection, get_current_job
from bson import ObjectId
from wireless import Wireless
import pymongo
import time

MONGOCLIENT = pymongo.MongoClient()
DB = MONGOCLIENT.smoothie.attacks

use_connection()


def main():
    """
        Adds networks as a type of client.
    """

    job = get_current_job()

    while job.meta['run']:
        job = get_current_job()
        mongo_id = ObjectId(job.meta['mongo_id'])
        mongo_document = DB.find_one({'_id': mongo_id})

        if 'wifi_list' not in mongo_document:
            # Wait for wifi list to populate.

            ifaces = [a for a in Wireless().interfaces()
                      if not a.startswith('smoothie')]

            DB.update({'_id': mongo_id}, {'wifi_list': ifaces})
            time.sleep(30)
