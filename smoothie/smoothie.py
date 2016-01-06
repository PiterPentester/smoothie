#!/usr/bin/env python

"""

    Main server.

    This one launches processes and interacts with them in specific
    ways to store them in a mongodb database.

    It requires python-rq as it queues each task, with a simple API.

    Each task is defined as a server module in server/modules, so rq should
    be able to import smoothie.server.modules.<your_task> as you add
    your_task using this.

    All post data should be available inside the task using
    get_current_job().meta

    I'll need another component that notifies changes in mongodb
    via websocket / marks content as changed / sends notifies via ws.

"""

from flask import Flask, request, render_template
from bson.json_util import dumps
from bson import ObjectId
from redis import Redis
from rq import Queue
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

        That will be executed and added to the mongo
        database with the returned id.

        Mongodb ID will be accesible to the plugin in
        meta['mongo_id'] (wich SHOULD be the ID of
        a current working attack)
    """
    job = RQ_QUEUE.enqueue_call(func="smoothie.plugins.{}".format(plugin),
                                timeout=60 * 60 * 60)
    job.meta = dict(request.form)
    job.meta['mongo_id'] = mongo_id
    job.save()
    DB.update({'_id': ObjectId(mongo_id)},
              {'$set': {'run_{}'.format(str(job.id)): True}})
    return str(job.id)


@APP.route('/data/<mongo_id>', methods=["GET"])
def data_get(mongo_id):
    """
    .. http::post:: /data/(str:mongo_id)

        Get a mongo document.
    """

    return dumps(DB.find_one({'_id': ObjectId(mongo_id)}))


@APP.route('/data/<mongo_id>', methods=["POST"])
def data_post(mongo_id):
    """
    .. http::post:: /data/(str:mongo_id)

        Modify a mongo document.
    """
    return dumps(DB.update({'_id': ObjectId(mongo_id)},
                           {'$set': request.form}))


@APP.route('/stop_plugin/<mongo_id>/<job_id>', methods=["POST"])
def stop_plugin(mongo_id, job_id):
    """
        .. http:put:: /create/(str:plugin)

            Stop a specific redis job.
    """
    return dumps(DB.update({'_id': ObjectId(mongo_id)},
                           {'$set': {'run_{}'.format(job_id): False}}))


@APP.route('/create/<attack_type>', methods=["POST"])
def create_attack(attack_type):
    """
        Kind of a dummy function.
        This right now only creates a new entry in attack
        mongo database and returns the id.
        The mongodb document structures is as follows::

            Attack{
                _id : ObjectId()
                type: <attack_type>,
                targets: [
                    {
                        _id: <int>,
                        ip: <ip>,
                        bssid: <mac>
                        essid: <essid>,
                        credentials: [],
                        extra_data: [],
                        raw_packets: []
                    }
                ]
            }
    """
    return str(DB.insert_one({
        'type': attack_type,
        'targets': []
    }).inserted_id)


def main():
    """
        Main
    """

    APP.run(host='0.0.0.0', port=8080, debug=True)
