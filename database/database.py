from flask_pymongo import PyMongo
from flask import current_app
from main import mongo
import pymongo
from pymongo.collection import ReturnDocument


def insert_liked_tracks_history_entry(tracker_entry):
    return mongo.db.liked_tracks_history.insert_one(tracker_entry)


def find_user_latest_liked_tracks_history_entry(user_id):
    return mongo.db.liked_tracks_history.find_one(
        {"user_id": user_id},
        sort=[('_id', pymongo.DESCENDING)]
    )


def add_user():
    users_collection = mongo.db.users.find()


def find_and_update_user(user_id, user_attributes):
    return mongo.db.users.find_one_and_update(
        {"user_id": user_id},
        {"$set": user_attributes},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def find_user(user_id):
    return mongo.db.users.find_one(
        {"user_id": user_id}
    )


def get_all_users_with_attribute(attribute_name, attribute_value):
    return mongo.db.users.find({attribute_name: attribute_value})
