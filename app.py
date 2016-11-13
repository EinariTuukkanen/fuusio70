# -*- coding=utf-8 -*-
from flask import Flask
from flask import request
from flask_mail import Mail, Message

from pymongo import MongoClient

from bson import json_util
from bson.objectid import ObjectId
import json

from time import time

from flask_cors import CORS, cross_origin

import ConfigParser
from string import Template

app = Flask(__name__)
CORS(app)

client = MongoClient('localhost', 27017)
db = client.fuusio70

def init_config(config_name):
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    config.read(config_name)
    settings  = dict()
    app.config.update(**dict(config.items('Email')))
    for section in config.sections():
        settings.update({section : dict(config.items(section))})
    if db.config.find_one() is None:
        db.config.save(settings)
    else:
        db.config.update({'_id': db.config.find_one().get('_id')}, settings, upsert=True)
    if not db.config.find_one({'referenceCounter': { '$exists': 1}}):
        db.config.update({'referenceCounter': { '$exists': 1}},{'referenceCounter': db.config.find_one({}, {'Billing': 1, '_id': 0}).get('Billing').get('InitialReference')}, upsert=True)

def reference_counter():
    reference_number = db.config.find_one({'referenceCounter':{'$exists': 1}})
    db.config.update({'_id': reference_number.get('_id')}, {'referenceCounter': int(reference_number.get('referenceCounter')) +1})
    return int(reference_number.get('referenceCounter')) +1
    
def send_mail(user_data): # done for a specific case for Fuusi70
    settings = db.config.find_one()
    email_templates = settings.get('Email_templates')
    billing = settings.get('Billing')
    if user_data['status'] == u'student':
        sum = int(billing.get('StudentPrice'))
    else:
        sum = int(billing.get('DefaultPrice'))
    if user_data['sillis'] == 'true':
        sum += int(billing.get('Sillis'))
    if user_data['historyOrder'] == 'true':
        sum += int(billing.get('HistoryManuscript'))
    if user_data['historyDeliveryMethod'] == 'true':
        sum += int(billing.get('PostDelivery'))
    email_templates.update({'sum' : sum})
    email_templates.update(user_data)
    
    if user_data['status'] == 'inviteGuest' or user_data['status'] == 'supporter':
        letter = Template(email_templates.get('ThankYouLetter')).safe_substitute(email_templates)
    else:
        letter = Template(email_templates.get('Bill')).safe_substitute(email_templates)
    msg = Message(email_templates.get('MailHeader'), sender=(email_templates.get('SenderEmailName'), email_templates.get('SenderEmailAddress')), recipients=[user_data['email']])
    msg.body = letter
    mail.send(msg)

init_config('config.ini')
mail = Mail(app)

@app.route('/users/<user_id>', methods=['GET'])
def user_read(user_id):
    user = db.users.findOne({'_id': ObjectId(user_id)})
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
    user['referenceNumber'] = reference_counter()
    db.users.update({'_id': ObjectId(user_id)}, {'$set': user})
    send_mail(user)
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
		'referenceNumber': '',
        'sillis': '',
        'status': '',
        'table': '',
        'timestamp': timestamp
    }
    users = db.users
    user_id = users.insert_one(dummyUser).inserted_id
    return json.dumps({'userId': str(user_id), 'timestamp': timestamp})