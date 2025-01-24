import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

class AdPlacementOptimizer:
    def __init__(self):
        """Initialize the Ad Placement Optimizer"""
        # Create output directories
        os.makedirs('data/optimization', exist_ok=True)
        os.makedirs('data/plots', exist_ok=True)
        
        # Configuration parameters
        self.config = {
            'min_gap_minutes': 5,        # Minimum gap between ads
            'max_ads_per_hour': 4,       # Maximum ads per hour
            'optimal_ad_duration': 1.5,   # Standard ad duration in minutes
            'engagement_threshold': 0.7   # Minimum engagement score to place ad
        }
    
    def load_data(self, filepath):
        """Load and prepare podcast data"""
        try:
            self.df = pd.read_csv(filepath)
            self.df['duration_minutes'] = self.df['duration_ms'] / (1000 * 60)
            self.df['release_date'] = pd.to_datetime(self.df['release_date'])
            print(f"Loaded {len(self.df)} episodes")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def calculate_engagement_score(self, time_point, duration):
        """Calculate engagement score for a given time point"""
        # Engagement curve parameters
        peak1 = duration * 0.2  # First peak at 20%
        peak2 = duration * 0.5  # Second peak at 50%
        peak3 = duration * 0.8  # Third peak at 80%
        
        # Calculate distance from peaks
        dist1 = abs(time_point - peak1)
        dist2 = abs(time_point - peak2)
        dist3 = abs(time_point - peak3)
        
        # Get minimum distance to any peak
        min_dist = min(dist1, dist2, dist3)
        
        # Convert distance to score (closer = higher score)
        score = 1 / (1 + min_dist)
        
        return score
    
    def find_optimal_ad_spots(self, duration_minutes):
        """Find optimal ad spots for an episode"""
        try:
            # Calculate maximum number of ads based on duration
            max_ads = min(
                int(duration_minutes / self.config['min_gap_minutes']),
                int(duration_minutes / 60 * self.config['max_ads_per_hour']) + 1
            )
            
            # Generate potential time points
            time_points = np.linspace(
                self.config['min_gap_minutes'],
                duration_minutes - self.config['min_gap_minutes'],
                100
            )
            
            # Calculate engagement scores for all points
            scores = [self.calculate_engagement_score(t, duration_minutes) 
                     for t in time_points]
            
            # Find peaks in engagement scores
            optimal_spots = []
            for i in range(len(scores)):
                if (i == 0 or scores[i] > scores[i-1]) and \
                   (i == len(scores)-1 or scores[i] > scores[i+1]):
                    if scores[i] > self.config['engagement_threshold']:
                        optimal_spots.append({
                            'time': round(time_points[i], 2),
                            'score': round(scores[i], 3)
                        })
            
            # Sort by score and take top max_ads spots
            optimal_spots.sort(key=lambda x: x['score'], reverse=True)
            optimal_spots = optimal_spots[:max_ads]
            
            # Sort by time for final output
            optimal_spots.sort(key=lambda x: x['time'])
            
            return optimal_spots
            
        except Exception as e:
            print(f"Error finding optimal spots: {e}")
            return None
    
    def visualize_ad_placement(self, duration_minutes, optimal_spots):
        """Visualize optimal ad placements"""
        try:
            # Generate time points for plotting
            time_points = np.linspace(0, duration_minutes, 1000)
            scores = [self.calculate_engagement_score(t, duration_minutes) 
                     for t in time_points]
            
            # Create plot
            plt.figure(figsize=(12, 6))
            
            # Plot engagement curve
            plt.plot(time_points, scores, 'b-', label='Engagement Score')
            
            # Plot optimal ad spots
            for spot in optimal_spots:
                plt.axvline(x=spot['time'], color='r', linestyle='--', alpha=0.5)
                plt.plot(spot['time'], spot['score'], 'ro', 
                        label=f"Ad at {spot['time']:.1f} min")
            
            plt.title(f'Optimal Ad Placement for {duration_minutes:.0f} Minute Episode')
            plt.xlabel('Time (minutes)')
            plt.ylabel('Engagement Score')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.savefig('data/plots/ad_placement_visualization.png')
            plt.close()
            
        except Exception as e:
            print(f"Error in visualization: {e}")
    
    def generate_placement_strategy(self, episode_data):
        """Generate complete ad placement strategy"""
        try:
            duration_minutes = episode_data['duration_minutes']
            
            # Find optimal spots
            optimal_spots = self.find_optimal_ad_spots(duration_minutes)
            
            # Calculate expected revenue
            avg_revenue_per_ad = 30  # Example value in dollars
            total_revenue = len(optimal_spots) * avg_revenue_per_ad
            
            # Generate strategy report
            strategy = {
                'episode_duration': duration_minutes,
                'number_of_ads': len(optimal_spots),
                'ad_positions': optimal_spots,
                'estimated_revenue': total_revenue,
                'recommendations': {
                    'ad_duration': self.config['optimal_ad_duration'],
                    'min_gap': self.config['min_gap_minutes'],
                    'engagement_threshold': self.config['engagement_threshold']
                }
            }
            
            # Save strategy
            with open('data/optimization/placement_strategy.json', 'w') as f:
                json.dump(strategy, f, indent=4)
            
            # Create visualization
            self.visualize_ad_placement(duration_minutes, optimal_spots)
            
            return strategy
            
        except Exception as e:
            print(f"Error generating strategy: {e}")
            return None

if __name__ == "__main__":
    # Initialize optimizer
    optimizer = AdPlacementOptimizer()
    
    # Example episode data
    example_episode = {
        'duration_minutes': 45,
        'type': 'interview',
        'day_of_week': 2,
        'hour': 9
    }
    
    # Generate strategy
    strategy = optimizer.generate_placement_strategy(example_episode)
    
    if strategy:
        print("\nOptimal Ad Placement Strategy:")
        print(f"Episode Duration: {strategy['episode_duration']} minutes")
        print(f"Number of Ads: {strategy['number_of_ads']}")
        print("\nAd Positions:")
        for spot in strategy['ad_positions']:
            print(f"- {spot['time']} minutes (score: {spot['score']})")
        print(f"\nEstimated Revenue: ${strategy['estimated_revenue']}")