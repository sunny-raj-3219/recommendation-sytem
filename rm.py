import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import base64

# Initialize Spotify client
CLIENT_ID = "160bcb397044469d9501d534848870c8"
CLIENT_SECRET = "a7f455d473144b8cadaba7c058bd92a7"

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

try:
    results = sp.search(q="artist:Arijit Singh", type="artist")
    print(results)
except Exception as e:
    print("Error connecting to Spotify API:", e)

# Session state for tracking recommendation index, user name, and age
if 'rec_index' not in st.session_state:
    st.session_state.rec_index = 0
if 'name' not in st.session_state:
    st.session_state.name = ""
if 'age' not in st.session_state:
    st.session_state.age = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False  # Track if user has submitted name and age
if 'show_welcome_message' not in st.session_state:
    st.session_state.show_welcome_message = False  # Track if we need to show the welcome message
if 'show_recommendations' not in st.session_state:
    st.session_state.show_recommendations = False  # Track if recommendations are being shown

# Function to convert image to base64
def get_image_base64(file):
    return base64.b64encode(file.read()).decode()

# Path to your background image
background_image_path = "C:/Users/rajsu/OneDrive/Desktop/11/8.jpg"

# Read the image file
with open(background_image_path, "rb") as image_file:
    image_base64 = get_image_base64(image_file)
    page_bg_image = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{image_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0);
    }}
    [data-testid="stToolbar"] {{
        right: 2rem;
    }}
    </style>
    """
    st.markdown(page_bg_image, unsafe_allow_html=True)

# Function to get songs based on artist name
def get_recommendations(recommendation_type, query=None):
    try:
        recommended_songs = []
        recommended_posters = []
        recommended_urls = []

        if recommendation_type == "Artist-Based":
            results = sp.search(q=f"artist:{query}", type="artist", limit=1)
            if results['artists']['items']:
                artist_id = results['artists']['items'][0]['id']
                top_tracks = sp.artist_top_tracks(artist_id)['tracks']
                recommendations = {"tracks": top_tracks}
            else:
                return [], [], []

        # Randomize or paginate the results
        track_list = recommendations['tracks']
        random.shuffle(track_list)

        # Pick the 5 songs based on current index
        for i in range(st.session_state.rec_index, st.session_state.rec_index + 5):
            if i < len(track_list):
                track = track_list[i]
                song_name = track['name']
                album_cover_url = track['album']['images'][0]['url']
                spotify_url = track['external_urls']['spotify']
                recommended_songs.append(song_name)
                recommended_posters.append(album_cover_url)
                recommended_urls.append(spotify_url)

        # Update the index for the next recommendation batch
        st.session_state.rec_index += 5
        if st.session_state.rec_index >= len(track_list):
            st.session_state.rec_index = 0
        return recommended_songs, recommended_posters, recommended_urls

    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return [], [], []

# Function to display clickable posters with the song name in the center
def display_clickable_poster_with_text(url, song_name, link, size=100):
    st.markdown(f"""
        <div style="position: relative; text-align: center; width: {size}px; margin: 10px auto;">
            <a href="{link}" target="_blank">
                <img src="{url}" width="{size}" style="border-radius: 10px;">
                <div style="position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); background-color: rgba(0, 0, 0, 0.8); color: white; width: 100%; padding: 5px 0; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    <strong>{song_name}</strong>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)

# Welcome page
st.markdown("<h1 style='text-align: center; color: #FF5733; margin: 0; padding: 2px 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);'>🎼 TuneHints 🎼</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FFCC00; margin: 0; padding: 2px 0; font-size: 1.8em; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);'>Your Personalized Music Recommendation System</h3>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #FF5733;'>", unsafe_allow_html=True)

