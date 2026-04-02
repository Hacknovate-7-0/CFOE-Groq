"""
Visualization module for carbon footprint data
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


class Visualizer:
    """Create visualizations for carbon footprint analysis"""
    
    def __init__(self):
        sns.set_style("whitegrid")
        self.colors = sns.color_palette("husl", 8)
    
    def plot_emissions(self, results):
        """Plot emission results"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Pie chart
        sectors = list(results['by_sector'].keys())
        values = list(results['by_sector'].values())
        axes[0].pie(values, labels=sectors, autopct='%1.1f%%', colors=self.colors)
        axes[0].set_title('Emissions by Sector')
        
        # Bar chart
        axes[1].bar(sectors, values, color=self.colors)
        axes[1].set_xlabel('Sector')
        axes[1].set_ylabel('Emissions (tons CO2)')
        axes[1].set_title('Total Emissions by Sector')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('emissions_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_trends(self, data):
        """Plot emission trends over time"""
        plt.figure(figsize=(12, 6))
        for sector in data['sector'].unique():
            sector_data = data[data['sector'] == sector]
            plt.plot(sector_data['month'], sector_data['emissions'], marker='o', label=sector)
        
        plt.xlabel('Month')
        plt.ylabel('Emissions (tons CO2)')
        plt.title('Emission Trends by Sector')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('emission_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
