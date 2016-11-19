from flask import Flask
from flask import request

from pymongo import MongoClient

from bson import json_util
from bson.objectid import ObjectId
import json

from time import time
import threading

from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

client = MongoClient('localhost', 27017)
db = client.fuusio70


@app.route('/users/<user_id>', methods=['GET'])
def user_read(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    return json.dumps(user, default=json_util.default)


@app.route('/users', methods=['GET'])
def users_read():
    users = db.users
    return json.dumps(list(users.find()), default=json_util.default)


@app.route('/usersCount', methods=['GET'])
def users_count():
    count = db.users.count()
    return json.dumps(count)


@app.route('/users', methods=['PUT'])
@cross_origin(origins='*')
def users_update():
    raw_data = request.data
    print('DEBUG: data: ' + str(raw_data))
    if not raw_data:
        print('DEBUG: data was empty')
        return 'Data was empty'
    data = json.loads(raw_data)
    user = data['formData']
    user_id = data['userId']
    db.users.update({'_id': ObjectId(user_id)}, {'$set': user})
    return json.dumps({'userId': str(user_id)})


@app.route('/users', methods=['POST'])
@cross_origin(origins='*')
def users_create():
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
        'sillis': '',
        'status': '',
        'table': '',
        'timestamp': timestamp
    }
    user_id = users.insert_one(dummy_user).inserted_id

    threading.Timer(60 * 31, session_timeout, (str(user_id),))

    return json.dumps({'userId': str(user_id), 'timestamp': timestamp})


def session_timeout(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if not user['name']:
        db.users.delete_one({'_id': ObjectId(user_id)})

app.run()
