#!/usr/bin/env python3.4
from rq import use_connection, get_current_job
from flask_socketio import SocketIO
from bson import ObjectId
import eventlet
import pymongo
import inspect
import time
import os

eventlet.monkey_patch()
use_connection()

MONGOCLIENT = pymongo.MongoClient()
DB = MONGOCLIENT.smoothie.attacks
SOCKETIO = SocketIO(message_queue='redis://localhost:6379/')


class SmoothiePlugin:
    """
        Base plugin.
        This leaves us with basic mongo manipulation, handles
        run time and sleeps 10 second between each
        callback call
    """
    def __init__(self):
        self.job = get_current_job()
        self.timeout = 60 * 10
        self.start_date = time.time()
        while 'mongo_id' not in self.job.meta:
            self.job = get_current_job()
        self.mongo_id = ObjectId(self.job.meta['mongo_id'])
        file_ = inspect.getfile(self.__class__)
        self.name = os.path.basename(file_).split('.')[0]
        self.result = "Ok"
        self._do_run = True
        self.run()

    @property
    def do_run(self):
        """
            This property checks if we've stopped
            the job via API
        """
        if time.time() > self.start_date + self.timeout:
            return False
        if self.name not in self.mongo_document['plugins']:
            return True  # Not yet started
        if self._do_run is False:
            return self._do_run
        return self.mongo_document['plugins'][self.name]

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

    def set(self, data):
        """
            Forces a $set on the database and puts the data via ws.
        """
        self.update({'$set': data})
        SOCKETIO.emit('data', data, namespace="/smoothie")

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

    def stop(self):
        """
            Stops gracefuly
        """
        self._do_run = False

    def __repr__(self):
        return "{}: {}".format(self.name, self.result)
