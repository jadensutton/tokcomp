from flask import session

from .object_mapper import CompilationObjectMapper
from .utils import CompilationUtils

MONGO_KEY_NAME = 'MONGO_KEY'
DB_NAME = 'main'
COMPILATION_COLLECTION_NAME = 'compilations'

class CompilationService:
    def __init__(self, mongo_client, uuid, datetime):
        self.cluster = mongo_client(os.environ.get(MONGO_KEY_NAME))
        self.compilation_object_mapper = CompilationObjectMapper()
        self.compilation_utils = CompilationUtils()
        self.uuid = uuid.uuid4()
        self.datetime = datetime

    def create(self, user_id: str, compilation: dict) -> dict:
        if not self.validate_permissions(user_id):
            print('backend.compilations.service.py - create() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        compilation_id = str(self.uuid)
        compilation = self.add_fields_to_compilation(compilation)
        compilation['modified_at'] = self.datetime.now()

        if not self.validate_input(compilation, compilation_id, user_id):
            print('backend.compilations.service.py - create() - Input validation failed.')
            return {'error': 'Invalid input'}, 400

        db = self.cluster[DB_NAME]
        collection = db[COMPILATION_COLLECTION_NAME]

        persistence_compilation = self.compilation_object_mapper.transport_to_persistence(compilation, user_id, compilation_id)
        try:
            collection.insert_one(persistence_compilation)
        except Exception as e:
            print('backend.compilations.service.py - create() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return persistence_compilation, 200

    def get_one(self, user_id: str, compilation_id: str) -> dict:
        if not self.validate_permissions(user_id):
            print('backend.compilations.service.py - update() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        collection = db[COMPILATION_COLLECTION_NAME]

        try:
            persistence_compilation = collection.find_one({'_id': compilation_id, 'created_by': user_id})
        except Exception as e:
            print('backend.compilations.service.py - get_one() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        if not persistence_compilation:
            return {}, 400

        transport_compilation = self.compilation_object_mapper.persistence_to_transport(persistence_compilation)

        return transport_compilation, 200

    def get(self, user_id: str) -> list:
        if not self.validate_permissions(user_id):
            print('backend.compilations.service.py - get() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        collection = db[COMPILATION_COLLECTION_NAME]

        try:
            persistence_compilation = collection.find({'created_by': user_id})
        except Exception as e:
            print('backend.compilations.service.py - get() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        transport_compilations = [self.compilation_object_mapper.persistence_to_transport(persistence_compilation) for persistence_compilation in persistence_compilation]

        return {'data': transport_compilations}, 200

    def update(self, user_id: str, compilation_id: str, compilation: dict) -> dict:
        if not self.validate_permissions(user_id):
            print('backend.compilations.service.py - update() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        compilation['modified_at'] = self.datetime.now()

        if not self.validate_input(compilation, compilation_id, user_id):
            print('backend.compilations.service.py - update() - Input validation failed.')
            return {'error': 'Invalid input'}, 400

        if not self.validate_tiktok_urls(compilation['videos']):
            print('backend.compilations.service.py - update() - Invalid share URL(s)')
            return {'error': 'Invalid input'}, 400

        db = self.cluster[DB_NAME]
        collection = db[COMPILATION_COLLECTION_NAME]

        persistence_compilation = self.compilation_object_mapper.transport_to_persistence(compilation, user_id, compilation_id)
        try:
            collection.replace_one({'_id': compilation_id, 'created_by': user_id}, persistence_compilation)
        except Exception as e:
            print('backend.compilations.service.py - update() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return persistence_compilation, 200

    def delete(self, user_id: str, compilation_id: str) -> str:
        if not self.validate_permissions(user_id):
            print('backend.compilations.service.py - delete() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        collection = db[COMPILATION_COLLECTION_NAME]

        try:
            collection.delete_one({'_id': compilation_id, 'created_by': user_id})
        except Exception as e:
            print('backend.compilations.service.py - delete() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return 'Ok', 200

    def validate_input(self, compilation: dict, compilation_id: str, user_id: str) -> bool:
        if not user_id or not compilation_id:
            print('backend.compilations.service.py - validate_input() - compilation_id or user_id not provided. compilation_id = {compilation_id}, user_id = {user_id}'.format(compilation_id=compilation_id, user_id=user_id))
            return False

        if not self.compilation_utils.get_required_fields() <= set(compilation.keys()):
            print('backend.compilations.service.py - validate_input() - Compilation obj does not contain all required fields. Compilation = \n{}'.format(compilation))
            return False

        for field in self.compilation_utils.get_required_fields():
            if compilation[field] == None:
                print('backend.compilations.service.py - validate_input() - Compilation obj contains None for a required field. Compilation = \n{}'.format(compilation))
                return False

        return True

    def validate_permissions(self, user_id: str) -> bool:
        return session and user_id == session['user']['_id']

    def validate_tiktok_urls(self, video_urls: list):
        for url in video_urls:
            url_sections = url.split('/')
            if len(url_sections) != 6:
                return False

            if url_sections[0] != 'https:' or url_sections[2] != 'www.tiktok.com' or url_sections[3][0] != '@' or url_sections[4] != 'video':
                return False

        return True

    def add_fields_to_compilation(self, compilation: dict) -> dict:
        compilation['videos'] = []
        compilation['created_at'] = self.datetime.now()

        return compilation
