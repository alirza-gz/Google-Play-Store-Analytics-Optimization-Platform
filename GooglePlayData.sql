----------------------------------------------------------
-- Step 1: Create the database
----------------------------------------------------------
-- Run this command as a superuser or via your preferred DB management tool.
CREATE DATABASE GooglePlayData;

----------------------------------------------------------
-- Step 2: Connect to the newly created database
----------------------------------------------------------
-- (psql command to connect; if using another tool, connect accordingly)
\c GooglePlayData

----------------------------------------------------------
-- Step 3: Create the 'categories' table
-- This table contains only one column 'category', which stores the unique category names.
----------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category VARCHAR(100) PRIMARY KEY  -- Category name as primary key (unique)
);

----------------------------------------------------------
-- Step 4: Create the 'developers' table
----------------------------------------------------------
CREATE TABLE IF NOT EXISTS developers (
    developer_id VARCHAR(255) PRIMARY KEY,   -- Developer identifier (assumed unique)
    developer_website VARCHAR(255),          -- Developer website URL
    developer_email VARCHAR(255)             -- Developer email address
);

----------------------------------------------------------
-- Step 5: Create the 'applications' table
-- This table includes all columns from the dataset.
-- The 'category' column here is a foreign key referencing the categories table.
----------------------------------------------------------
CREATE TABLE IF NOT EXISTS applications (
    app_id VARCHAR(2000) PRIMARY KEY,           -- Application identifier
    app_name TEXT,            -- Application name
    category VARCHAR(100),            -- Category name (foreign key to categories.category)
    rating FLOAT,                       -- App rating (e.g., 4.5)
    rating_count BIGINT,                          -- Number of ratings
    installs BIGINT,                              -- Number of installs
    minimum_installs BIGINT,                      -- Minimum installs value
    maximum_installs BIGINT,                      -- Maximum installs value
    free BOOLEAN,                              -- Indicates if the app is free
    price FLOAT,                       -- App price (if not free)
    currency VARCHAR(50),                      -- Currency code (e.g., USD)
    size FLOAT,                        -- App size in MB
    minimum_android VARCHAR(50),               -- Minimum required Android version
    developer_id VARCHAR(255),        -- Developer identifier (foreign key to developers.developer_id)
    released DATE,                             -- Release date of the app
    last_updated DATE,                         -- Last updated date
    content_rating VARCHAR(50),                -- Content rating (e.g., "Everyone", "Teen")
    privacy_policy TEXT,               -- URL of the privacy policy
    ad_supported BOOLEAN,                      -- Indicates if the app is ad-supported
    in_app_purchases BOOLEAN,                  -- Indicates if the app offers in-app purchases
    editors_choice BOOLEAN,                    -- Indicates if the app is an editor's choice
    scraped_time TIMESTAMP,                    -- Time when the data was scraped
    CONSTRAINT fk_category FOREIGN KEY (category) REFERENCES categories(category),
    CONSTRAINT fk_developer FOREIGN KEY (developer_id) REFERENCES developers(developer_id)
);


----------------------------------------------------------
-- Step 6: Create indexes for optimized search queries
----------------------------------------------------------

----------------------------------------------------------------------
-- 1. Create an index on the "category" column in the "applications" table.
--    This index helps speed up queries that filter by category.
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_category
ON applications(category);

----------------------------------------------------------------------
-- 2. Create a composite index on the "category" and "free" columns.
--    This index is designed to speed up filtering of free or paid apps within a specific category.
--    The INCLUDE clause adds additional columns (rating, app_name, price, installs)
--    so that queries that use these columns can be fully satisfied by the index (covering index).
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_category_free
ON applications(category, free)
INCLUDE (rating, app_name, price, installs);

----------------------------------------------------------------------
-- 3. Create an index on the "rating" column.
--    This index accelerates queries that filter or perform range operations on the app ratings.
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_rating
ON applications(rating);

----------------------------------------------------------------------
-- 4. Create an index on the "content_rating" column.
--    This index speeds up filtering based on the app's content rating.
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_content_rating
ON applications(content_rating);

----------------------------------------------------------------------
-- 5. Create an index on the "app_name" column.
--    This index improves the performance of text-based searches on application names.
--    (For advanced text searches, consider using a GIN index with the pg_trgm extension.)
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_app_name
ON applications(app_name);

----------------------------------------------------------------------
-- 6. Create an index on the "released" column.
--    This index improves query performance for filtering and grouping apps by their release dates.
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_released
ON applications(released);

----------------------------------------------------------------------
-- 7. Create an index on the "last_updated" column.
--    This index speeds up queries that filter or group apps based on the last updated date.
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_last_updated
ON applications(last_updated);

----------------------------------------------------------------------
-- 8. Create an index on the "developer_id" column.
--    This index enhances the performance of join operations with the developers table.
----------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_applications_developer_id
ON applications(developer_id);