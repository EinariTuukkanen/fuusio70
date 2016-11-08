from flask import Flask
from flask import request

from pymongo import MongoClient

from bson import json_util
from bson.objectid import ObjectId
import json

from time import time

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
    dummyUser = {
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
    users = db.users
    user_id = users.insert_one(dummyUser).inserted_id
    return json.dumps({'userId': str(user_id), 'timestamp': timestamp})
