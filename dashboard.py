import time
import datetime
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

# Set Streamlit page configuration
st.set_page_config(page_title="Google Play Data Dashboard", layout="wide")

# ------------------------------------------------------------------------------
# Function to load data from PostgreSQL with caching
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Define PostgreSQL connection parameters
    host = '127.0.0.1'
    dbname = 'GooglePlayData'
    user = 'postgres'
    password = 'Alireza1679'

    # Connection string for PostgreSQL
    connection_str = f'postgresql+psycopg2://{user}:{password}@{host}/{dbname}'

    # Create a SQLAlchemy engine
    engine = create_engine(connection_str)

    # SQL Query with aliases for clarity
    query = """
    SELECT
        a.app_id,
        a.app_name,
        a.category,
        a.rating,
        a.rating_count,
        a.installs,
        a.free,
        a.price,
        a.currency,
        a.size,
        a.minimum_installs,
        a.maximum_installs,
        a.minimum_android,
        a.developer_id,
        a.released AS release_date,
        a.last_updated,
        a.content_rating,
        a.privacy_policy AS privacy_policy_url,
        a.ad_supported,
        a.in_app_purchases,
        a.editors_choice,
        a.scraped_time,
        c.category AS category_name,
        d.developer_email
    FROM applications a
    JOIN categories c ON a.category = c.category
    JOIN developers d ON a.developer_id = d.developer_id;
    """
    df = pd.read_sql(query, engine)
    return df

# ------------------------------------------------------------------------------
# Load data from database and measure query execution time
# ------------------------------------------------------------------------------
load_start = time.time()
df = load_data()
load_time = time.time() - load_start
st.sidebar.write(f"Data loaded in {load_time:.2f} seconds")

# ------------------------------------------------------------------------------
# Sidebar Filters - User input filters for the dashboard
# ------------------------------------------------------------------------------
st.sidebar.header("Filter Options")

# Filter by Category
category_filter = st.sidebar.multiselect(
    "Select Categories",
    options=df["category"].unique(),
    default=df["category"].unique()
)

# Filter by Rating Range
rating_filter = st.sidebar.slider(
    "Select Rating Range",
    min_value=0.0,
    max_value=5.0,
    value=(0.0, 5.0)
)

# Filter by Price (Free or Paid)
price_filter = st.sidebar.selectbox(
    "Select Price Range",
    options=["Free", "Paid"]
)

# Filter by Content Rating
content_rating_filter = st.sidebar.multiselect(
    "Select Content Ratings",
    options=df["content_rating"].unique(),
    default=df["content_rating"].unique()
)

# Advanced Search: Search for App Name
search_term = st.sidebar.text_input("Search for App Name", "")

# ------------------------------------------------------------------------------
# Filter the DataFrame based on selected filters
# ------------------------------------------------------------------------------
filtered_df = df[
    (df["category"].isin(category_filter)) &
    (df["rating"] >= rating_filter[0]) &
    (df["rating"] <= rating_filter[1]) &
    (df["free"] == (price_filter == "Free")) &
    (df["content_rating"].isin(content_rating_filter))
]

# Apply advanced search filter if a search term is provided
if search_term:
    filtered_df = filtered_df[filtered_df["app_name"].str.contains(search_term, case=False, na=False)]

st.write(f"Showing {len(filtered_df)} apps after filtering")
# Limit displayed rows to avoid high memory usage
st.dataframe(filtered_df.head(3000))

# ------------------------------------------------------------------------------
# Data Processing: Convert date columns to datetime and extract year
# ------------------------------------------------------------------------------
filtered_df["release_date"] = pd.to_datetime(filtered_df["release_date"], errors="coerce")
filtered_df["last_updated"] = pd.to_datetime(filtered_df["last_updated"], errors="coerce")
filtered_df["release_year"] = filtered_df["release_date"].dt.year
filtered_df["updated_year"] = filtered_df["last_updated"].dt.year

# ------------------------------------------------------------------------------
# Chart 1: App Release Trend Over the Years (for a selected category)
# ------------------------------------------------------------------------------
st.subheader("App Release Trend Over the Years")
selected_category_for_trend = st.selectbox(
    "Select a Category for Release Trend",
    options=df["category"].unique(),
    key="release_trend"
)
# Measure query execution time for release trend groupby operation
release_start = time.time()
release_trend = filtered_df[filtered_df["category"] == selected_category_for_trend] \
    .groupby("release_year").size().reset_index(name="App Count")
release_time = time.time() - release_start
st.write(f"Release Trend query executed in {release_time:.2f} seconds")
fig_release = px.line(release_trend, x="release_year", y="App Count",
                      title=f"Release Trend for {selected_category_for_trend}")
