import pymongo
from pymongo import MongoClient

client = pymongo.MongoClient("mongodb+srv://nonagon-test:test123@nonagon-db.cgyrqbh.mongodb.net/?retryWrites=true&w=majority")
db = client["nonagon-bot"]


collection = db["guild-data"]

# database -> collection -> post (each post must have a _id or else its autogenerated)

collection.insert_one({})