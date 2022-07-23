import os

from flask import session
from gridfs import GridFS

MONGO_KEY_NAME = 'MONGO_KEY'
DB_NAME = 'gridfs'

class FileService:
    def __init__(self, mongo_client):
        self.cluster = mongo_client(os.environ.get(MONGO_KEY_NAME))

    def create(self, file, export_id: str) -> dict:
        db = self.cluster[DB_NAME]
        fs = GridFS(db)

        try:
            file_id = fs.put(file, _id=export_id)

        except Exception as e:
            print('backend.files.service.py - create() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return file_id

    def get_one(self, user_id: str, export_id: str) -> str:
        if not self.validate_permissions(user_id):
            print('backend.files.service.py - get() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        fs = GridFS(db)

        try:
            file = fs.get(export_id).read()
        except Exception as e:
            print('backend.files.service.py - get_one() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return file, 200

    def validate_permissions(self, user_id: str) -> bool:
        return user_id == session['user']['_id']
