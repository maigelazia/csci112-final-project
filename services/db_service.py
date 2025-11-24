from pymongo import MongoClient
import config

client = MongoClient(config.MONGO_URI)
db = client[config.DB_NAME]

def appointments_collection():
    return db.appointments

def patients_collection():
    return db.patients