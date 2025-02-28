from flask_pymongo import PyMongo
from main import mongo
import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId
from utils.constants import USER_ID_KEY


# Liked tracks history functions
def insert_liked_tracks_history_entry(tracker_entry):
    return mongo.db.liked_tracks_history.insert_one(tracker_entry)


def find_user_latest_liked_tracks_history_entry(user_id):
    return mongo.db.liked_tracks_history.find_one(
        {USER_ID_KEY: user_id},
        sort=[('_id', pymongo.DESCENDING)]
    )


def get_all_user_liked_tracks_history_data(user_id):
    return mongo.db.liked_tracks_history.find(
        {USER_ID_KEY: user_id},
        # {USER_ID_KEY: 0, "_id": 0},
        sort=[('_id', pymongo.ASCENDING)]
    )


# Shuffled history functions
# Schema
# {
#    USER_ID_KEY: user_id,
#    "count": current_count,
#    "difference": difference,
# }


def get_all_user_shuffle_history_data(user_id):
    return mongo.db.shuffle_history.find(
        {USER_ID_KEY: user_id},
        {USER_ID_KEY: 0, "_id": 0},
        sort=[('_id', pymongo.DESCENDING)]
    )

# Shuffled history total shuffle counters functions


def find_shuffle_counter(user_id):
    return mongo.db.shuffle_history.find_one(
        {USER_ID_KEY: user_id}
    )


def find_and_update_shuffle_counter(user_id, shuffle_history_counter):
    return mongo.db.shuffle_history.find_one_and_update(
        {USER_ID_KEY: user_id},
        {"$set": shuffle_history_counter},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


# Track statistics update function
def update_track_statistics(tracks):
    """
    Increments the shuffle count or inserts new tracks if missing.
    """
    bulk_updates = [
        pymongo.UpdateOne(
            {"track_id": track["id"]},
            {
                "$set": {
                    "track_name": track["name"],
                    "artists": [
                        {"artist_id": artist["id"], "artist_name": artist["name"]}
                        for artist in track["artists"]
                    ]
                },
                "$inc": {"shuffle_count": 1}
            },
            upsert=True
        )
        for track in tracks
    ]

    if bulk_updates:
        mongo.db.track_statistics.bulk_write(bulk_updates)


def get_top_tracks(limit: int):
    """
    Retrieves the top shuffled tracks sorted by shuffle count.
    """
    return mongo.db.track_statistics.find(
        {},
        {"_id": 0, "track_id": 1, "track_name": 1, "shuffle_count": 1}
    ).sort("shuffle_count", -1).limit(limit)


def get_top_artists(limit: int):
    """
    Aggregates shuffle counts by artist and returns the top artists.
    """
    pipeline = [
        # Unwind the artists array to treat each artist separately
        {"$unwind": "$artists"},
        # Group by artist_id and sum shuffle_count
        {"$group": {
            "_id": "$artists.artist_id",
            "artist_name": {"$first": "$artists.artist_name"},
            "total_shuffles": {"$sum": "$shuffle_count"}
        }},
        {"$sort": {"total_shuffles": -1}},
        {"$limit": limit},
        {"$project": {
            "_id": 0,
            "artist_id": "$_id",
            "artist_name": 1,
            "total_shuffles": 1
        }}
    ]

    return list(mongo.db.track_statistics.aggregate(pipeline))


# User functions


def find_and_update_user(user_id, user_entry):
    return mongo.db.users.find_one_and_update(
        {USER_ID_KEY: user_id},
        {"$set": user_entry},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def find_user(user_id):
    return mongo.db.users.find_one(
        {USER_ID_KEY: user_id}
    )


def get_all_users_with_attribute(attribute_name, attribute_value):
    return mongo.db.users.find({"user_attributes." + attribute_name: attribute_value})


# Session functions

def find_session(session_id):
    return mongo.db.sessions.find_one(
        {"session_id": session_id}
    )


def find_and_update_session(hashed_session_id, session_entry):
    return mongo.db.sessions.find_one_and_update(
        {"session_id": hashed_session_id},
        {"$set": session_entry},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )


def delete_session(session_id):
    return mongo.db.sessions.delete_one(
        {"session_id": session_id},
    )


def delete_expired_session(current_datetime):
    return mongo.db.sessions.delete_many(
        {"session_expiry": {"$lt": current_datetime}},
    )
