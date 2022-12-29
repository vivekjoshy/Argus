import certifi
import pandas as pd
import pymongo
import requests
import streamlit as st
from matplotlib import pyplot as plt, ticker
from matplotlib.backends.backend_agg import RendererAgg
from odmantic import SyncEngine
from pymongo import MongoClient

import argus
from argus.db.models.user import MemberModel
from argus.utils import normalize

# Set Title
st.set_page_config(
    page_title="Argus: Leaderboard",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)
st.title("Argus: Leaderboard")

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
    skill_cursor = (
        db[config["database"]["name"]].member.find().sort("rating", pymongo.DESCENDING)
    )

    st.write("Top 10 Debaters:")

    tabs = (tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10) = st.tabs(
        [f"#{i}" for i in range(1, 11)]
    )

    count = 0
    for skill_mapping in skill_cursor:
        if count == 10:
            break
        member_map = skill_mapping["member"]
        if not member_map:
            continue

        member_id = int(member_map)
        member = engine.find_one(MemberModel, MemberModel.member == member_id)
        r = requests.get(f"{DISCORD_USER_ENDPOINT}/{member_id}", headers=headers)

        count += 1
        data = r.json()
        avatar_hash = str(data["avatar"])
        avatar_url = f"{USER_AVATAR}/{member_id}/{avatar_hash}.png"
        if avatar_hash.startswith("a_"):
            avatar_url = f"{USER_AVATAR}/{member_id}/{avatar_hash}.gif"

        with tabs[count - 1]:
            col1, col2, col3 = st.columns(3)
            with col2:
                st.image(
                    avatar_url,
                    caption=f"{data['username']}#{data['discriminator']}",
                )
                table = {
                    "Server Rank": count,
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
            _lock = RendererAgg.lock
            with _lock:
                plt.style.use("ggplot")
                fig, ax = plt.subplots()
                ax.barh(list(y.keys()), list(y.values()))
                plt.tight_layout()
                ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
                st.pyplot(fig)
