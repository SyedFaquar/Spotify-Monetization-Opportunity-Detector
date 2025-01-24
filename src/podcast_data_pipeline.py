import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime
import logging
import json
from config import SPOTIFY_CONFIG

class SpotifyPodcastPipeline:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CONFIG['client_id'],
            client_secret=SPOTIFY_CONFIG['client_secret']
        ))
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename=f'podcast_pipeline_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )


    def extract_show_id(url):
        """Extract show ID from Spotify URL"""
        return url.split('show/')[-1].split('?')[0]
        

    def fetch_podcast_data(self, show_id):
        """Fetch podcast show and episode data"""
        try:
            show = self.sp.show(show_id)
            episodes = self.get_all_episodes(show_id)
            return show, episodes
        except Exception as e:
            logging.error(f"Error fetching podcast data: {str(e)}")
            return None, None
            

    def get_all_episodes(self, show_id):
        """Fetch all episodes of a podcast"""
        episodes = []
        results = self.sp.show_episodes(show_id)
        
        while results:
            episodes.extend(results['items'])
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        return episodes


    def process_episode_data(self, episodes):
        """Extract relevant features from episodes"""
        processed_data = []
        
        for episode in episodes:
            if episode is not None:  # Check if episode exists
                try:
                    episode_data = {
                        'episode_id': episode.get('id', ''),
                        'name': episode.get('name', ''),
                        'duration_ms': episode.get('duration_ms', 0),
                        'release_date': episode.get('release_date', ''),
                        'description': episode.get('description', ''),
                        'explicit': episode.get('explicit', False),
                        'language': episode.get('language', '')
                    }
                    processed_data.append(episode_data)
                except Exception as e:
                    logging.error(f"Error processing episode: {str(e)}")
                    continue
            
        if not processed_data:
            logging.warning("No valid episodes found to process")
            return pd.DataFrame()  # Return empty DataFrame if no valid episodes
            
        return pd.DataFrame(processed_data)


    def save_data(self, df, filename):
        """Save processed data to CSV"""
        try:
            # Create data directory if it doesn't exist
            import os
            os.makedirs('data', exist_ok=True)
            
            # Save the data
            filepath = f'data/{filename}.csv'
            df.to_csv(filepath, index=False)
            logging.info(f"Data saved successfully to {filepath}")
            print(f"Data saved to: {os.path.abspath(filepath)}")
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")

            
    def run_pipeline(self, show_ids):
        """Run the complete pipeline for multiple shows"""
        all_episodes_data = []
        
        for show_id in show_ids:
            show, episodes = self.fetch_podcast_data(show_id)
            if show and episodes:
                processed_data = self.process_episode_data(episodes)
                all_episodes_data.append(processed_data)
                
        if all_episodes_data:
            final_df = pd.concat(all_episodes_data, ignore_index=True)
            self.save_data(final_df, f'podcast_data_{datetime.now().strftime("%Y%m%d")}')
            return final_df
        return None

# Usage Example
if __name__ == "__main__":
    pipeline = SpotifyPodcastPipeline()

    # List of show IDs to process
    show_ids = ['6E1u3kxII5CbbFR4VObax4', '1VXcH8QHkjRcTCEd88U3ti', '4fsW5D9rKYycsP2hgKtvCk', '5RdShpOtxKO3ZWohR2M6Sv', '0ofXAdFIQQRsCYj9754UFx', 
                '4rOoJ6Egrf8K2IrywzwOMk', '3gaGfrqgnVqUBNDdtv5p3S', '7wkYuqWC8z51nfetiZCTbT', '2HGcJRYrjGnpce6bRp8UXm', '5VzFvh1JlEhBMS6ZHZ8CNO']  
    
    podcast_data = pipeline.run_pipeline(show_ids) 