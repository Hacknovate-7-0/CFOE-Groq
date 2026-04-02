"""
Optimization module for carbon footprint reduction
"""

import numpy as np
import pandas as pd


class Optimizer:
    """Generate optimization recommendations"""
    
    REDUCTION_POTENTIAL = {
        'Transport': 0.25,
        'Energy': 0.35,
        'Industry': 0.20,
        'Agriculture': 0.15,
        'Residential': 0.30
    }
    
    def optimize(self, results):
        """Generate optimization recommendations"""
        recommendations = []
        total_potential = 0
        
        for sector, emissions in results['by_sector'].items():
            potential = self.REDUCTION_POTENTIAL.get(sector, 0.20)
            reduction = emissions * potential
            total_potential += reduction
            
            recommendations.append({
                'sector': sector,
                'current_emissions': emissions,
                'reduction_potential': reduction,
                'percentage': potential * 100
            })
        
        return {
            'recommendations': recommendations,
            'potential': (total_potential / results['total']) * 100,
            'total_reduction': total_potential
        }
    
    def prioritize_sectors(self, results):
        """Prioritize sectors for optimization"""
        sectors = []
        for sector, emissions in results['by_sector'].items():
            potential = self.REDUCTION_POTENTIAL.get(sector, 0.20)
            impact = emissions * potential
            sectors.append({'sector': sector, 'impact': impact})
        
        return sorted(sectors, key=lambda x: x['impact'], reverse=True)
