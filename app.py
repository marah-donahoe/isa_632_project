import streamlit as st
import requests

# -------------------------
# CONFIG
# -------------------------
DATABRICKS_URL = st.secrets["DATABRICKS_URL"]
ENDPOINT_NAME = st.secrets["ENDPOINT_NAME"]
TOKEN = st.secrets["TOKEN"]
# -------------------------
# UI
# -------------------------
st.title("🎵 AI Playlist Generator")

user_input = st.text_input(
    "Enter a song, artist, or vibe:",
    placeholder="e.g., Lauryn Hill or sad hip hop vibes"
)

# -------------------------
# CALL ENDPOINT
# -------------------------
def get_playlist(prompt):
    url = f"{DATABRICKS_URL}/serving-endpoints/{ENDPOINT_NAME}/invocations"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        return f"Error: {response.text}"

    data = response.json()

    try:
        return data["output"][0]["content"][0]["text"]
    except:
        return str(data)

# -------------------------
# BUTTON
# -------------------------
if st.button("Generate Playlist"):
    if user_input:
        with st.spinner("Creating your playlist..."):
            result = get_playlist(user_input)
            st.text_area("Your Playlist", result, height=300)
    else:
        st.warning("Please enter a prompt.")