if not st.session_state.submitted:
    # Existing input layout...
    col1, col2 = st.columns(2)  # Use columns for input layout
    with col1:
        st.markdown("<p style='color: white; font-size: .9em; margin: 0;'>Enter your name:</p>", unsafe_allow_html=True)
        st.session_state.name = st.text_input("", "", key="name_input")  # Keeping the input box without a label

    with col2:
        st.markdown("<p style='color: white; font-size: .9em; margin: 0;'>Enter your age:</p>", unsafe_allow_html=True)
        st.session_state.age = st.slider(" ", min_value=10, max_value=100, value=25, step=1)

    if st.button("Submit") and st.session_state.name and st.session_state.age:
        st.session_state.submitted = True  # Mark as submitted
        st.session_state.show_welcome_message = True  # Trigger welcome message

# Show welcome message at the top
if st.session_state.show_welcome_message:
    welcome_placeholder = st.empty()  # Create a placeholder for the welcome message
    with welcome_placeholder.container():
        st.markdown(f"""
            <div style="background-color: #FFA597; margin-top: 10px; margin-bottom: 20px; padding-top: 10px; border-radius: 15px;">
                <h6 style='text-align: center; color: black;'>Welcome to TuneHints, {st.session_state.name}! Every song has a story—let’s find yours!</h6>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Proceed to Recommendations"):
            st.session_state.show_welcome_message = False  # Close the welcome message
            st.session_state.show_recommendations = True  # Show recommendations page
            welcome_placeholder.empty()  # Clear the message

# Second welcome message (for example, after getting recommendations)
if st.session_state.show_recommendations:
    # Similar structure for the second welcome message, if applicable
    st.markdown(f"""
        <div style="background-color: #FFA597; margin-top: 10px; margin-bottom: 10px; padding-top: 10px; border-radius: 15px;">
            <h6 style='text-align: center; color: black;'>Welcome back, {st.session_state.name}! Let's get started with your music recommendations!</h6>
        </div>
    """, unsafe_allow_html=True)

    # Recommendation type selectbox (only artist-based)
    st.markdown("<p style='color: white; font-size: 0.9em; margin: 0;'>Enter an artist name:</p>", unsafe_allow_html=True)
    artist_input = st.text_input("", "Arijit Singh", max_chars=20)

    if st.button("Get Recommendations") and artist_input:
        recommended_songs, recommended_posters, recommended_urls = get_recommendations("Artist-Based", artist_input)

        if recommended_songs:
            col1, col2, col3, col4, col5 = st.columns(5, gap="small")

            for i, col in enumerate([col1, col2, col3, col4, col5]):
                if i < len(recommended_songs):
                    with col:
                        display_clickable_poster_with_text(recommended_posters[i], recommended_songs[i], recommended_urls[i])
        else:
            st.warning("No recommendations found. Please try again.")

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------
    # Search-Based Recommendations Section
    st.markdown("<h5 style=' color: #FFCC00; margin: 0; padding: 15px 0; font-size: 1.5em; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);'>🔍 Search-Based Recommendations</h5>", unsafe_allow_html=True)

    # Search input, only show if user has submitted
    st.markdown("<p style='color: white; font-size: .9em; margin: 0;'>Search for a song:</p>", unsafe_allow_html=True)
    search_input = st.text_input("", "Love Dose", max_chars=20)  # Keeping the input box without a label

    # Show search result when button is clicked
    if st.button('Search'):
        results = sp.search(q=search_input, type='track', limit=10)
        search_tracks = results['tracks']['items']

        if search_tracks:
            searched_track = search_tracks[0]
            searched_song_name = searched_track['name']
            searched_album_cover_url = searched_track['album']['images'][0]['url']
            searched_song_url = searched_track['external_urls']['spotify']

            # Display searched song prominently
            st.markdown("<h5 style=' color: #FFCC00; margin: 0; padding: 15px 0; font-size: 1.5em; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);'>Searched Song:</h5>", unsafe_allow_html=True)
            display_clickable_poster_with_text(searched_album_cover_url, searched_song_name, searched_song_url, size=150)  # Larger size for prominence
        else:
            st.write("No songs found for your search.")
