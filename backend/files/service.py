import os

from flask import session
from gridfs import GridFS

MONGO_KEY_NAME = 'MONGO_KEY'
DB_NAME = 'gridfs'

class FileService:
    def __init__(self, mongo_client):
        self.cluster = mongo_client('mongodb+srv://admin:fY9sUYO5nWUdCcOQ@cluster0.cyk1gh1.mongodb.net/?retryWrites=true&w=majority')#os.environ.get(MONGO_KEY_NAME))

    def create(self, file, file_id: str) -> dict:
        db = self.cluster[DB_NAME]
        fs = GridFS(db)

        try:
            fs.put(file, _id=file_id)

        except Exception as e:
            print('backend.files.service.py - create() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return 'Ok', 200

    def get_one(self, user_id: str, file_id: str) -> str:
        if not self.validate_permissions(user_id):
            print('backend.files.service.py - get() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        fs = GridFS(db)

        try:
            file = fs.get(file_id).read()
        except Exception as e:
            print('backend.files.service.py - get_one() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return file, 200

    def validate_permissions(self, user_id: str) -> bool:
        return session and user_id == session['user']['_id']
