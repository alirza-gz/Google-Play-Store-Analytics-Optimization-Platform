import pandas as pd
import numpy as np

# 1. Load the dataset from the CSV file
df = pd.read_csv('Google-Playstore.csv')

# Display the first 5 rows of the dataset
print("Initial Data:")
print(df.head())

# Display dataset information (number of rows, columns, data types, non-null counts)
print("\nDataset Info:")
print(df.info())

# 2. Drop duplicate records to ensure data integrity
df.drop_duplicates(inplace=True)
print("\nNumber of records after dropping duplicates:", df.shape[0])

# 3. Check for missing values in each column
print("\nMissing values per column:")
print(df.isnull().sum())

# 4. Drop rows with any missing values (this step might be adjusted as per your project needs)
df.dropna(inplace=True)
print("\nNumber of records after dropping rows with missing values:", df.shape[0])

# 5. Clean and standardize the 'Installs' column
# Remove commas and plus signs, then convert the column to integer
df['Installs'] = df['Installs'].str.replace('[+,]', '', regex=True).astype(int)
print("\nSample 'Installs' values after cleaning:")
print(df['Installs'].head())

# 6. Clean and standardize the 'Price' column
# Check if the 'Price' column is of type object (string). If so, remove the dollar sign.
# If it is already numeric (float), skip this cleaning step.
if isinstance(df['Price'].iloc[0], str):
    df['Price'] = df['Price'].str.replace('$', '', regex=True).astype(float)
else:
    print("\n'Price' column is already numeric. Skipping string cleaning for Price.")
print("\nSample 'Price' values after cleaning (if applicable):")
print(df['Price'].head())

# 7. Clean and standardize the 'Size' column
def convert_size(size):
    """
    Convert a size string to megabytes (MB).
    - If the size is "Varies with device", return NaN.
    - If the size ends with 'M', remove the 'M' and convert to float.
    - If the size ends with 'k', remove the 'k', convert to float, and convert kilobytes to megabytes.
    """
    if size == "Varies with device":
        return np.nan
    # Check if size ends with 'M'
    if size[-1] == 'M':
        try:
            return float(size[:-1])
        except:
            return np.nan
    # Check if size ends with 'k'
    if size[-1] == 'k':
        try:
            return float(size[:-1]) / 1024  # Convert kilobytes to megabytes (1 MB = 1024 kB)
        except:
            return np.nan
    return np.nan

# Apply the conversion function to the 'Size' column
df['Size'] = df['Size'].apply(convert_size)
print("\nSample 'Size' values after conversion:")
print(df['Size'].head())

# Replace NaN values in 'Size' with the median size
df['Size'].fillna(df['Size'].median(), inplace=True)

# 8. Validate the 'Rating' column by ensuring values are between 0 and 5
df = df[(df['Rating'] >= 0) & (df['Rating'] <= 5)]
print("\nNumber of records after filtering invalid ratings:", df.shape[0])

# 9. Display the final cleaned dataset and its summary statistics
print("\nCleaned Data Sample:")
print(df.head())
print("\nFinal Dataset Info:")
print(df.info())
print("\nDescriptive Statistics:")
print(df.describe())

# 10. Save the cleaned dataset to a new CSV file for future use
df.to_csv('cleaned_googleplaystore.csv', index=False)
print("\nCleaned dataset saved to 'cleaned_googleplaystore.csv'.")
