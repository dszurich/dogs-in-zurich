# Streamlit live coding script
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
import time
import asyncio

# Load Data
df = pd.read_csv("https://drive.google.com/uc?export=download&id=1PAoIbp1cZrthkuqLSNGcPl_fkkr_YJEK")

# Load geojson data
with urlopen('https://drive.google.com/uc?export=download&id=1jS2OxyS7alvJjMYaLH8GGFWcTcjkj37z') as response:
    counties = json.load(response)

# Group data by district and count the number of dog owners
district_counts = df.groupby('STADTKREIS')['HALTER_ID'].count().reset_index(name='count')

# Title for the app
st.title("Dogs in Zurich Stats")
st.text('Updated 10 Sept 2024 7.00 pm')

# Create the choropleth map using Plotly
fig = px.choropleth_mapbox(
    district_counts,
    geojson=counties,
    locations='STADTKREIS',
    featureidkey="properties.name",  # Ensure this matches your GeoJSON file's property for district names
    color='count',
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=11,
    center={"lat": 47.3769, "lon": 8.5417},  # Centered on Zurich
    opacity=0.5,
    labels={'count': 'Dog Owners'}
)

# Remove extra margins around the map
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Display the map in Streamlit
st.plotly_chart(fig)

unique_owners = df['HALTER_ID'].nunique()

# Count male and female owners based on 'GESCHLECHT' column
male_owners = df[df['GESCHLECHT'] == 'm']['HALTER_ID'].nunique()
female_owners = df[df['GESCHLECHT'] == 'w']['HALTER_ID'].nunique()


# Placeholder to display the metrics
placeholder1 = st.empty()  # Number of dogs

# Create columns for owners, male, and female
col1, col2, col3 = st.columns(3)
placeholder2 = col1.empty()  # Total owners
placeholder_male = col2.empty()  # Male owners
placeholder_female = col3.empty()  # Female owners

# Starting numbers as half of the total
start_dogs = len(df) // 2
start_owners = unique_owners // 2
start_male_owners = male_owners // 2
start_female_owners = female_owners // 2

# Final numbers for each
total_dogs = len(df)
total_owners = unique_owners

# Async function to increment the number of dogs
async def increment_dogs(placeholder, start, end):
    for i in range(start, end + 1):  # Increment by 1
        placeholder.metric("Number of Dogs", i)  # No delta, just the number
        await asyncio.sleep(0.000001)  # Minimal sleep to ensure fast execution

# Async function to increment the number of owners
async def increment_owners(placeholder, start, end, placeholder_male, male_start, male_end, placeholder_female, female_start, female_end):
    male_count = male_start
    female_count = female_start

    for i in range(start, end + 1):  # Increment total owners
        placeholder.metric("Number of Owners", i)  # No delta, just the number
        
        # Increment male owners only if it hasn't reached the total male owners
        if male_count <= male_end:
            placeholder_male.metric("Male Owners", male_count)  # No delta, just the number
            male_count += 1
        
        # Increment female owners only if it hasn't reached the total female owners
        if female_count <= female_end:
            placeholder_female.metric("Female Owners", female_count)  # No delta, just the number
            female_count += 1

        await asyncio.sleep(0.000001)

# Main async function to run both tasks concurrently
async def main():
    task1 = asyncio.create_task(increment_dogs(placeholder1, start_dogs, total_dogs))
    task2 = asyncio.create_task(increment_owners(placeholder2, start_owners, total_owners, placeholder_male, start_male_owners, male_owners, placeholder_female, start_female_owners, female_owners))
    
    # Wait for both tasks to finish
    await asyncio.gather(task1, task2)

# Run the async main function within the Streamlit app
asyncio.run(main())

st.header("What breeds are popular in each District")

# Group data by district and breed, then count the occurrences
breed_counts = df.groupby(['STADTKREIS', 'RASSE1'])['HALTER_ID'].count().reset_index(name='count')

# Find the top 10 breeds
top_10_breeds = df['RASSE1'].value_counts().nlargest(10).index

# Filter the data to include only the top 10 breeds
breed_counts_top10 = breed_counts[breed_counts['RASSE1'].isin(top_10_breeds)]

# Create a stacked bar chart using Plotly
fig = px.bar(
    breed_counts_top10,
    x='STADTKREIS',
    y='count',
    color='RASSE1',
    # title='Dogs in Each District by Breed (Top 10 Breeds)',
    barmode='stack'
)

# Display the chart in Streamlit
st.plotly_chart(fig)

st.header("Find Your Pets")


# Dropdown for age range with "All" option
age_range = st.selectbox("Select Age Range", options=["All"] + list(df['ALTER'].unique()))

# Dropdown for district with "All" option
district = st.selectbox("Select District (STADTKREIS)", options=["All"] + list(df['STADTKREIS'].unique()))

# Dropdown for dog color with "All" option
dog_color = st.multiselect("Select Dog Color", options=["All"] + list(df['HUNDEFARBE'].unique()), default=["All"])

# Filter the data based on user selection
filtered_df = df.copy()

# Apply filters based on the dropdown selections
if age_range != "All":
    filtered_df = filtered_df[filtered_df['ALTER'] == age_range]
if district != "All":
    filtered_df = filtered_df[filtered_df['STADTKREIS'] == district]
if "All" not in dog_color:
    filtered_df = filtered_df[filtered_df['HUNDEFARBE'].isin(dog_color)]

# Group by breed and get the top 10 breeds
top_breeds = filtered_df['RASSE1'].value_counts().nlargest(10).reset_index()
top_breeds.columns = ['RASSE1', 'count']

# Create the bar chart
fig = px.bar(top_breeds, x='RASSE1', y='count', title='Top 10 Dog Breeds')

# Show the bar chart in Streamlit
st.plotly_chart(fig)