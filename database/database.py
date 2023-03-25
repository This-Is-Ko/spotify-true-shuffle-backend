from flask_pymongo import PyMongo
from flask import current_app
from main import mongo
import pymongo
from pymongo.collection import ReturnDocument

# Liked tracks history functions


def insert_liked_tracks_history_entry(tracker_entry):
    return mongo.db.liked_tracks_history.insert_one(tracker_entry)


def find_user_latest_liked_tracks_history_entry(user_id):
    return mongo.db.liked_tracks_history.find_one(
        {"user_id": user_id},
        sort=[('_id', pymongo.DESCENDING)]
    )


def get_all_user_liked_tracks_history_data(user_id):
    return mongo.db.liked_tracks_history.find(
        {"user_id": user_id},
        # {"user_id": 0, "_id": 0},
        sort=[('_id', pymongo.DESCENDING)]
    )


# Shuffled history functions
# Schema
# {
#    "user_id": user_id,
#    "count": current_count,
#    "difference": difference,
# }


def get_all_user_shuffle_history_data(user_id):
    return mongo.db.shuffle_history.find(
        {"user_id": user_id},
        {"user_id": 0, "_id": 0},
        sort=[('_id', pymongo.DESCENDING)]
    )

# Shuffled history total shuffle counters functions


def find_shuffle_counter(user_id):
    return mongo.db.shuffle_history.find_one(
        {"user_id": user_id}
    )


def find_and_update_shuffle_counter(user_id, shuffle_history_counter):
    return mongo.db.shuffle_history.find_one_and_update(
        {"user_id": user_id},
        {"$set": shuffle_history_counter},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


# User functions


def find_and_update_user(user_id, user_entry):
    return mongo.db.users.find_one_and_update(
        {"user_id": user_id},
        {"$set": user_entry},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def find_user(user_id):
    return mongo.db.users.find_one(
        {"user_id": user_id}
    )


def get_all_users_with_attribute(attribute_name, attribute_value):
    return mongo.db.users.find({"user_attributes." + attribute_name: attribute_value})
