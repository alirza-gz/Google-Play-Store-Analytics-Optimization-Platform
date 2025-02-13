import pandas as pd
from sqlalchemy import create_engine

# ------------------------------------------------------------------------------
# 1. Create a SQLAlchemy engine to connect to the PostgreSQL database.
# Replace 'username', 'password', 'localhost', '5432' and 'googleplaystore'
# with your PostgreSQL credentials and database details.
# ------------------------------------------------------------------------------
engine = create_engine('postgresql://postgres:Alireza1679@127.0.0.1:5432/GooglePlayData')

# ------------------------------------------------------------------------------
# 2. Load the cleaned CSV file into a Pandas DataFrame.
# ------------------------------------------------------------------------------
df = pd.read_csv('cleaned_googleplaystore.csv')

# ------------------------------------------------------------------------------
# 3. Convert date/time columns to datetime objects.
# ------------------------------------------------------------------------------
df['Released'] = pd.to_datetime(df['Released'], errors='coerce')
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df['Scraped Time'] = pd.to_datetime(df['Scraped Time'], errors='coerce')

# ------------------------------------------------------------------------------
# 4. Insert data into the 'categories' table.
#
#    The 'categories' table contains only the 'category' column.
# ------------------------------------------------------------------------------
categories_df = df[['Category']].drop_duplicates().rename(columns={'Category': 'category'})
categories_df.to_sql('categories', engine, if_exists='append', index=False)
print("Categories inserted successfully.")

# ------------------------------------------------------------------------------
# 5. Insert data into the 'developers' table.
#
#    We extract the relevant columns and drop duplicates based on 'developer_id'
#    to avoid unique constraint violations.
# ------------------------------------------------------------------------------
developers_df = df[['Developer Id', 'Developer Website', 'Developer Email']].rename(
    columns={
        'Developer Id': 'developer_id',
        'Developer Website': 'developer_website',
        'Developer Email': 'developer_email'
    }
)
# Remove duplicate developers based on the 'developer_id' column
developers_df = developers_df.drop_duplicates(subset=['developer_id'])
developers_df.to_sql('developers', engine, if_exists='append', index=False)
print("Developers inserted successfully.")

# ------------------------------------------------------------------------------
# 6. Insert data into the 'applications' table.
#
#    We select and rename columns to match the schema of the applications table.
# ------------------------------------------------------------------------------
applications_df = df[[
    'App Id', 'App Name', 'Category', 'Rating', 'Rating Count', 'Installs',
    'Minimum Installs', 'Maximum Installs', 'Free', 'Price', 'Currency', 'Size',
    'Minimum Android', 'Developer Id', 'Released', 'Last Updated', 'Content Rating',
    'Privacy Policy', 'Ad Supported', 'In App Purchases', 'Editors Choice', 'Scraped Time'
]].rename(columns={
    'App Id': 'app_id',
    'App Name': 'app_name',
    'Category': 'category',
    'Rating': 'rating',
    'Rating Count': 'rating_count',
    'Installs': 'installs',
    'Minimum Installs': 'minimum_installs',
    'Maximum Installs': 'maximum_installs',
    'Free': 'free',
    'Price': 'price',
    'Currency': 'currency',
    'Size': 'size',
    'Minimum Android': 'minimum_android',
    'Developer Id': 'developer_id',
    'Released': 'released',
    'Last Updated': 'last_updated',
    'Content Rating': 'content_rating',
    'Privacy Policy': 'privacy_policy',
    'Ad Supported': 'ad_supported',
    'In App Purchases': 'in_app_purchases',
    'Editors Choice': 'editors_choice',
    'Scraped Time': 'scraped_time'
})
applications_df.to_sql('applications', engine, if_exists='append', index=False)
print("Applications inserted successfully.")
