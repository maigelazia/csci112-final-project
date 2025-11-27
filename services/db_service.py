from pymongo import MongoClient
import config

_client = MongoClient(config.MONGO_URI)
_db = _client[config.DB_NAME]

def appointments_collection():
    return _db.appointments

def patients_collection():
    return _db.patients
