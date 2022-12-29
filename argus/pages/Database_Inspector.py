import certifi
import pandas as pd
import requests
import streamlit as st
from matplotlib import pyplot as plt, ticker
from odmantic import SyncEngine
from pymongo import MongoClient

import argus
from argus.db.models.user import MemberModel
from argus.utils import normalize

# Set Title
st.set_page_config(
    page_title="Argus: Database Inspector",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
st.title("Argus: Database Inspector")

# Secrets
config = st.secrets

# Constants
DISCORD_API = "https://discord.com/api/v10"
DISCORD_USER_ENDPOINT = f"{DISCORD_API}/users"
IMAGE_BASE_URL = "https://cdn.discordapp.com"
USER_AVATAR = f"{IMAGE_BASE_URL}/avatars/"

AUTHORIZATION_TOKEN = f"Bot {config['bot']['token']}"
USER_AGENT = f"Argus (https://github.com/OpenDebates/Argus, {argus.__version__})"
headers = {"Authorization": AUTHORIZATION_TOKEN, "User-Agent": USER_AGENT}

# Setup Database
db = MongoClient(config["database"]["uri"], tlsCAFile=certifi.where())
engine = SyncEngine(client=db, database=config["database"]["name"])
guild_id = config["global"]["guild_id"]

with st.container():
    raw_member_id = st.text_input("Discord ID: ", max_chars=19)

    if not raw_member_id.isdigit():
        st.error("*Discord IDs can only contain numbers.*")
    elif len(raw_member_id) > 19:
        st.error("*Discord ID is too long.*")
    elif len(raw_member_id) < 16:
        st.error("*Discord ID is too short.*")
    else:
        member_id = int(raw_member_id)
        member = engine.find_one(MemberModel, MemberModel.member == member_id)
        r = requests.get(f"{DISCORD_USER_ENDPOINT}/{member_id}", headers=headers)
        if r.status_code == 404:
            st.error("*User does not exist.*")
        elif member is None:
            st.error("*User is not a member of the server.*")
        else:
            data = r.json()
            avatar_hash = str(data["avatar"])
            avatar_url = f"{USER_AVATAR}/{member_id}/{avatar_hash}.png"
            if avatar_hash.startswith("a_"):
                avatar_url = f"{USER_AVATAR}/{member_id}/{avatar_hash}.gif"

            pipeline = [
                {"$sort": {"rating": -1}},
                {"$group": {"_id": None, "items": {"$push": "$$ROOT"}}},
                {"$unwind": {"path": "$items", "includeArrayIndex": "items.rank"}},
                {"$replaceRoot": {"newRoot": "$items"}},
                {"$addFields": {"newRank": {"$add": ["$rank", 1]}}},
                {"$match": {"member": int(member_id)}},
            ]

            member_found = None
            member_doc = db[config["database"]["name"]].member.aggregate(
                pipeline=pipeline
            )
            for member_found in member_doc:
                break

            if member_found:
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.image(
                        avatar_url,
                        caption=f"{data['username']}#{data['discriminator']}",
                    )
                    table = {
                        "Server Rank": [member_found["rank"] + 1],
                        "Rating": [member.rating],
                        "Mean (µ)": [member.mu],
                        "Confidence Interval (σ)": [member.sigma],
                    }
                    df = pd.DataFrame(table)
                st.table(df)
                y = {
                    "Factual": member.factual,
                    "Consistent": member.consistent,
                    "Charitable": member.charitable,
                    "Respectful": member.respectful,
                }
                y = normalize(y)
                plt.style.use("ggplot")
                fig, ax = plt.subplots()
                ax.barh(list(y.keys()), list(y.values()))
                plt.tight_layout()
                ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
                st.pyplot(fig)
            else:
                st.error("*Database seems to be corrupt. Please contact an engineer.*")
