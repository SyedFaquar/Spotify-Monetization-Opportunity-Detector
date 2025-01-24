import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class PodcastEngagementAnalyzer:
    def __init__(self):
        """Initialize the analyzer with necessary directories"""
        # Create directories for outputs
        os.makedirs('data/analysis', exist_ok=True)
        os.makedirs('data/plots', exist_ok=True)
        
        # Dictionary to store analysis results
        self.results = {}
    
    def load_data(self, filepath):
        """Load and prepare podcast data"""
        try:
            # Read data with specific dtypes to avoid conversion issues
            self.df = pd.read_csv(filepath, dtype={
                'episode_id': str,
                'name': str,
                'duration_ms': float,  # Changed to float
                'release_date': str,
                'description': str,
                'explicit': bool,
                'language': str
            })
            
            # Convert duration to minutes
            self.df['duration_minutes'] = self.df['duration_ms'] / (1000 * 60)
            
            # Convert release_date to datetime
            self.df['release_date'] = pd.to_datetime(self.df['release_date'])
            
            print(f"Loaded {len(self.df)} episodes")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def analyze_duration_patterns(self):
        """Analyze episode duration patterns"""
        try:
            duration_stats = {
                'mean_duration': self.df['duration_minutes'].mean(),
                'median_duration': self.df['duration_minutes'].median(),
                'std_duration': self.df['duration_minutes'].std(),
                'min_duration': self.df['duration_minutes'].min(),
                'max_duration': self.df['duration_minutes'].max()
            }
            
            # Create duration distribution plot
            plt.figure(figsize=(10, 6))
            sns.histplot(data=self.df, x='duration_minutes', bins=30)
            plt.title('Episode Duration Distribution')
            plt.xlabel('Duration (minutes)')
            plt.ylabel('Count')
            plt.savefig('data/plots/duration_distribution.png')
            plt.close()
            
            self.results['duration_patterns'] = duration_stats
            return duration_stats
            
        except Exception as e:
            print(f"Error in duration analysis: {e}")
            return None
    
    def analyze_release_patterns(self):
        """Analyze episode release patterns"""
        try:
            # Extract day and hour
            self.df['day_of_week'] = self.df['release_date'].dt.day_name()
            self.df['hour'] = self.df['release_date'].dt.hour
            
            # Analyze patterns
            day_counts = self.df['day_of_week'].value_counts()
            hour_counts = self.df['hour'].value_counts().sort_index()
            
            # Create plots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Plot days
            day_counts.plot(kind='bar', ax=ax1)
            ax1.set_title('Episodes by Day of Week')
            ax1.set_ylabel('Number of Episodes')
            
            # Plot hours
            hour_counts.plot(kind='bar', ax=ax2)
            ax2.set_title('Episodes by Hour')
            ax2.set_xlabel('Hour of Day')
            ax2.set_ylabel('Number of Episodes')
            
            plt.tight_layout()
            plt.savefig('data/plots/release_patterns.png')
            plt.close()
            
            release_patterns = {
                'day_patterns': day_counts.to_dict(),
                'hour_patterns': hour_counts.to_dict()
            }
            
            self.results['release_patterns'] = release_patterns
            return release_patterns
            
        except Exception as e:
            print(f"Error in release pattern analysis: {e}")
            return None
    
    def suggest_ad_breaks(self):
        """Suggest optimal ad break positions"""
        try:
            # Calculate potential break points
            self.df['suggested_breaks'] = pd.cut(
                self.df['duration_minutes'],
                bins=[0, 20, 40, 60, np.inf],
                labels=['1 break', '2 breaks', '3 breaks', '4+ breaks']
            )
            
            break_suggestions = self.df.groupby('suggested_breaks').agg({
                'episode_id': 'count',
                'duration_minutes': ['mean', 'min', 'max']
            }).round(2)
            
            self.results['ad_break_suggestions'] = break_suggestions.to_dict()
            return break_suggestions
            
        except Exception as e:
            print(f"Error in break suggestions: {e}")
            return None
    
    def generate_report(self):
        """Generate a comprehensive engagement report"""
        try:
            # Run all analyses
            self.analyze_duration_patterns()
            self.analyze_release_patterns()
            self.suggest_ad_breaks()
            
            # Create report
            report = "Podcast Engagement Analysis Report\n"
            report += "=" * 50 + "\n\n"
            
            for section, data in self.results.items():
                report += f"\n{section.upper()}\n"
                report += "-" * 50 + "\n"
                report += str(data)
                report += "\n" + "=" * 50 + "\n"
            
            # Save report
            with open('data/analysis/engagement_report.txt', 'w') as f:
                f.write(report)
            
            print("Report generated successfully!")
            return True
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return False

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = PodcastEngagementAnalyzer()
    
    # Load data
    if analyzer.load_data('data/podcast_data_cleaned.csv'):
        # Generate report
        analyzer.generate_report()