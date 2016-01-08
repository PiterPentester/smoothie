#!/usr/bin/env python

"""

    Main server.

    This one launches processes and interacts with them in specific
    ways to store them in a mongodb database.

    It requires python-rq as it queues each task, with a simple API.

    Each task is defined as a server module in server/modules, so rq should
    be able to import smoothie.server.modules.<your_task> as you add
    your_task using this.

"""

from flask import Flask, request, render_template
from bson.json_util import dumps
from bson import ObjectId
from redis import Redis
from rq import Queue
import json
import pymongo
import logging

APP = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(name=__name__)
MONGOCLIENT = pymongo.MongoClient()
DB = MONGOCLIENT.smoothie.attacks
RQ_QUEUE = Queue(connection=Redis(), name="plugins")


@APP.route('/', methods=["GET"])
def index():
    return render_template("index.html")


@APP.route('/start_plugin/<plugin>/<mongo_id>', methods=["POST"])
def create(plugin, mongo_id):
    """
        .. http:post:: /create/(str:plugin)

        Create a plugin task for a specific attack.
        This will add to the redis queue a job for
        a specific smoothie plugin.
        Mongodb ID will be accesible to the plugin in
        meta['mongo_id'] (wich SHOULD be the ID of
        a current working attack)
    """
    DB.update({'_id': ObjectId(mongo_id)}, {'$set': dict(request.form)})
    job = RQ_QUEUE.enqueue_call(func="smoothie.plugins.{}".format(plugin),
                                timeout=60 * 60 * 60)
    job.meta['mongo_id'] = mongo_id
    job.save()
    return str(job.id)


@APP.route('/data/<mongo_id>', methods=["GET"])
def data_get(mongo_id):
    """
    .. http::post:: /data/(str:mongo_id)

        Returns a mongo document.
    """
    return dumps(DB.find_one({'_id': ObjectId(mongo_id)}))


@APP.route('/data/<mongo_id>', methods=["POST"])
@APP.route('/data', methods=["POST"])
def data_post(mongo_id=False):
    """
    .. http::post:: /data/(str:mongo_id)

        Modify a mongo document.

        If no id is requested, it'll create a new one
        and return the id.
    """
    if not mongo_id:
        return str(DB.insert_one(json.loads(request.form['data'])).inserted_id)

    return dumps(DB.update({'_id': ObjectId(mongo_id)},
                           {'$set': request.form}))


def main():
    """
        Main
    """

    APP.run(host='0.0.0.0', port=8080, debug=True)
