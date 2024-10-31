from dotenv import load_dotenv
from requests import get, post
import os
import base64
import json

# THIS IS A MINI LIBRARY IMPLEMENETATION OF METHODS THAT CAN WORK ON A CLIENT CREDITIONAL APPLICATION OF THE API

# Load environment variables (client ID and secret) from .env file
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Function to get the OAuth token from Spotify API
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    
    # Parse the JSON response and retrieve the access token
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

# Helper function to format the authorization header for Spotify API requests
def get_auth_header(token):
    return {"Authorization":"Bearer " + token}

# Album-related code:

# Function to get the album ID from Spotify using the album name
def get_album_id(token, album_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={album_name}&type=album&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    
    # Check if the search returns a valid album
    if "albums" in json_result and json_result["albums"]["items"]:
        album_id = json_result["albums"]["items"][0]["id"]
        return album_id
    else:
        print("Nothing was found from the search")
        return None

# Function to search for an album and return its details
def search_for_album(token, album_name):
    album_id = get_album_id(token, album_name)
    url = f"https://api.spotify.com/v1/albums/"
    query_url = url + album_id
    headers = get_auth_header(token)
    result = get(query_url, headers=headers)
    
    # Return the album details as a JSON object
    json_result = json.loads(result.content)
    return json_result

# Artist-related code:

# Function to search for an artist and return the first result
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    
    # Parse the JSON result to get the artist details
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("nothing was found from the search")
        return None    
    return json_result[0]

# Function to get the artist ID by artist name
def get_artist_id(token, artist_name):
    result = search_for_artist(token, artist_name)
    
    # Return the artist's ID if found
    if "id" in result:
        return result["id"]
    else:
        return "None"

# Function to retrieve top tracks by an artist
def get_songs_by_artist(token, artist_name):
    artist_id = get_artist_id(token, artist_name)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    
    # Parse and display the tracks in the response
    json_result = json.loads(result.content)
    if "tracks" in json_result:
        songs = json_result["tracks"]
        for idx, song in enumerate(songs):
            print(f"{idx + 1}. {song['name']}")
        return json_result["tracks"]
    else:
        print("nothing was found")
        return None

# Function to get related artists by artist name
def get_related_artists(token, artist_name):
    artist_id = get_artist_id(token, artist_name)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/related-artists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    
    # Parse and display the related artists in the response
    json_result = json.loads(result.content)
    if "artists" in json_result:
        artists = json_result["artists"]
        for idx, artist in enumerate(artists):
            print(f"{idx + 1}. {artist['name']}")
        return json_result["artists"]
    else:
        print("nothing was found")
        return None

# Songs/tracks-related code:

# Function to search for a song and return its details
def search_for_song(token, song_name):
    song_id = get_song_id(token, song_name)
    url = f"https://api.spotify.com/v1/tracks/"
    query_url = url + song_id
    headers = get_auth_header(token)
    result = get(query_url, headers=headers)
    
    # Return the song details as a JSON object
    json_result = json.loads(result.content)
    return json_result

# Function to get the song ID from Spotify using the song name
def get_song_id(token, song_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={song_name}&type=track&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    
    # Check if the search returns a valid track
    json_result = json.loads(result.content)
    if "tracks" in json_result and json_result["tracks"]["items"]:
        track_id = json_result["tracks"]["items"][0]["id"]
        return track_id
    else:
        print("Nothing was found from the search")
        return None

# Recommended songs-related code:

# Function to get recommended songs based on various parameters (artists, genres, tracks, etc.)
def recommended_songs(token, seed_artists, seed_genres, seed_tracks, 
                      target_danceability=None,
                      target_energy=None,
                      target_valence=None,
                      target_popularity=None,
                      target_acousticness=None,
                      target_instrumentalness=None,
                      target_tempo=None):
    url = create_recommendations_url(seed_artists, seed_genres, seed_tracks, 
                                     target_danceability, target_energy, target_valence, 
                                     target_popularity, target_acousticness, 
                                     target_instrumentalness, target_tempo)
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    
    # Parse and display the recommended tracks in the response
    json_result = json.loads(result.content)
    if "tracks" in json_result:
        tracks = json_result["tracks"]
        for idx, track in enumerate(tracks):
            print(f"{idx + 1}. {track['name']} by {track['artists'][0]['name']}")
        return tracks
    else:
        print("No recommendations found")
        return None

# Helper function to create a recommendation URL with optional filter parameters
def create_recommendations_url(seed_artists, seed_genres, seed_tracks, 
                               target_danceability=None,
                               target_energy=None,
                               target_valence=None,
                               target_popularity=None,
                               target_acousticness=None,
                               target_instrumentalness=None,
                               target_tempo=None):
    url = (f"https://api.spotify.com/v1/recommendations?"
           f"seed_artists={seed_artists}&seed_genres={seed_genres}&seed_tracks={seed_tracks}")
    
    # Add optional parameters to the URL if provided
    if target_danceability is not None: url += f"&target_danceability={target_danceability}"
    if target_energy is not None: url += f"&target_energy={target_energy}"
    if target_valence is not None: url += f"&target_valence={target_valence}"
    if target_popularity is not None: url += f"&target_popularity={target_popularity}"
    if target_acousticness is not None: url += f"&target_acousticness={target_acousticness}"
    if target_instrumentalness is not None: url += f"&target_instrumentalness={target_instrumentalness}"
    if target_tempo is not None: url += f"&target_tempo={target_tempo}"

    return url

# Playlist-related code:

# Get current user's playlists
def get_user_playlists(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    if "items" in json_result:
        playlists = json_result["items"]
        for idx, playlist in enumerate(playlists):
            print(f"{idx + 1}. {playlist['name']}")
        return playlists
    else:
        print("No playlists found")
        return None

# Create a new playlist for the user
def create_playlist(token, user_id, playlist_name, description="", public=False):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    data = {
        "name": playlist_name,
        "description": description,
        "public": public
    }
    result = post(url, headers=headers, json=data)
    json_result = json.loads(result.content)
    return json_result

# Add tracks to a playlist
def add_tracks_to_playlist(token, playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    data = {
        "uris": track_uris
    }
    result = post(url, headers=headers, json=data)
    return json.loads(result.content)

# Remove tracks from a playlist
def remove_tracks_from_playlist(token, playlist_id, track_uris):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    data = {
        "tracks": [{"uri": uri} for uri in track_uris]
    }
    result = requests.delete(url, headers=headers, json=data)
    return json.loads(result.content)

# User profile-related code:

# Get current user's profile
def get_current_user_profile(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)

# Get another user's profile by ID
def get_user_profile(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)

# Library-related code:

# Save albums to the library
def save_albums_to_library(token, album_ids):
    url = "https://api.spotify.com/v1/me/albums"
    headers = get_auth_header(token)
    data = {
        "ids": album_ids
    }
    result = post(url, headers=headers, json=data)
    return json.loads(result.content)

# Remove albums from the library
def remove_albums_from_library(token, album_ids):
    url = "https://api.spotify.com/v1/me/albums"
    headers = get_auth_header(token)
    data = {
        "ids": album_ids
    }
    result = requests.delete(url, headers=headers, json=data)
    return json.loads(result.content)

# Check if albums are in the library
def check_albums_in_library(token, album_ids):
    url = f"https://api.spotify.com/v1/me/albums/contains?ids={','.join(album_ids)}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)

# Player-related code:

# Get current playback state
def get_current_playback(token):
    url = "https://api.spotify.com/v1/me/player"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)

# Skip to the next track
def skip_to_next_track(token):
    url = "https://api.spotify.com/v1/me/player/next"
    headers = get_auth_header(token)
    result = post(url, headers=headers)
    return result.status_code  # 204 means successful

# Skip to the previous track
def skip_to_previous_track(token):
    url = "https://api.spotify.com/v1/me/player/previous"
    headers = get_auth_header(token)
    result = post(url, headers=headers)
    return result.status_code  # 204 means successful

# Pause playback
def pause_playback(token):
    url = "https://api.spotify.com/v1/me/player/pause"
    headers = get_auth_header(token)
    result = post(url, headers=headers)
    return result.status_code  # 204 means successful

# Resume playback
def resume_playback(token):
    url = "https://api.spotify.com/v1/me/player/play"
    headers = get_auth_header(token)
    result = post(url, headers=headers)
    return result.status_code  # 204 means successful

# Set playback volume (volume percent between 0-100)
def set_volume(token, volume_percent):
    url = f"https://api.spotify.com/v1/me/player/volume?volume_percent={volume_percent}"
    headers = get_auth_header(token)
    result = post(url, headers=headers)
    return result.status_code  # 204 means successful

# Follow-related code:

# Follow an artist or user
def follow_artist_or_user(token, artist_ids, type="artist"):
    url = f"https://api.spotify.com/v1/me/following?type={type}"
    headers = get_auth_header(token)
    data = {
        "ids": artist_ids
    }
    result = put(url, headers=headers, json=data)
    return json.loads(result.content)

# Unfollow an artist or user
def unfollow_artist_or_user(token, artist_ids, type="artist"):
    url = f"https://api.spotify.com/v1/me/following?type={type}"
    headers = get_auth_header(token)
    data = {
        "ids": artist_ids
    }
    result = requests.delete(url, headers=headers, json=data)
    return result.status_code  # 204 means successful

# Check if user is following an artist or user
def check_following(token, artist_ids, type="artist"):
    url = f"https://api.spotify.com/v1/me/following/contains?type={type}&ids={','.join(artist_ids)}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return json.loads(result.content)



token = get_token()

songs = recommended_songs(token, get_artist_id(token, "tul8ate"), "country, classical", get_song_id(token, "layalina"))





