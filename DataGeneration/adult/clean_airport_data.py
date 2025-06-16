

# Add this method to your AdultDatasetCleaner class
def fix_coordinate_data(self):
    """Fix obviously wrong coordinate values"""
    # Fix longitude values that are clearly wrong (missing decimal)
    mask = self.df_cleaned['longitude_deg'].abs() > 1000
    if mask.any():
        print(f"Fixing {mask.sum()} longitude values that appear to be missing decimals")
        self.df_cleaned.loc[mask, 'longitude_deg'] = self.df_cleaned.loc[mask, 'longitude_deg'] / 1000
    
    # Similar fix for latitude if needed
    mask = self.df_cleaned['latitude_deg'].abs() > 90
    if mask.any():
        print(f"Fixing {mask.sum()} latitude values that appear to be missing decimals")  
        self.df_cleaned.loc[mask, 'latitude_deg'] = self.df_cleaned.loc[mask, 'latitude_deg'] / 100

# Call this method in your process() method after clean_data()



