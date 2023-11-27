import settings

from pymongo.mongo_client import MongoClient

client = MongoClient(settings.mongodb_uri)
db = client.users_db

usersCollection = db['users_collection']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)