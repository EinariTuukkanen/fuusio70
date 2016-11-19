from flask_mail import Mail, Message

import ConfigParser

from pymongo import MongoClient
from string import Template

client = MongoClient('localhost', 27017)
db = client.fuusio70

class Config:
    
    def __init__(flask_app, mongo_db):
        self.config = ConfigParser.SafeConfigParser()
        self.db = mongo_db

    
    def init_config(config_name):
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
        if db.config.find_one({'referenceCounter': { '$exists': 1}}):
            db.config.update({'referenceCounter': { '$exists': 1}},{'referenceCounter': db.config.find_one({}, {'InitialReference': 1, '_id': 0}).get('InitialReference')}, upsert=True)
    
    def reference_counter ()
        reference_number = db.config.find_one({'referenceCounter':{'$exists': 1}})
        db.config.update({'_id': reference_number.get('_id')}, {'referenceCounter': int(reference_number.get('referenceCounter')) +1})
        return int(reference_number.get('referenceCounter')) +1
    
class Mail_sender:
    def __init__(flask_app, mongo_db):
        self.mail = Mail(flask_app)
        self.db = mongo_db
    
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
        letter = Template(email_templates.get('ThankYouLetter')).safe_substitute(settings)
    else:
        letter = Template(email_templates.get('Bill')).safe_substitute(settings)
    msg = Message(email_templates.get('MailHeader'), sender=(email_templates.get('SenderEmailName'), email_templates.get('SenderEmailAddress')), recipients=[user_data['email']])
    msg.body = letter
    mail.send(msg)