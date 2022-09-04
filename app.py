import json
import uuid
import os

from flask import Flask, request, session, jsonify
from flask_cors import CORS, cross_origin
from functools import wraps
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import unquote

from backend import CompilationService
from backend import ExportService
from backend import FileService
from backend import UserService
from backend import BackgroundService
from backend import ThumbnailService
from backend import EmailUtils

app = Flask(__name__, static_folder='client/build', static_url_path='')
app.secret_key = 'J7g2#G7g73$fk2v6V6a!7v3KV37vd6'#os.environ.get('FLASK_SECRET_KEY')
cors = CORS(app, supports_credentials=True)
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
    compilation_service = CompilationService(MongoClient, uuid, datetime)
    return compilation_service.create(user_id, compilation)

@app.route('/compilations/<user_id>', methods=['GET'])
@auth_required
def get_compilations(user_id):
    compilation_service = CompilationService(MongoClient, uuid, datetime)
    return compilation_service.get(user_id)

@app.route('/compilations/<user_id>/<compilation_id>', methods=['GET'])
@auth_required
def get_compilation(user_id, compilation_id):
    compilation_service = CompilationService(MongoClient, uuid, datetime)
    return compilation_service.get_one(user_id, compilation_id)

@app.route('/compilations/<user_id>/<compilation_id>', methods=['PATCH'])
@auth_required
def update_compilation(user_id, compilation_id):
    compilation = json.loads(request.data)
    compilation_service = CompilationService(MongoClient, uuid, datetime)
    return compilation_service.update(user_id, compilation_id, compilation)

@app.route('/compilations/<user_id>/<compilation_id>', methods=['DELETE'])
@auth_required
def delete_compilation(user_id, compilation_id):
    compilation_service = CompilationService(MongoClient, uuid, datetime)
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
    export_service = ExportService(MongoClient, uuid, datetime, browser, BeautifulSoup, file_service)
    return export_service.create(user_id, compilation_id, export)

@app.route('/exports/<user_id>', methods=['GET'])
@auth_required
def get_exports(user_id):
    export_service = ExportService(MongoClient, uuid, datetime, None, BeautifulSoup, None)
    return export_service.get(user_id)

@app.route('/files/<user_id>/<file_id>', methods=['GET'])
@auth_required
def get_file(user_id, file_id):
    type = request.args.get('type')
    file_service = FileService(MongoClient)
    return file_service.get_one(user_id, file_id, type)

@app.route('/thumbnails/<path:url>', methods=['GET'])
@auth_required
def get_thumbnail(url):
    thumbnail_service = ThumbnailService(BeautifulSoup)
    return thumbnail_service.get_one(unquote(url))

@app.route('/backgrounds/<user_id>', methods=['POST'])
@auth_required
def create_background(user_id):
    print(request.form['name'])
    print(request.form['file'])
    background = {}#json.loads(request.data)
    #print(request.data)

    background_service = BackgroundService(MongoClient, uuid)
    return background_service.create(user_id, background)

@app.route('/user/me', methods=['GET'])
@cross_origin()
def me():
    response = jsonify(session['user'])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200

@app.route('/user/login', methods=['POST'])
@cross_origin()
def login():
    email = get_param(request, 'email')
    password = get_param(request, 'password')

    user_service = UserService(MongoClient, uuid, pbkdf2_sha256, datetime, None)

    login_response, status = user_service.login(email, password)
    response = jsonify(login_response)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, status

@app.route('/user/signup', methods=['POST'])
@cross_origin()
def signup():
    email = get_param(request, 'email')
    password = get_param(request, 'password')

    email_utils = EmailUtils()

    user_service = UserService(MongoClient, uuid, pbkdf2_sha256, datetime, email_utils)

    signup_response, status = user_service.signup(email, password)
    response = jsonify(signup_response)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response, status

@app.route('/user/logout')
def logout():
    user_service = UserService(MongoClient, uuid, pbkdf2_sha256, datetime, None)
    return user_service.logout()

@app.route('/user/confirm/<user_id>/<confirmation_code>')
def confirm(user_id, confirmation_code):
    user_service = UserService(MongoClient, uuid, pbkdf2_sha256, datetime, None)
    return user_service.confirm(user_id, confirmation_code)

@app.route('/user/forgot/<user_id>')
def forgot(user_id):
    email_utils = EmailUtils()
    user_service = UserService(MongoClient, uuid, pbkdf2_sha256, datetime, email_utils)
    return user_service.forgot(user_id)

@app.route('/user/change_password/<user_id>/<change_password_code>', methods=['POST'])
def change_password(user_id, change_password_code):
    new_password = get_param(request, 'new_password')
    user_service = UserService(MongoClient, uuid, pbkdf2_sha256, datetime, None)
    return user_service.change_password(user_id, change_password_code, new_password)

def get_param(r, param_name):
    return json.loads(r.data)[param_name]

app.run()
