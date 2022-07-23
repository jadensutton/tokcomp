import json
import uuid
import os

from flask import Flask, request, session
from flask_cors import CORS, cross_origin
from functools import wraps
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from backend import CompilationService
from backend import ExportService
from backend import FileService
from backend import UserService

app = Flask(__name__, static_folder='client/build', static_url_path='')
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'

def auth_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return {'error': 'Unauthorized.'}, 401

    return wrap

@app.route('/compilations/<user_id>', methods=['POST'])
@auth_required
def create_compilation(user_id):
    compilation = json.loads(request.data)
    compilation_service = CompilationService(MongoClient, uuid.uuid4, datetime)
    return compilation_service.create(user_id, compilation)

@app.route('/compilations/<user_id>', methods=['GET'])
@auth_required
def get_compilations(user_id):
    compilation_service = CompilationService(MongoClient, uuid.uuid4, datetime)
    return compilation_service.get(user_id)

@app.route('/compilations/<user_id>/<compilation_id>', methods=['GET'])
@auth_required
def get_compilation(user_id, compilation_id):
    compilation_service = CompilationService(MongoClient, uuid.uuid4, datetime)
    return compilation_service.get_one(user_id, compilation_id)

@app.route('/compilations/<user_id>/<compilation_id>', methods=['PUT'])
@auth_required
def update_compilation(user_id, compilation_id):
    compilation = json.loads(request.data)
    compilation_service = CompilationService(MongoClient, uuid.uuid4, datetime)
    return compilation_service.update(user_id, compilation_id, compilation)

@app.route('/compilations/<user_id>/<compilation_id>', methods=['DELETE'])
@auth_required
def delete_compilation(user_id, compilation_id):
    compilation_service = CompilationService(MongoClient, uuid.uuid4, datetime)
    return compilation_service.delete(user_id, compilation_id)

@app.route('/exports/<user_id>/<compilation_id>', methods=['POST'])
@auth_required
def create_export(user_id, compilation_id):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('log-level=3')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    file_service = FileService(MongoClient)

    export = json.loads(request.data)
    export_service = ExportService(MongoClient, uuid.uuid4, datetime, browser, BeautifulSoup, file_service)
    return export_service.create(user_id, compilation_id, export)

@app.route('/exports/<user_id>', methods=['GET'])
@auth_required
def get_exports(user_id):
    export_service = ExportService(MongoClient, uuid.uuid4, datetime, None, BeautifulSoup, None)
    return export_service.get(user_id)

@app.route('/files/<user_id>/<export_id>', methods=['GET'])
@auth_required
def get_file(user_id, export_id):
    file_service = FileService(MongoClient)
    return file_service.get_one(user_id, export_id)

@app.route('/user/login', methods=['POST'])
def login():
    email = get_param(request, 'email')
    password = get_param(request, 'password')

    user_service = UserService(MongoClient, uuid.uuid4, pbkdf2_sha2656)
    return user_service.login(email, password)

@app.route('/user/signup', methods=['POST'])
def signup():
    email = get_param(request, 'email')
    password = get_param(request, 'password')

    user_service = UserService(MongoClient, uuid.uuid4, pbkdf2_sha256)
    return user_service.signup(email, password)

@app.route('/user/logout')
def logout():
    user_service = UserService(MongoClient, uuid.uuid4, pbkdf2_sha256)
    return user_service.logout()

def get_param(r, param_name):
    return json.loads(r.data)[param_name]

app.run()
