from flask import Flask, request, jsonify
from config import Config
from flask_pymongo import PyMongo
from flask_restful import Api
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
CORS(app)
mongo = PyMongo(app)

from app import routes
