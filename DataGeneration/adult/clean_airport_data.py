
# dropping columns with >20% null values would mean that we need to change the ddl and insert query language.
#  For now I keep it on hold as this logic leads to the deletion of 7 columns.
# Everything is working fine with the current code.


import pandas as pd

import os, sys
# allow imports from project root if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class AirportDatasetCleaner:
    def __init__(self, input_file):
        self.input_file = input_file
        self.df = None
        self.df_cleaned = None

    def load_data(self):
        """Load data from the CSV file"""
        self.df = pd.read_csv(self.input_file)
        print("Dataset loaded successfully!")
        print(f"Shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        print("\nFirst few rows:")
        print(self.df.head())

    def clean_data(self):
        """Clean the dataset by removing rows with missing values"""
        print(f"\nBefore cleaning: {len(self.df)} rows")
        
        # Replace '?' with NaN
        self.df.replace('?', pd.NA, inplace=True)
        
        # Drop columns that have more than 90% null values
        null_percentages = (self.df.isnull().sum() / len(self.df)) * 100
        columns_to_drop = null_percentages[null_percentages > 20].index.tolist()
        
        if columns_to_drop:
            print(f"Dropping columns with >20% null values: {columns_to_drop}")
            for col in columns_to_drop:
                print(f"  {col}: {null_percentages[col]:.1f}% null")
            self.df = self.df.drop(columns=columns_to_drop)
        else:
            print("No columns have >20% null values")
        
        # Now drop rows with any remaining null values
        self.df_cleaned = self.df.dropna().reset_index(drop=True)
        print(f"After cleaning: {len(self.df_cleaned)} rows")
        print(f"Removed {len(self.df) - len(self.df_cleaned)} rows with missing values")


    def fix_coordinate_data(self):
        """Fix obviously wrong coordinate values"""
        # First, let's identify the correct column names for coordinates
        coordinate_columns = [col for col in self.df_cleaned.columns if 'lon' in col.lower() or 'lat' in col.lower()]
        print(f"\nFound coordinate columns: {coordinate_columns}")
        
        # Try to find longitude column
        longitude_col = None
        latitude_col = None
        
        for col in self.df_cleaned.columns:
            if 'lon' in col.lower():
                longitude_col = col
            if 'lat' in col.lower():
                latitude_col = col
        
        if longitude_col:
            print(f"Using longitude column: {longitude_col}")
            # Fix longitude values that are clearly wrong (missing decimal)
            mask = self.df_cleaned[longitude_col].abs() > 1000
            if mask.any():
                print(f"Fixing {mask.sum()} longitude values that appear to be missing decimals")
                self.df_cleaned.loc[mask, longitude_col] = self.df_cleaned.loc[mask, longitude_col] / 1000
        else:
            print("No longitude column found")
        
        if latitude_col:
            print(f"Using latitude column: {latitude_col}")
            # Similar fix for latitude if needed
            mask = self.df_cleaned[latitude_col].abs() > 90
            if mask.any():
                print(f"Fixing {mask.sum()} latitude values that appear to be missing decimals")  
                self.df_cleaned.loc[mask, latitude_col] = self.df_cleaned.loc[mask, latitude_col] / 100
        else:
            print("No latitude column found")

    def save_cleaned_data(self, output_file):
        """Save the cleaned data to a new CSV file"""
        self.df_cleaned.to_csv(output_file, index=False)
        print(f"\nCleaned data saved to: {output_file}")
        print(f"Final dataset shape: {self.df_cleaned.shape}")
    



# Add this method to your AdultDatasetCleaner class

if __name__ == "__main__":
    AirportDatasetCleaner = AirportDatasetCleaner(input_file='DataGeneration/adult/airport.csv')
    AirportDatasetCleaner.load_data()
    AirportDatasetCleaner.clean_data()
    AirportDatasetCleaner.fix_coordinate_data()
    AirportDatasetCleaner.save_cleaned_data(output_file='cleaned_airport.csv')
    




