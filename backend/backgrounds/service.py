from flask import session

from PIL import Image
from .object_mapper import BackgroundObjectMapper
from .utils import BackgroundUtils

MONGO_KEY_NAME = 'MONGO_KEY'
DB_NAME = 'main'
BACKGROUND_COLLECTION_NAME = 'backgrounds'

class BackgroundService:
    def __init__(self, mongo_client, uuid):
        self.cluster = mongo_client('mongodb+srv://admin:fY9sUYO5nWUdCcOQ@cluster0.cyk1gh1.mongodb.net/?retryWrites=true&w=majority')#os.environ.get(MONGO_KEY_NAME))
        self.background_object_mapper = BackgroundObjectMapper()
        self.background_utils = BackgroundUtils()
        self.uuid = uuid.uuid4()

    def create(self, user_id: str, background: dict) -> dict:
        if not self.validate_permissions(user_id):
            print('backend.backgrounds.service.py - create() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        if not self.validate_input(background, user_id):
            print('backend.backgrounds.service.py - create() - Input validation failed.')
            return {'error': 'Invalid input'}, 400

        background_id = str(self.uuid)

        db = self.cluster[DB_NAME]
        collection = db[BACKGROUND_COLLECTION_NAME]

        persistence_background = self.background_object_mapper.transport_to_persistence(background, user_id, background_id)
        try:
            collection.insert_one(persistence_background)
        except Exception as e:
            print('backend.backgrounds.service.py - create() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return persistence_background, 200

    def get(self, user_id: str) -> list:
        if not self.validate_permissions(user_id):
            print('backend.backgrounds.service.py - get() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        collection = db[BACKGROUND_COLLECTION_NAME]

        try:
            persistence_background = collection.find({'created_by': user_id})
        except Exception as e:
            print('backend.backgrounds.service.py - get() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        transport_backgrounds = [self.background_object_mapper.persistence_to_transport(persistence_background) for persistence_background in persistence_background]

        return {'data': transport_backgrounds}, 200

    def validate_input(self, background: dict, user_id: str) -> bool:
        if not user_id:
            print('backend.backgrounds.service.py - validate_input() - user_id not provided. user_id = {user_id}'.format(user_id=user_id))
            return False

        if not self.background_utils.get_required_fields() <= set(background.keys()):
            print('backend.backgrounds.service.py - validate_input() - Background obj does not contain all required fields. Background = \n{}'.format(background))
            return False

        for field in self.background_utils.get_required_fields():
            if background[field] == None:
                print('backend.backgrounds.service.py - validate_input() - Background obj contains None for a required field. Background = \n{}'.format(background))
                return False

        if session['user']['plan'] == 'free':
            print('backend.backgrounds.service.py - validate_input() - User with free plan attempted to use custom background. Background = {}'.format(background['background']))
            return False

        print(background['file'])
        img = Image.open(background['file'])
        width, height = img.size
        if width != 1920 or height != 1080:
            print('backend.backgrounds.service.py - validate_input() - Image submitted was not 1920 x 1080. Width = {}, Height = {}'.format(width, height))
            return False

        return True

    def validate_permissions(self, user_id: str) -> bool:
        return session and user_id == session['user']['_id']
