import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import os

class TestBasicFunctionality(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        print("\nSetting up test data...")
        try:
            # Create test data with explicit data types
            self.test_data = pd.DataFrame({
                'episode_id': pd.Series(['test1', 'test2', 'test3'], dtype='string'),
                'name': pd.Series(['Episode 1', 'Episode 2', 'Episode 3'], dtype='string'),
                'duration_ms': pd.Series([1800000, 2700000, 3600000], dtype='int64'),
                'release_date': pd.Series(['2025-01-01', '2025-01-02', '2025-01-03'], dtype='string'),
                'description': pd.Series(['Test 1', 'Test 2', 'Test 3'], dtype='string'),
                'explicit': pd.Series([False, False, True], dtype='bool'),
                'language': pd.Series(['en', 'en', 'en'], dtype='string')
            })
            
            # Create data directory
            os.makedirs('data', exist_ok=True)
            
            # Save test data with specific dtypes
            self.test_data.to_csv('data/test_data.csv', index=False)
            print("Test data setup complete")
            
        except Exception as e:
            print(f"Error in setup: {str(e)}")
            print(f"Error type: {type(e)}")
            raise

    def test_1_data_loading(self):
        """Test data loading functionality"""
        print("\nTest 1: Data Loading")
        try:
            # Test file existence
            self.assertTrue(os.path.exists('data/test_data.csv'))
            
            # Load with explicit dtypes
            df = pd.read_csv('data/test_data.csv', dtype={
                'episode_id': 'string',
                'name': 'string',
                'duration_ms': 'int64',
                'release_date': 'string',
                'description': 'string',
                'explicit': 'bool',
                'language': 'string'
            })
            
            self.assertEqual(len(df), 3)
            print("Data loading test passed")
            
        except Exception as e:
            print(f"Error in data loading test: {str(e)}")
            print(f"Error type: {type(e)}")
            raise

    def test_2_data_processing(self):
        """Test basic data processing"""
        print("\nTest 2: Data Processing")
        try:
            # Convert duration to minutes using float64
            duration_minutes = self.test_data['duration_ms'].astype('float64') / (1000 * 60)
            expected_minutes = np.array([30, 45, 60], dtype='float64')
            
            np.testing.assert_array_almost_equal(duration_minutes.to_numpy(), expected_minutes)
            print("Data processing test passed")
            
        except Exception as e:
            print(f"Error in data processing test: {str(e)}")
            print(f"Error type: {type(e)}")
            raise

    def test_3_basic_calculations(self):
        """Test basic calculations"""
        print("\nTest 3: Basic Calculations")
        try:
            # Calculate average duration using float64
            avg_duration = (self.test_data['duration_ms'].astype('float64') / (1000 * 60)).mean()
            self.assertAlmostEqual(avg_duration, 45.0)
            print("Basic calculations test passed")
            
        except Exception as e:
            print(f"Error in calculations test: {str(e)}")
            print(f"Error type: {type(e)}")
            raise

    def test_4_data_validation(self):
        """Test data validation"""
        print("\nTest 4: Data Validation")
        try:
            # Test data types using dtype property
            self.assertEqual(self.test_data['episode_id'].dtype, 'string')
            self.assertEqual(self.test_data['duration_ms'].dtype, 'int64')
            print("Data validation test passed")
            
        except Exception as e:
            print(f"Error in validation test: {str(e)}")
            print(f"Error type: {type(e)}")
            raise

    def tearDown(self):
        """Clean up test files"""
        try:
            if os.path.exists('data/test_data.csv'):
                os.remove('data/test_data.csv')
            print("Test cleanup complete")
            
        except Exception as e:
            print(f"Error in cleanup: {str(e)}")
            print(f"Error type: {type(e)}")

if __name__ == '__main__':
    # Print pandas and numpy versions for debugging
    print(f"Pandas version: {pd.__version__}")
    print(f"Numpy version: {np.__version__}")
    
    unittest.main(verbosity=2)