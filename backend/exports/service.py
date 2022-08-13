import os
import requests
import shutil

from flask import session
from threading import Thread
from moviepy.editor import VideoFileClip, concatenate_videoclips
from natsort import natsorted

from .object_mapper import ExportObjectMapper
from .utils import ExportUtils

MONGO_KEY_NAME = 'MONGO_KEY'
DB_NAME = 'main'
EXPORT_COLLECTION_NAME = 'exports'
COMPILATION_COLLECTION_NAME = 'compilations'

class ExportService:
    def __init__(self, mongo_client, uuid4, datetime, browser, beautiful_soup, file_service):
        self.cluster = mongo_client(os.environ.get(MONGO_KEY_NAME))#os.environ.get(MONGO_KEY_NAME))
        self.export_object_mapper = ExportObjectMapper()
        self.export_utils = ExportUtils()
        self.uuid = uuid4()
        self.datetime = datetime
        self.browser = browser
        self.beautiful_soup = beautiful_soup
        self.file_service = file_service()

    def create(self, user_id: str, compilation_id: str, export: dict) -> dict:
        if not self.validate_permissions(user_id):
            print('backend.exports.service.py - create() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        if not self.validate_compilation_id(compilation_id):
            print('backend.exports.service.py - create() - Input validation failed.')
            return {'error': 'Invalid input'}, 400

        export_id = str(self.uuid)

        export['compilation_id'] = compilation_id
        export['created_at'] = self.datetime.now()
        export['status'] = self.export_utils.get_pending_status()
        export['status_message'] = self.export_utils.get_pending_status_message()

        db = self.cluster[DB_NAME]
        collection = db[EXPORT_COLLECTION_NAME]

        persistence_export = self.export_object_mapper.transport_to_persistence(export, user_id, export_id)
        try:
            collection.insert_one(persistence_export)
        except Exception as e:
            print('backend.exports.service.py - create() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        Thread(target=self.build, args=(persistence_export,)).start()

        return persistence_export, 200

    def get(self, user_id: str) -> list:
        if not self.validate_permissions(user_id):
            print('backend.exports.service.py - get() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        collection = db[EXPORT_COLLECTION_NAME]

        try:
            persistence_export = collection.find({'created_by': user_id})
        except Exception as e:
            print('backend.exports.service.py - get() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        transport_exports = [self.export_object_mapper.persistence_to_transport(persistence_export) for persistence_export in persistence_export]

        return {'data': transport_exports}, 200

    def delete(self, user_id: str, export_id: str):
        if not self.validate_permissions(user_id):
            print('backend.exports.service.py - delete() - Permission validation failed.')
            return {'error': 'Unauthorized'}, 401

        db = self.cluster[DB_NAME]
        collection = db[EXPORT_COLLECTION_NAME]

        try:
            collection.delete_one({'_id': export_id, 'created_by': user_id})
        except Exception as e:
            print('backend.exports.service.py - delete() - {}'.format(e))
            raise RuntimeError('Internal server error.')

        return 'Ok', 200

    def validate_input(self, export: dict, export_id: str, user_id: str):
        if not user_id or not export_id:
            print('backend.exports.service.py - validate_input() - export_id or user_id not provided. export_id = {export_id}, user_id = {user_id}'.format(export_id=export_id, user_id=user_id))
            return False

        if not self.export_utils.get_required_fields() <= set(export.keys()):
            print('backend.exports.service.py - validate_input() - Export obj does not contain all required fields. Export = \n{}'.format(export))
            return False

        for field in self.export_utils.get_required_fields():
            if export[field] == None:
                print('backend.exports.service.py - validate_input() - Export obj contains None for a required field. Export = \n{}'.format(export))
                return False

        return True

    def validate_permissions(self, user_id: str) -> bool:
        return session and user_id == session['user']['_id']

    def validate_compilation_id(self, compilation_id: str) -> bool:
        db = self.cluster[DB_NAME]
        collection = db[COMPILATION_COLLECTION_NAME]

        if collection.find_one({'_id': compilation_id}):
            return True

        return False

    def build(self, export: dict):
        temp_path = './backend/exports/temp/{}'.format(export['_id'])
        os.makedirs(temp_path)

        try:
            db = self.cluster[DB_NAME]
            exports_collection = db[EXPORT_COLLECTION_NAME]
            compilations_collection = db[COMPILATION_COLLECTION_NAME]

            compilation = compilations_collection.find_one({'_id': export['compilation_id']})

            for i, share_url in enumerate(compilation['videos']):
                self.browser.get(share_url)
                soup = self.beautiful_soup(self.browser.page_source, 'html.parser')

                url = soup.find('video').get('src')
                with open('{}/{}.mp4'.format(temp_path, i), 'wb') as f_out:
                    r = requests.get(url, stream=True)
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f_out.write(chunk)

        except Exception as e:
            print('backend.exports.service.py - build() - {}'.format(e))
            exports_collection.update_one({'_id': export['_id']}, {'$set': {'status': self.export_utils.get_failed_status(), 'status_message': self.export_utils.get_failed_status_message()}})
            raise RuntimeError('Error while downloading compilation videos.')

        source_videos = []
        try:
            for root, dirs, files in os.walk(temp_path):
                files = natsorted(files)
                for file in files:
                    if os.path.splitext(file)[1] == '.mp4':
                        file_path = os.path.join(root, file)
                        video = VideoFileClip(file_path)
                        source_videos.append(video)

            compilation_video = concatenate_videoclips(source_videos, method='compose')
            compilation_path = '{}/{}'.format(temp_path, 'compilation.mp4')
            compilation_video.to_videofile(compilation_path, fps=60, remove_temp=False)

        except Exception as e:
            print('backend.exports.service.py - build() - {}'.format(e))
            exports_collection.update_one({'_id': export['_id']}, {'$set': {'status': self.export_utils.get_failed_status(), 'status_message': self.export_utils.get_failed_status_message()}})
            raise RuntimeError('Error while combining compilation videos.')

        try:
            self.file_service.create(open(compilation_path, 'rb'), export['_id'])

        except Exception as e:
            print('backend.exports.service.py - build() - {}'.format(e))
            exports_collection.update_one({'_id': export['_id']}, {'$set': {'status': self.export_utils.get_failed_status(), 'status_message': self.export_utils.get_failed_status_message()}})
            raise RuntimeError('Error while uploading final compilation video.')

        exports_collection.update_one({'_id': export['_id']}, {'$set': {'status': self.export_utils.get_complete_status(), 'status_message': self.export_utils.get_complete_status_message()}})
        shutil.rmtree(temp_path, ignore_errors=True)
