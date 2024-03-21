import pandas as pd
import numpy as np
import os
import sys
import streamlit as st
import base64

from geopy.distance import great_circle
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.metrics import davies_bouldin_score

# Set background

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True
        )

# Find Nearby

def find_nearby_coworks(campsite, coworks, max_distance_km):
    nearby_coworks = []
    for _, cowork in coworks.iterrows():
        dist = great_circle((campsite.latitude, campsite.longitude), (cowork.latitude, cowork.longitude)).kilometers
        if dist <= max_distance_km:
            nearby_coworks.append(cowork)
    return nearby_coworks

# Load the data

df_campsites = pd.read_csv("campsites_encoding.csv")
df_coworks = pd.read_csv("coworkings_encoding.csv")

# Reverse dictionaries for decoding

type = {0: 'City', 1: 'Town', 2: 'Village'}
luxury = {0: 'Campsite', 1: 'Glamping', 2: 'Camper'}
beach = {0: 'No', 1: 'Yes'}
wild = {0: 'No', 1: 'Yes'}


# Prepare data for model training

Xca = df_campsites

# Initialize and fit DBSCAN for campsites with results EPS: 30, Min_Samples: 9


dbscan_optimal_campsites = DBSCAN(eps=30, min_samples=9, metric='euclidean').fit(Xca)

# Assign cluster labels
df_campsites['cluster'] = dbscan_optimal_campsites.labels_


# Streamlit app
def main():

    # Page configuration
    st.set_page_config(
        page_title='My Jobcation Path',
        page_icon='🏕️',
        layout='wide'
    )
        
    # Add background image
    st.markdown(
        """
        <style>
        .reportview-container {
            background: url('landscape_back.png') no-repeat center center fixed;
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    add_bg_from_local("landscape_back2.png")

    custom_css ="""
     <style>
    /* Cambiar el color del texto dentro del formulario */
    .stTextInput, .stNumberInput, .stTextArea, .stSelectbox, .stMultiSelect {
        color: red !important;
        font-size: 20px !important;
    }
    /* Cambiar el color de fondo de las cajas de selección */
    .st-af, .st-c7 {
        background-color: transparent !important;
    }
    /* Cambiar el color y el tamaño del texto en los elementos */
    .st-title, .st-form, .st-slider {
        color: purple !important;
        font-size: 30px !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True) 
    st.title(":blue_car: MY JOBCATION PATH :blue_car:")
    st.markdown(custom_css, unsafe_allow_html=True) 
    st.markdown("Enter your preferences for your adventure.")
    
    # Divide Page in 2 columns:
    col1, col2 = st.columns(2)
    
    # User input form
    st.markdown(custom_css, unsafe_allow_html=True)
    with col1:
        with st.form(key='site_recommender_form'):
            user_type_input = st.selectbox("Do you want to be close to?", [""] + list(type.values()))  # Define 'type' values
            user_luxury_input = st.selectbox("Where do we spend the night?", [""] + list(luxury.values())) # Define 'luxury' values
            user_beach_input = st.selectbox("Do you want to stay near of a beach?", [""] + list(beach.values())) # Define 'beach' values
            user_wild_input = st.selectbox("Into the wild?", [""] + list(wild.values()))  # Define 'wild' values
            user_slider_input = st.slider("How far away do you need a workspace?(km)", 0, 60)
            user_rating_input = st.slider("Rate for this experience (1-5):", 1, 5, 1)
            submit_button = st.form_submit_button(label='Get my jobcation plan!')
    
        

        new_title = '<p style="color:Black; font-size: 24px; font-style: italic;">Home is not a place, it is something that you build.(Gaston de Bachelar)</p>'
        st.markdown(new_title, unsafe_allow_html=True)

    # Perform predictions and show the results when the form is submitted
    with col2:
        #st.markdown(custom_css, unsafe_allow_html=True)
        #new_title = '<p style="color:Grey; font-size: 16px; font-style: italic;">Home is not a place, it is something that you build.(Gaston de Bachelar)</p>'
        #st.markdown(new_title, unsafe_allow_html=True)
        if submit_button:
            # Simulated decoded values
            user_type_input = {'City': 0 ,'Town': 1 , 'Village': 2 }  # Simulated decoded values for 'user_type_input'
            user_luxury_input = {'Campsite': 0 ,'Glamping': 1 , 'Camper': 2 }  # Simulated decoded values for 'user_luxury_input'
            user_beach_input = {'No': 0, 'Yes': 1}  # Simulated decoded values for 'user_beach_input'
            user_wild_input = {'No': 0, 'Yes': 1}  # Simulated decoded values for 'user_destination_input'


            # Simulated prediction model
            user_category_encoded = 0  # Simulated user category encoded value
            user_category = cat_sites_decoded[user_category_encoded]

            # Display results at the bottom of the page
            st.markdown("## Results")
            st.write("#### Category more adequate to you:", user_category)

            # Get top three sites to visit
            top_sites_names = get_top_three_sites_by_category(user_category_encoded, 0)  # Simulated destination encoded value
            st.markdown("## Places you shouldn't miss:")
            for idx, site_name in enumerate(top_sites_names):
                st.write(f"{idx+1}. {site_name}")

            # Display sites on a map
            st.subheader("Map of these sites")
            # Simulated map data
            map_data = {'latitud': [1.23, 4.56, 7.89], 'longitud': [9.01, 2.34, 5.67], 'name': ['Site 1', 'Site 2', 'Site 3']}
            map_data = df[df['name'].isin(top_sites_names)][['latitud', 'longitud', 'name']]
            map_data.rename(columns={'latitud': 'LAT', 'longitud': 'LON'}, inplace=True)
            st.map(map_data)

    def get_top_three_sites_by_category(user_category_encoded, user_destination_encoded):
        # Simulated dataframe with site data
        df = {'cat_sites_reduced_encoded': [0, 1, 0, 2], 'destination_encoded': [0, 0, 1, 1], 'rating': [5, 4, 3, 2], 'name': ['Site 1', 'Site 2', 'Site 3', 'Site 4']}
        df = pd.DataFrame(df)
        # Filter sites of this category and destination
        category_sites = df[(df['cat_sites_reduced_encoded'] == user_category_encoded) & (df['destination_encoded'] == user_destination_encoded)]
        # Sort the sites by the column "rating" in descending order
        sorted_sites = category_sites.sort_values(by='rating', ascending=False)
        # Take the top three sites with the highest ratings and get only the "name" column
        top_three_sites = sorted_sites.head(3)['name']

        return top_three_sites.tolist()

if __name__ == "__main__":
    main()
