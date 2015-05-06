__author__ = 'poojapawara'

from flask import Flask
import pymongo

app = Flask(__name__)
app.debug = True

conn = pymongo.MongoClient()

db = conn['test']

from app import views