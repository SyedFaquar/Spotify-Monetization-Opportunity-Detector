import os
from config import SPOTIFY_CONFIG
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#function to test spotify connection
def test_spotify_connection():
    try:
        auth_manager = SpotifyClientCredentials(
            client_id=SPOTIFY_CONFIG['client_id'],
            client_secret=SPOTIFY_CONFIG['client_secret']
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        results = sp.search(q='podcast', type='show', limit=1)
        
        if results:
            print("✅ Connection successful!")
            print(f"Test search result: {results['shows']['items'][0]['name']}")
        return True
        
    except Exception as e:
        print("❌ Connection failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_spotify_connection()