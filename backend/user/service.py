import os
from flask import session

MONGO_KEY_NAME = 'MONGO_KEY'
DB_NAME = 'main'
USERS_COLLECTION_NAME = 'users'

class UserService:
    def __init__(self, mongo_client, uuid4, encryption_algorithm):
        self.cluster = mongo_client(os.environ.get(MONGO_KEY_NAME))
        self.uuid = uuid4()
        self.encryption_algorithm = encryption_algorithm

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user

        return user, 200

    def login(self, email, password):
        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        user = collection.find_one({'email': email})

        if user and self.encryption_algorithm.verify(password, user['password']):
            return self.start_session(user)

        return {'error': 'Invalid login credentials'}, 401

    def signup(self, email, password):
        if not self.validate_email(email):
            return {'error': 'Email address already in use'}, 400

        if not self.validate_password(password):
            return {'error': 'Password is invalid. Must have at least 8 characters.'}, 400

        user = {
            '_id': str(self.uuid),
            'email': email,
            'password': password
        }

        user['password'] = self.encryption_algorithm.encrypt(user['password'])

        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        if collection.insert_one(user):
            return self.start_session(user)

        return {'error': 'Signup failed.'}, 400

    def logout(self):
        session.clear()
        return 'Ok', 200

    def validate_email(self, email):
        db = self.cluster[DB_NAME]
        collection = db[USERS_COLLECTION_NAME]

        if collection.find_one({'email': email}):
            return False

        return True

    def validate_password(self, password):
        return len(password) >= 8
