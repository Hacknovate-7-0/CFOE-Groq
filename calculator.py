"""
Carbon footprint calculation module
"""

import pandas as pd
import numpy as np


class CarbonCalculator:
    """Calculate carbon footprints from activity data"""
    
    EMISSION_FACTORS = {
        'Transport': 0.21,
        'Energy': 0.45,
        'Industry': 0.35,
        'Agriculture': 0.28,
        'Residential': 0.18
    }
    
    def calculate(self, data):
        """Calculate total carbon footprint"""
        total = data['emissions'].sum()
        by_sector = data.groupby('sector')['emissions'].sum().to_dict()
        
        return {
            'total': total,
            'by_sector': by_sector,
            'data': data
        }
    
    def calculate_per_capita(self, total_emissions, population):
        """Calculate per capita emissions"""
        return total_emissions / population
    
    def apply_emission_factors(self, activity_data, sector):
        """Apply emission factors to activity data"""
        factor = self.EMISSION_FACTORS.get(sector, 0.25)
        return activity_data * factor
