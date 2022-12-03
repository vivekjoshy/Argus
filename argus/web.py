import pymongo
import streamlit as st
from odmantic import SyncEngine

from argus.config import config
from argus.db.mongo import MongoClient

# Set Title
st.title("Argus - Leaderboard")

# Setup Database
db = MongoClient(config=config)
engine = SyncEngine(client=db, database=config["database"]["name"])


guild_id = config["global"]["guild_id"]
skill_cursor = db[db.database].member.find().sort("rating", pymongo.DESCENDING)

skill_ratings = []
for skill_mapping in skill_cursor:
    skill_ratings.append((skill_mapping["member"], skill_mapping["rating"]))


st.write(skill_ratings)
