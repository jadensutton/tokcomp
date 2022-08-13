import os

from flask import session
from datetime import datetime, timedelta

from .utils import UserUtils

MONGO_KEY_NAME = 'MONGO_KEY'
DB_NAME = 'main'
USERS_COLLECTION_NAME = 'users'

class UserService:
    def __init__(self, mongo_client, uuid4, encryption_algorithm, datetime, email_utils):
        self.cluster = mongo_client(os.environ.get(MONGO_KEY_NAME))
        self.user_utils = UserUtils()
        self.uuid = uuid4
        self.encryption_algorithm = encryption_algorithm
        self.email_utils = email_utils

    def start_session(self, user):
        del user['password']
        del user['confirmation_code']
        del user['change_password_code']
        del user['change_password_request_time']
        session['logged_in'] = True
        session['user'] = user

        return user, 200

    def login(self, email, password):
        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        user = collection.find_one({'email': email})

        if user and self.encryption_algorithm.verify(password, user['password']):
            return self.start_session(user)

        return {'error': 'Invalid login credentials.'}, 401

    def signup(self, email, password):
        if not self.validate_email(email):
            return {'error': 'Email address already in use.'}, 400

        if not self.validate_password(password):
            return {'error': 'Password is invalid. Must have at least 8 characters.'}, 400

        user = {
            '_id': str(self.uuid.uuid4()),
            'email': email,
            'password': password,
            'confirmation_code': str(self.uuid.uuid4()),
            'change_password_code': None,
            'change_password_request_time': None,
            'status': self.user_utils.get_pending_status()
        }

        user['password'] = self.encryption_algorithm.encrypt(user['password'])

        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        if collection.insert_one(user):
            self.email_utils.confirm_user(user['email'], user['_id'], user['confirmation_code'])
            return self.start_session(user)

        return {'error': 'Signup failed.'}, 400

    def logout(self):
        session.clear()
        return 'Ok', 200

    def confirm(self, user_id, confirmation_code):
        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        user = collection.find_one({'_id': user_id})

        if user and user['confirmation_code'] == confirmation_code:
            if collection.update_one({'_id': user_id}, {'$set': {'status': self.user_utils.get_complete_status()}}):
                return 'Ok', 200

        return {'error': 'Error confirming email.'}, 400

    def forgot(self, user_id):
        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        user = collection.find_one({'_id': user_id})
        if user:
            change_password_code = str(self.uuid.uuid4())
            if collection.update_one({'_id': user_id}, {'$set': {'change_password_code': self.encryption_algorithm.encrypt(change_password_code), 'change_password_request_time': datetime.now()}}):
                self.email_utils.forgot_password(user['email'], user['_id'], change_password_code)
                return 'Ok', 200

        return {'error': 'Error generating password reset code.'}, 400

    def change_password(self, user_id, change_password_code, new_password):
        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        if not self.validate_permissions(user_id):
            user = collection.find_one({'_id': user_id})

            if not user or not self.encryption_algorithm.verify(change_password_code, user['change_password_code']) or datetime.now() > user['change_password_request_time'] + timedelta(hours=1):
                return {'error': 'Unauthorized'}, 401

        if not self.validate_password(new_password):
            return {'error': 'Password is invalid. Must have at least 8 characters.'}, 400

        if collection.update_one({'_id': user_id}, {'$set': {'password': self.encryption_algorithm.encrypt(new_password)}}):
            return 'Ok', 200

        return {'error': 'Change password failed.'}, 400

    def validate_email(self, email):
        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        if collection.find_one({'email': email}):
            return False

        return True

    def validate_password(self, password):
        return len(password) >= 8

    def validate_permissions(self, user_id: str) -> bool:
        return session and user_id == session['user']['_id']
