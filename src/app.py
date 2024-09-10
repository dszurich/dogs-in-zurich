
# Streamlit live coding script
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
from adjustText import adjust_text #added
#conda install 

st.text('Updated 10 Sept 2024 4.14 pm')

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

# First some MPG Data Exploration
mpg_df_raw = load_data(path="./data/raw/mpg.csv")
mpg_df = deepcopy(mpg_df_raw)
mpg_data = mpg_df

# Title of the dashboard
st.title("Highway Fuel Efficiency")

# Checkbox to show/hide the dataframe
if st.checkbox("Show dataframe"):
    st.write(mpg_data.head())

# Selection options
years = mpg_data['year'].unique().tolist()
years.sort()
years.insert(0, "All")

classes = mpg_data['class'].unique().tolist()
classes.sort()
classes.insert(0, "All")

# Radio button to choose between Highway MPG or City MPG
fuel_efficiency_type = st.radio("Choose Fuel Efficiency Type:", ("Highway MPG", "City MPG"))

# Depending on the choice, show the corresponding slider
if fuel_efficiency_type == "Highway MPG":
    hwy_min, hwy_max = int(mpg_data['hwy'].min()), int(mpg_data['hwy'].max())
    hwy_range = st.slider("Select Highway MPG range", min_value=hwy_min, max_value=hwy_max, value=(hwy_min, hwy_max))
    filtered_data = mpg_data[(mpg_data['hwy'] >= hwy_range[0]) & (mpg_data['hwy'] <= hwy_range[1])]
else:
    cty_min, cty_max = int(mpg_data['cty'].min()), int(mpg_data['cty'].max())
    cty_range = st.slider("Select City MPG range", min_value=cty_min, max_value=cty_max, value=(cty_min, cty_max))
    filtered_data = mpg_data[(mpg_data['cty'] >= cty_range[0]) & (mpg_data['cty'] <= cty_range[1])]

# Year selection
selected_year = st.selectbox("Select year", years)

# Class selection
selected_class = st.selectbox("Select class", classes)

# Show class means option
show_class_means = st.radio("Show class means", ["No", "Yes"])

# Filter the data further based on year and class
if selected_year != "All":
    filtered_data = filtered_data[filtered_data['year'] == int(selected_year)]

if selected_class != "All":
    filtered_data = filtered_data[filtered_data['class'] == selected_class]

# Function to calculate class means and adjust text positions
def plot_class_means(ax, data):
    numeric_columns = ['displ', 'hwy' if fuel_efficiency_type == "Highway MPG" else 'cty']  # Numeric columns for calculation
    means = data.groupby('class')[numeric_columns].mean()  # Compute mean only for numeric columns
    ax.scatter(means['displ'], means['hwy' if fuel_efficiency_type == "Highway MPG" else 'cty'], color='red', label='Class Mean', s=100, zorder=5)
    
    # List to hold text objects for adjustment
    texts = []
    for i, row in means.iterrows():
        label = row.name
        x = row['displ']
        y = row['hwy' if fuel_efficiency_type == "Highway MPG" else 'cty']
        texts.append(ax.text(x, y, label, color='red'))

    # Adjust text positions to avoid overlap
    adjust_text(texts, arrowprops=dict(arrowstyle='->', color='gray'))

# Radio button for graph type selection
graph_type = st.radio("Choose graph type", ["Matplotlib", "Plotly"])

# Plot with Matplotlib
if graph_type == "Matplotlib":
    fig, ax = plt.subplots()
    ax.scatter(filtered_data['displ'], filtered_data['hwy'] if fuel_efficiency_type == "Highway MPG" else filtered_data['cty'], alpha=0.7)
    ax.set_xlabel("Engine Displacement (displ)")
    ax.set_ylabel("Fuel Efficiency (hwy)" if fuel_efficiency_type == "Highway MPG" else "Fuel Efficiency (cty)")
    ax.set_title("Fuel Efficiency vs. Engine Displacement")

    if show_class_means == "Yes":
        plot_class_means(ax, mpg_data)

    st.pyplot(fig)

# Plot with Plotly
else:
    fig = px.scatter(filtered_data, x='displ', y='hwy' if fuel_efficiency_type == "Highway MPG" else 'cty',
                     labels={"displ": "Engine Displacement (displ)", "hwy": "Fuel Efficiency (hwy)" if fuel_efficiency_type == "Highway MPG" else "Fuel Efficiency (cty)"},
                     title="Fuel Efficiency vs. Engine Displacement")

    if show_class_means == "Yes":
        means = mpg_data.groupby('class')[['displ', 'hwy' if fuel_efficiency_type == "Highway MPG" else 'cty']].mean().reset_index()
        fig.add_scatter(x=means['displ'], y=means['hwy' if fuel_efficiency_type == "Highway MPG" else 'cty'], mode='markers+text', text=means['class'],
                        textposition='top right',  # Position the text
                        marker=dict(color='red', size=10), name='Class Mean')

    fig.update_layout(
        xaxis_title="Engine Displacement (L)",
        yaxis_title="Fuel Efficiency (MPG)" if fuel_efficiency_type == "Highway MPG" else "Fuel Efficiency (cty)",
        title="Fuel Efficiency vs. Engine Displacement",
        title_x=0.5  # Center the title
    )

    st.plotly_chart(fig)