st.plotly_chart(fig_release)

# ------------------------------------------------------------------------------
# Chart 2: Last Updated Trend Over the Years (for a selected category)
# ------------------------------------------------------------------------------
st.subheader("Last Updated Trend Over the Years")
selected_category_for_update = st.selectbox(
    "Select a Category for Last Updated Trend",
    options=df["category"].unique(),
    key="update_trend"
)
update_start = time.time()
update_trend = filtered_df[filtered_df["category"] == selected_category_for_update] \
    .groupby("updated_year").size().reset_index(name="App Count")
update_time = time.time() - update_start
st.write(f"Last Updated query executed in {update_time:.2f} seconds")
fig_update = px.line(update_trend, x="updated_year", y="App Count",
                     title=f"Last Updated Trend for {selected_category_for_update}")
st.plotly_chart(fig_update)

# ------------------------------------------------------------------------------
# Chart 3: Average Rating per Category
# ------------------------------------------------------------------------------
st.subheader("Average Rating per Category")
avg_start = time.time()
avg_rating = filtered_df.groupby("category")["rating"].mean().reset_index()
avg_time = time.time() - avg_start
st.write(f"Average Rating query executed in {avg_time:.2f} seconds")
fig_avg_rating = px.bar(avg_rating, x="category", y="rating",
                        title="Average Rating by Category")
st.plotly_chart(fig_avg_rating)

# ------------------------------------------------------------------------------
# Chart 4: Price Distribution of Paid Apps (Improved)
# ------------------------------------------------------------------------------
st.subheader("Price Distribution of Paid Apps")
# Filter out free apps to focus on price distribution among paid apps
paid_apps = filtered_df[filtered_df["price"] > 0]

if not paid_apps.empty:
    price_start = time.time()
    # Create histogram for price distribution using 50 bins
    fig_price = px.histogram(
        paid_apps,
        x="price",
        nbins=50,
        title="Price Distribution of Paid Apps"
    )
    price_time = time.time() - price_start
    st.write(f"Price Distribution query executed in {price_time:.2f} seconds")
    # Update layout for better visualization
    fig_price.update_layout(
        xaxis_title="Price (USD)",
        yaxis_title="Number of Apps",
        bargap=0.1
    )
    st.plotly_chart(fig_price)
else:
    st.write("No paid apps available in the current filter.")

# ------------------------------------------------------------------------------
# Chart 5: Total Installs by Category
# ------------------------------------------------------------------------------
st.subheader("Total Installs by Category")
installs_start = time.time()
installs_dist = filtered_df.groupby("category")["installs"].sum().reset_index()
installs_time = time.time() - installs_start
st.write(f"Total Installs query executed in {installs_time:.2f} seconds")
fig_installs = px.bar(installs_dist, x="category", y="installs",
                      title="Total Installs by Category")
st.plotly_chart(fig_installs)

# ------------------------------------------------------------------------------
# CRUD Operations Section via API calls for Applications, Developers, and Categories
# ------------------------------------------------------------------------------
st.subheader("CRUD Operations (Using API)")
api_base_url = "http://127.0.0.1:8000"
crud_option = st.selectbox("Select CRUD Operation",
                           options=["Create Application", "Update Application", "Delete Application", "Get Application",
                                    "Create Developer", "Update Developer", "Delete Developer", "Get Developer",
                                    "Create Category", "Update Category", "Delete Category", "Get Category"])

# -------------------------------
# CRUD for Application
# -------------------------------
if crud_option == "Create Application":
    st.markdown("### Create a New Application")
    with st.form("create_app_form"):
        app_id = st.text_input("App ID")
        app_name = st.text_input("App Name")
        category = st.text_input("Category")
        rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=0.0)
        rating_count = st.number_input("Rating Count", min_value=0, value=0, step=1)
        installs = st.number_input("Installs", min_value=0, value=0, step=1)
        free = st.selectbox("Free", options=["True", "False"]) == "True"
        price = st.number_input("Price", min_value=0.0, value=0.0)
        currency = st.text_input("Currency", value="USD")
        size = st.number_input("Size (MB)", min_value=0.0, value=0.0)
        minimum_installs = st.number_input("Minimum Installs", min_value=0, value=0, step=1)
        maximum_installs = st.number_input("Maximum Installs", min_value=0, value=0, step=1)
        minimum_android = st.text_input("Minimum Android")
        developer_id = st.text_input("Developer ID")
        released = st.date_input("Released")
        last_updated = st.date_input("Last Updated")
        content_rating = st.text_input("Content Rating")
        privacy_policy_url = st.text_input("Privacy Policy URL")
        ad_supported = st.selectbox("Ad Supported", options=["True", "False"]) == "True"
        in_app_purchases = st.selectbox("In-App Purchases", options=["True", "False"]) == "True"
        editors_choice = st.selectbox("Editor's Choice", options=["True", "False"]) == "True"
        submitted = st.form_submit_button("Create Application")
    if submitted:
        payload = {
            "app_id": app_id,
            "app_name": app_name,
            "category": category,
            "rating": rating,
            "rating_count": rating_count,
            "installs": installs,
            "free": free,
            "price": price,
            "currency": currency,
            "size": size,
            "minimum_installs": minimum_installs,
            "maximum_installs": maximum_installs,
            "minimum_android": minimum_android,
            "developer_id": developer_id,
            "released": released.isoformat() if released else None,
            "last_updated": last_updated.isoformat() if last_updated else None,
            "content_rating": content_rating,
            "privacy_policy_url": privacy_policy_url,
            "ad_supported": ad_supported,
            "in_app_purchases": in_app_purchases,
            "editors_choice": editors_choice,
            "scraped_time": datetime.datetime.now().isoformat()
        }
        response = requests.post(f"{api_base_url}/applications/", json=payload)
        if response.status_code in (200, 201):
            st.success("Application created successfully!")
        else:
            st.error(f"Failed to create application: {response.text}")

