from flask import Flask
from flask_cors import CORS

CACHE = {}
CACHE_DEP = {}
EMPL_DEV = {}    
WORK_TIME = {}
UNDISTRIDUTED_WORKS = {}

import server.updater

updater.upd_start()

app = Flask(__name__)

CORS(app, support_credentials=True)

import server.views

