from flask import Flask, request, jsonify
from config import Config
from flask_pymongo import PyMongo
from flask_restful import Api
from datetime import datetime, date, timedelta
import requests, uuid, os