elif crud_option == "Update Application":
    st.markdown("### Update an Existing Application")
    with st.form("update_app_form"):
        app_id = st.text_input("App ID to Update")
        st.markdown("Enter fields to update:")
        app_name = st.text_input("App Name")
        category = st.text_input("Category")
        rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=0.0)
        rating_count = st.number_input("Rating Count", min_value=0, value=0, step=1)
        installs = st.number_input("Installs", min_value=0, value=0, step=1)
        free_str = st.selectbox("Free", options=["", "True", "False"])
        price = st.number_input("Price", min_value=0.0, value=0.0)
        currency = st.text_input("Currency")
        size = st.number_input("Size (MB)", min_value=0.0, value=0.0)
        minimum_installs = st.number_input("Minimum Installs", min_value=0, value=0, step=1)
        maximum_installs = st.number_input("Maximum Installs", min_value=0, value=0, step=1)
        minimum_android = st.text_input("Minimum Android")
        developer_id = st.text_input("Developer ID")
        released = st.date_input("Released")
        last_updated = st.date_input("Last Updated")
        content_rating = st.text_input("Content Rating")
        privacy_policy_url = st.text_input("Privacy Policy URL")
        ad_supported_str = st.selectbox("Ad Supported", options=["", "True", "False"])
        in_app_purchases_str = st.selectbox("In-App Purchases", options=["", "True", "False"])
        editors_choice_str = st.selectbox("Editor's Choice", options=["", "True", "False"])
        submitted = st.form_submit_button("Update Application")
    if submitted:
        payload = {}
        if app_name: payload["app_name"] = app_name
        if category: payload["category"] = category
        payload["rating"] = rating
        payload["rating_count"] = rating_count
        payload["installs"] = installs
        if free_str: payload["free"] = (free_str == "True")
        payload["price"] = price
        if currency: payload["currency"] = currency
        payload["size"] = size
        payload["minimum_installs"] = minimum_installs
        payload["maximum_installs"] = maximum_installs
        if minimum_android: payload["minimum_android"] = minimum_android
        if developer_id: payload["developer_id"] = developer_id
        if released: payload["released"] = released.isoformat()
        if last_updated: payload["last_updated"] = last_updated.isoformat()
        if content_rating: payload["content_rating"] = content_rating
        if privacy_policy_url: payload["privacy_policy_url"] = privacy_policy_url
        if ad_supported_str: payload["ad_supported"] = (ad_supported_str == "True")
        if in_app_purchases_str: payload["in_app_purchases"] = (in_app_purchases_str == "True")
        if editors_choice_str: payload["editors_choice"] = (editors_choice_str == "True")
        response = requests.put(f"{api_base_url}/applications/{app_id}", json=payload)
        if response.status_code == 200:
            st.success("Application updated successfully!")
        else:
            st.error(f"Failed to update application: {response.text}")

elif crud_option == "Delete Application":
    st.markdown("### Delete an Application")
    with st.form("delete_app_form"):
        app_id = st.text_input("App ID to Delete")
        submitted = st.form_submit_button("Delete Application")
    if submitted:
        response = requests.delete(f"{api_base_url}/applications/{app_id}")
        if response.status_code == 200:
            st.success("Application deleted successfully!")
        else:
            st.error(f"Failed to delete application: {response.text}")

