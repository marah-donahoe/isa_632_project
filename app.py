import streamlit as st
import requests
import re
import random
import time

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Playlist Generator",
    page_icon="🎵",
    layout="wide"
)

# -------------------------
# CUSTOM CSS
# -------------------------
st.markdown("""
<style>

.main {
    padding-top: 2rem;
}

.big-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.subtitle {
    font-size: 1.1rem;
    color: #888;
    margin-bottom: 2rem;
}

.song-card {
    padding: 1rem;
    border-radius: 12px;
    background-color: #1e1e1e;
    border: 1px solid #333;
    margin-bottom: 0.75rem;
}

.song-title {
    font-size: 1.1rem;
    font-weight: 600;
}

.song-artist {
    color: #999;
    font-size: 0.95rem;
}

.playlist-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.section-header {
    font-size: 1.3rem;
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

.stButton button {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIG
# -------------------------
DATABRICKS_URL = st.secrets["DATABRICKS_URL"]
TOKEN = st.secrets["TOKEN"]
ENDPOINT_NAME = st.secrets["ENDPOINT_NAME"]

# -------------------------
# SESSION STATE
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "playlist_history" not in st.session_state:
    st.session_state.playlist_history = []

# -------------------------
# HEADER
# -------------------------
st.markdown('<div class="big-title">🎵 AI Playlist Generator</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Generate playlists using songs, artists, lyrics, or vibes.</div>',
    unsafe_allow_html=True
)

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:

    st.header("Playlist Settings")

    mood = st.selectbox(
        "Mood",
        [
            "Any",
            "Chill",
            "Sad",
            "Energetic",
            "Romantic",
            "Late Night",
            "Dreamy",
            "Aggressive",
            "Nostalgic",
            "Happy"
        ]
    )

    num_songs = st.slider(
        "Number of Songs",
        min_value=5,
        max_value=25,
        value=10
    )

    st.divider()

    st.subheader("Prompt Ideas")

    example_prompts = [
        "late night r&b vibes",
        "sad indie breakup songs",
        "songs like Frank Ocean",
        "dreamy female vocals",
        "2000s pop nostalgia",
        "melancholy rap songs",
        "gym hype music",
        "songs like SZA but happier"
    ]

    for example in example_prompts:
        if st.button(example):
            st.session_state.selected_prompt = example

# -------------------------
# TABS
# -------------------------
tab1, tab2 = st.tabs(["🎧 Generator", "📜 Playlist History"])

# -------------------------
# API CALL
# -------------------------
def get_playlist(messages):

    url = f"{DATABRICKS_URL}/serving-endpoints/{ENDPOINT_NAME}/invocations"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": messages
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
        return f"Error: {response.text}"

    data = response.json()

    try:
        output = data.get("output", [])

        if output:
            content = output[0].get("content", [])

            if content:
                return content[0].get("text", "No response.")

        return "No response returned."

    except Exception as e:
        return f"Parsing error: {e}"

# -------------------------
# PLAYLIST PARSER
# -------------------------
def parse_playlist(text):

    playlist_title = "Generated Playlist"

    title_match = re.search(
        r"Playlist Title:\s*(.*)",
        text
    )

    if title_match:
        playlist_title = title_match.group(1).strip()

    songs = []

    song_matches = re.findall(
        r"\d+\.\s*(.*?)\s*:\s*(.*)",
        text
    )

    for match in song_matches:
        title = match[0].strip()
        artist = match[1].strip()

        songs.append({
            "title": title,
            "artist": artist
        })

    return playlist_title, songs

# -------------------------
# GENERATOR TAB
# -------------------------
with tab1:

    left_col, right_col = st.columns([1, 2])

    wwith left_col:

    st.markdown("### Enter a Prompt")

    default_prompt = st.session_state.get("selected_prompt", "")

    # -------------------------
    # CTRL + ENTER SUPPORT (JS)
    # -------------------------
    st.components.v1.html("""
    <script>
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            const btn = window.parent.document.querySelector('button[kind="formSubmit"]');
            if (btn) {
                btn.click();
            }
        }
    });
    </script>
    """, height=0)

    # -------------------------
    # FORM (handles Enter key)
    # -------------------------
    with st.form("playlist_form"):

        user_input = st.text_area(
            "Describe your playlist",
            value=default_prompt,
            placeholder="e.g., sad hip hop vibes or songs like Lauryn Hill",
            height=120
        )

        generate = st.form_submit_button(
            "Generate Playlist",
            use_container_width=True
        )

    with right_col:

        if generate and user_input:

            full_prompt = (
                f"🎧 Playlist Request\n\n"
                f"🎵 Mood: {mood}\n"
                f"🔢 Number of Songs: {num_songs}\n\n"
                f"📝 User Request:\n{user_input}\n\n"
                f"---\n"
                f"Return a playlist with title and songs in order."
            )

            st.session_state.messages.append({
                "role": "user",
                "content": full_prompt
            })

            loading_messages = [
                "Analyzing lyrics...",
                "Searching similar songs...",
                "Building playlist flow...",
                "Finding matching vibes...",
                "Generating recommendations..."
            ]

            loading_placeholder = st.empty()

            for i in range(3):
                loading_placeholder.info(random.choice(loading_messages))
                time.sleep(0.5)

            response = get_playlist(st.session_state.messages)

            loading_placeholder.empty()

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.session_state.playlist_history.append(response)

        # -------------------------
        # DISPLAY CHAT HISTORY
        # -------------------------
      for message in reversed(st.session_state.messages):

            if message["role"] == "user":

                with st.chat_message("user"):
                    st.write(message["content"])

            elif message["role"] == "assistant":

                with st.chat_message("assistant"):

                    playlist_title, songs = parse_playlist(
                        message["content"]
                    )

                    st.markdown(
                        f'<div class="playlist-title">{playlist_title}</div>',
                        unsafe_allow_html=True
                    )

                    if songs:

                        for i, song in enumerate(songs):

                            with st.container():

                                st.markdown(
                                    f"""
                                    <div class="song-card">
                                        <div class="song-title">
                                            {i+1}. {song['title']}
                                        </div>
                                        <div class="song-artist">
                                            {song['artist']}
                                        </div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    else:
                        st.write(message["content"])

# -------------------------
# HISTORY TAB
# -------------------------
with tab2:

    st.markdown("### Previous Playlists")

    if not st.session_state.playlist_history:
        st.info("No playlists generated yet.")

    else:

        for idx, playlist in enumerate(
            reversed(st.session_state.playlist_history)
        ):

            playlist_title, songs = parse_playlist(playlist)

            with st.expander(
                f"{playlist_title}",
                expanded=False
            ):

                if songs:

                    for i, song in enumerate(songs):

                        st.markdown(
                            f"""
                            <div class="song-card">
                                <div class="song-title">
                                    {i+1}. {song['title']}
                                </div>
                                <div class="song-artist">
                                    {song['artist']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                else:
                    st.write(playlist)