#!/usr/bin/env python

from rq import use_connection, get_current_job
from bson import ObjectId
import pymongo
import time

MONGOCLIENT = pymongo.MongoClient()
DB = MONGOCLIENT.smoothie.attacks

use_connection()


class SmoothiePlugin(object):
    """
        Base plugin.
        This leaves us with basic mongo manipulation, handles
        run time and sleeps 10 second between each
        callback call
    """
    def __init__(self):
        self.mongo_id = False
        while not self.mongo_id:
            self.job = get_current_job()
            self.mongo_id = ObjectId(self.job.meta['mongo_id'])
        self.run()

    @property
    def do_run(self):
        """
            This property checks if we've stopped
            the job via API
        """
        key = 'run_{}'.format(self.job.id)
        if key not in self.mongo_document:
            return True  # Not yet started
        return self.mongo_document[key]

    @property
    def mongo_document(self):
        """
            Finds our document
        """
        return DB.find_one({'_id': self.mongo_id})

    def update(self, query):
        """
            Updates given query on our mongo document
        """
        return DB.update({'_id': self.mongo_id}, query)

    @property
    def run(self):
        """
            Main loop
        """
        while self.do_run:
            self.callback()
            time.sleep(10)
        self.teardown()

    def callback(self):
        """
            Implement this in your plugins.
        """
        pass

    def teardown(self):
        """
            Tasks to execute after the plugin has been asked to stop
        """
        pass
