"""
Data processing module for carbon footprint analysis
"""

import pandas as pd
import numpy as np


class DataProcessor:
    """Handles data loading and preprocessing"""
    
    def __init__(self):
        self.data = None
    
    def load_data(self, filepath=None):
        """Load data from file or generate sample data"""
        if filepath:
            self.data = pd.read_csv(filepath)
        else:
            self.data = self._generate_sample_data()
        return self.data
    
    def _generate_sample_data(self):
        """Generate sample carbon emission data"""
        np.random.seed(42)
        data = {
            'sector': ['Transport', 'Energy', 'Industry', 'Agriculture', 'Residential'] * 12,
            'month': np.repeat(range(1, 13), 5),
            'emissions': np.random.uniform(100, 1000, 60),
            'activity': np.random.uniform(50, 500, 60)
        }
        return pd.DataFrame(data)
    
    def clean_data(self, data):
        """Clean and preprocess data"""
        data = data.dropna()
        data = data[data['emissions'] > 0]
        return data
    
    def aggregate_by_sector(self, data):
        """Aggregate emissions by sector"""
        return data.groupby('sector')['emissions'].sum().reset_index()
