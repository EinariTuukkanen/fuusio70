# -*- coding=utf-8 -*-


# ======================================
# >>> IMPORTS
# ======================================

# Python
import json
import threading

from bson import json_util
from bson.objectid import ObjectId
from time import time

# Third-party
from flask import Flask
from flask import request
from flask_mail import Mail
from flask_cors import CORS, cross_origin

from pymongo import MongoClient

# Project
import utils

# ======================================
# >>> INITIALIZE
# ======================================

client = MongoClient('localhost', 27017)
db = client.fuusio70

app = Flask(__name__)
CORS(app)
settings = utils.load_config(app, db, 'config.ini')
mail = Mail(app)


# ======================================
# >>> REST API ENDPOINTS
# ======================================

from datetime import datetime


@app.route('/users', methods=['GET'])
@cross_origin(origins='*')
def homepage():
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    <img src="http://loremflickr.com/600/400" />
    """.format(time=the_time)


@app.route('/users', methods=['GET'])
@cross_origin(origins='*')
def users_read():
    """ Returns all user objects """
    users = db.users
    return json.dumps(list(users.find()), default=json_util.default)


@app.route('/users/<user_id>', methods=['GET'])
@cross_origin(origins='*')
def user_read(user_id):
    """ Returns single user object by id """
    user = db.users.find_one({'_id': ObjectId(user_id)})
    user = user or {}
    return json.dumps(user, default=json_util.default)


@app.route('/usersCount', methods=['GET'])
@cross_origin(origins='*')
def users_count():
    """ Returns the count of user objects """
    count = db.users.count()
    return json.dumps(count)


@app.route('/users', methods=['PUT'])
@cross_origin(origins='*')
def users_update():
    """ Update user object """
    raw_data = request.data
    try:
        if not raw_data:
            raise ValueError('request.data was empty')
        data = json.loads(raw_data)
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


@app.route('/users', methods=['POST'])
@cross_origin(origins='*')
def users_create():
    """ Creates new empty user object """
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
    timeout_duration = int(settings['App']['SessionTimeout'])
    threading.Timer(
        timeout_duration, session_timeout, (db, str(user_id))
    ).start()

    return json.dumps({'userId': str(user_id), 'timestamp': timestamp})


# ======================================
# >>> HELPER FUNCTIONS
# ======================================

def session_timeout(mongo_db, user_id):
    user = mongo_db.users.find_one({'_id': ObjectId(user_id)})
    if not user.get('name'):
        mongo_db.users.delete_one({'_id': ObjectId(user_id)})


# ======================================
# >>> RUN
# ======================================


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
