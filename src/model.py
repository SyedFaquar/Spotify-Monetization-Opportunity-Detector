import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
import os

class AdPerformanceModel:
    def __init__(self):
        """Initialize the Ad Performance Model"""
        # Create directories for outputs
        os.makedirs('data/models', exist_ok=True)
        os.makedirs('data/plots', exist_ok=True)
        
        # Store model performance metrics
        self.metrics = {}
    
    def load_and_prepare_data(self, filepath):
        """Load and prepare data for modeling"""
        try:
            # Load data
            self.df = pd.read_csv(filepath, dtype={
                'episode_id': str,
                'name': str,
                'duration_ms': float,
                'release_date': str,
                'description': str,
                'explicit': bool,
                'language': str
            })
            
            # Feature engineering
            self.df['duration_minutes'] = self.df['duration_ms'] / (1000 * 60)
            self.df['release_date'] = pd.to_datetime(self.df['release_date'])
            self.df['day_of_week'] = self.df['release_date'].dt.dayofweek
            self.df['hour'] = self.df['release_date'].dt.hour
            
            # Create target variables
            self.create_target_variables()
            
            print(f"Data prepared successfully with {len(self.df)} episodes")
            return True
            
        except Exception as e:
            print(f"Error in data preparation: {e}")
            return False
    
    def create_target_variables(self):
        """Create target variables for ad performance"""
        # Calculate optimal break points based on duration
        self.df['early_break'] = self.df['duration_minutes'] * 0.2  # 20% into episode
        self.df['mid_break'] = self.df['duration_minutes'] * 0.5    # 50% into episode
        self.df['late_break'] = self.df['duration_minutes'] * 0.8   # 80% into episode
        
        # Calculate number of recommended breaks
        self.df['recommended_breaks'] = pd.cut(
            self.df['duration_minutes'],
            bins=[0, 20, 40, 60, np.inf],
            labels=[1, 2, 3, 4]
        ).astype(float)
    
    def build_model_pipeline(self):
        """Build the ML pipeline"""
        # Define features
        numeric_features = ['duration_minutes', 'day_of_week', 'hour']
        categorical_features = ['language']
        
        # Create preprocessing steps
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(drop='first', sparse=False)
        
        # Combine preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        # Create pipeline
        self.pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
    
    def train_break_point_model(self, target='mid_break'):
        """Train model for specific break point"""
        try:
            # Prepare features
            features = self.df[['duration_minutes', 'day_of_week', 'hour', 'language']]
            target_values = self.df[target]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, target_values, test_size=0.2, random_state=42
            )
            
            # Build and fit pipeline
            self.build_model_pipeline()
            self.pipeline.fit(X_train, y_train)
            
            # Make predictions
            y_pred = self.pipeline.predict(X_test)
            
            # Calculate metrics
            mse = np.mean((y_test - y_pred) ** 2)
            rmse = np.sqrt(mse)
            r2 = 1 - (np.sum((y_test - y_pred) ** 2) / np.sum((y_test - y_test.mean()) ** 2))
            
            # Store metrics
            self.metrics[target] = {
                'mse': mse,
                'rmse': rmse,
                'r2': r2
            }
            
            # Create prediction plot
            plt.figure(figsize=(10, 6))
            plt.scatter(y_test, y_pred, alpha=0.5)
            plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
            plt.xlabel('Actual Break Point (minutes)')
            plt.ylabel('Predicted Break Point (minutes)')
            plt.title(f'Actual vs Predicted {target.replace("_", " ").title()}')
            plt.savefig(f'data/plots/{target}_predictions.png')
            plt.close()
            
            return self.metrics[target]
            
        except Exception as e:
            print(f"Error in model training: {e}")
            return None
    
    def predict_ad_breaks(self, episode_data):
        """Predict ad break points for new episodes"""
        try:
            predictions = {}
            
            for break_point in ['early_break', 'mid_break', 'late_break']:
                # Train model if not already trained
                if break_point not in self.metrics:
                    self.train_break_point_model(break_point)
                
                # Make prediction
                pred = self.pipeline.predict(episode_data)[0]
                predictions[break_point] = round(pred, 2)
            
            return predictions
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return None
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        try:
            # Train models for all break points
            for break_point in ['early_break', 'mid_break', 'late_break']:
                self.train_break_point_model(break_point)
            
            # Create report
            report = "Ad Performance Model Report\n"
            report += "=" * 50 + "\n\n"
            
            for break_point, metrics in self.metrics.items():
                report += f"\n{break_point.upper()}\n"
                report += "-" * 50 + "\n"
                for metric, value in metrics.items():
                    report += f"{metric}: {value:.4f}\n"
                report += "=" * 50 + "\n"
            
            # Save report
            with open('data/models/performance_report.txt', 'w') as f:
                f.write(report)
            
            print("Performance report generated successfully!")
            return True
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return False

if __name__ == "__main__":
    # Initialize model
    model = AdPerformanceModel()
    
    # Load and prepare data
    if model.load_and_prepare_data('data/podcast_data_cleaned.csv'):
        # Generate performance report
        model.generate_performance_report()
        
        # Example prediction
        sample_episode = pd.DataFrame({
            'duration_minutes': [45],
            'day_of_week': [2],
            'hour': [9],
            'language': ['en']
        })
        
        predictions = model.predict_ad_breaks(sample_episode)
        if predictions:
            print("\nPredicted break points for 45-minute episode:")
            for break_point, time in predictions.items():
                print(f"{break_point}: {time} minutes")