# -*- coding=utf-8 -*-


# ======================================
# >>> IMPORTS
# ======================================

# Python
import json
import threading

# import json_util
from bson import ObjectId
from time import time

# Third-party
from flask import Flask
from flask import request
from flask import Blueprint
from flask_mail import Mail
from flask_cors import CORS, cross_origin

from pymongo import MongoClient

# Project
from server import utils

# ======================================
# >>> INITIALIZE
# ======================================

app = Flask(__name__)
CORS(app)

routes = Blueprint('ilmo', __name__, url_prefix='/api')

# ======================================
# >>> REST API ENDPOINTS
# ======================================


@routes.route('/users', methods=['GET'])
@cross_origin(origins='*')
def users_read():
    """ Returns all user objects """
    db = get_database()
    users = db.users
    return JSONEncoder().encode(list(users.find()))
    # , default=json_util.default


@routes.route('/users/<user_id>', methods=['GET'])
@cross_origin(origins='*')
def user_read(user_id):
    """ Returns single user object by id """
    db = get_database()
    user = db.users.find_one({'_id': ObjectId(user_id)})
    user = user or {}
    return JSONEncoder().encode(user)


@routes.route('/usersCount', methods=['GET'])
@cross_origin(origins='*')
def users_count():
    """ Returns the count of user objects """
    db = get_database()
    count = db.users.count()
    return JSONEncoder().encode(count)


@routes.route('/users', methods=['PUT'])
@cross_origin(origins='*')
def users_update():
    """ Update user object """
    db = get_database()
    raw_data = request.data
    print(str(raw_data.decode("utf-8")))
    try:
        if not raw_data:
            raise ValueError('request.data was empty')
        data = json.loads(str(raw_data.decode("utf-8")))
    except ValueError as e:
        print('[ERROR] /users PUT ValueError: ' + str(e))
        return str(e)

    user = data['formData']
    user['referenceNumber'] = utils.get_reference_number(db)
    user_id = data['userId']
    db.users.update({'_id': ObjectId(user_id)}, {'$set': user}, upsert=True)

    settings = db.config.find_one()
    utils.send_billing_mail(mail, settings, user)

    return json.dumps({'userId': str(user_id)})


@routes.route('/users', methods=['POST'])
@cross_origin(origins='*')
def users_create():
    """ Creates new empty user object """
    db = get_database()
    timestamp = int(time())
    users = db.users
    dummy_user = {
        'additionalInfo': '',
        'allergies': '',
        'avec': '',
        'email': '',
        'firstYear': '',
        'historyAddress': '',
        'historyDeliveryMethod': '',
        'historyOrder': '',
        'name': '',
        'referenceNumber': '',
        'sillis': '',
        'status': '',
        'table': '',
        'timestamp': timestamp
    }
    user_id = users.insert_one(dummy_user).inserted_id

    # Timeout, delete if not edited within timeout limit
    settings = db.config.find_one()
    timeout_duration = int(settings['App']['SessionTimeout'])
    threading.Timer(
        timeout_duration, session_timeout, (db, str(user_id))
    ).start()

    return json.dumps({'userId': str(user_id), 'timestamp': timestamp})


# ======================================
# >>> HELPERS
# ======================================

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def session_timeout(mongo_db, user_id):
    user = mongo_db.users.find_one({'_id': ObjectId(user_id)})
    if not user.get('name'):
        mongo_db.users.delete_one({'_id': ObjectId(user_id)})


def get_database():
    client = MongoClient('localhost', 27017)
    return client.fuusio70

# ======================================
# >>> RUN
# ======================================

settings = utils.load_config(app, get_database(), '/home/fuusio70-ilmo/server/config.ini')
mail = Mail(app)

app.register_blueprint(routes)
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0')