elif crud_option == "Get Application":
    st.markdown("### Get Application Details")
    with st.form("get_app_form"):
        app_id = st.text_input("App ID to Retrieve")
        submitted = st.form_submit_button("Get Application")
    if submitted:
        response = requests.get(f"{api_base_url}/applications/{app_id}")
        if response.status_code == 200:
            app_data = response.json()
            st.json(app_data)
        else:
            st.error(f"Failed to retrieve application: {response.text}")

# -------------------------------
# CRUD for Developer
# -------------------------------
elif crud_option == "Create Developer":
    st.markdown("### Create a New Developer")
    with st.form("create_dev_form"):
        developer_id = st.text_input("Developer ID")
        developer_website = st.text_input("Developer Website")
        developer_email = st.text_input("Developer Email")
        submitted = st.form_submit_button("Create Developer")
    if submitted:
        payload = {
            "developer_id": developer_id,
            "developer_website": developer_website,
            "developer_email": developer_email
        }
        response = requests.post(f"{api_base_url}/developers/", json=payload)
        if response.status_code in (200, 201):
            st.success("Developer created successfully!")
        else:
            st.error(f"Failed to create developer: {response.text}")

elif crud_option == "Update Developer":
    st.markdown("### Update an Existing Developer")
    with st.form("update_dev_form"):
        developer_id = st.text_input("Developer ID to Update")
        st.markdown("Enter fields to update:")
        developer_website = st.text_input("Developer Website")
        developer_email = st.text_input("Developer Email")
        submitted = st.form_submit_button("Update Developer")
    if submitted:
        payload = {}
        if developer_website: payload["developer_website"] = developer_website
        if developer_email: payload["developer_email"] = developer_email
        response = requests.put(f"{api_base_url}/developers/{developer_id}", json=payload)
        if response.status_code == 200:
            st.success("Developer updated successfully!")
        else:
            st.error(f"Failed to update developer: {response.text}")

elif crud_option == "Delete Developer":
    st.markdown("### Delete a Developer")
    with st.form("delete_dev_form"):
        developer_id = st.text_input("Developer ID to Delete")
        submitted = st.form_submit_button("Delete Developer")
    if submitted:
        response = requests.delete(f"{api_base_url}/developers/{developer_id}")
        if response.status_code == 200:
            st.success("Developer deleted successfully!")
        else:
            st.error(f"Failed to delete developer: {response.text}")

elif crud_option == "Get Developer":
    st.markdown("### Get Developer Details")
    with st.form("get_dev_form"):
        developer_id = st.text_input("Developer ID to Retrieve")
        submitted = st.form_submit_button("Get Developer")
    if submitted:
        response = requests.get(f"{api_base_url}/developers/{developer_id}")
        if response.status_code == 200:
            dev_data = response.json()
            st.json(dev_data)
        else:
            st.error(f"Failed to retrieve developer: {response.text}")

# -------------------------------
# CRUD for Category
# -------------------------------
elif crud_option == "Create Category":
    st.markdown("### Create a New Category")
    with st.form("create_cat_form"):
        category = st.text_input("Category")
        submitted = st.form_submit_button("Create Category")
    if submitted:
        payload = {"category": category}
        response = requests.post(f"{api_base_url}/categories/", json=payload)
        if response.status_code in (200, 201):
            st.success("Category created successfully!")
        else:
            st.error(f"Failed to create category: {response.text}")

elif crud_option == "Update Category":
    st.markdown("### Update an Existing Category")
    with st.form("update_cat_form"):
        category_id = st.text_input("Category to Update")
        new_category = st.text_input("New Category Value (if updating)")
        submitted = st.form_submit_button("Update Category")
    if submitted:
        payload = {}
        if new_category:
            payload["category"] = new_category
        response = requests.put(f"{api_base_url}/categories/{category_id}", json=payload)
        if response.status_code == 200:
            st.success("Category updated successfully!")
        else:
            st.error(f"Failed to update category: {response.text}")

elif crud_option == "Delete Category":
    st.markdown("### Delete a Category")
    with st.form("delete_cat_form"):
        category_id = st.text_input("Category to Delete")
        submitted = st.form_submit_button("Delete Category")
    if submitted:
        response = requests.delete(f"{api_base_url}/categories/{category_id}")
        if response.status_code == 200:
            st.success("Category deleted successfully!")
        else:
            st.error(f"Failed to delete category: {response.text}")

elif crud_option == "Get Category":
    st.markdown("### Get Category Details")
    with st.form("get_cat_form"):
        category_id = st.text_input("Category to Retrieve")
        submitted = st.form_submit_button("Get Category")
    if submitted:
        response = requests.get(f"{api_base_url}/categories/{category_id}")
        if response.status_code == 200:
            cat_data = response.json()
            st.json(cat_data)
        else:
            st.error(f"Failed to retrieve category: {response.text}")