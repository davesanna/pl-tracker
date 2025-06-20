from uuid import uuid4
import uuid
import pandas as pd
import streamlit as st
import plotly.express as px

from src.pl_tracker.auth import fetch_and_preprocess_nutrition_data
from src.pl_tracker.calculations import (
    get_last_7d_avg_calories_target,
    get_last_weight_entry,
    get_nutrition_data_for_user,
)
from src.pl_tracker.plots import (
    plot_calories_per_day,
    plot_expenditure_per_day,
    plot_macros_per_day,
    plot_steps_per_day,
    plot_weight_per_day,
)

st.header("Nutrition")
st.markdown("This page is under construction. Please check back later for updates.")


col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="### 🏋️ Current Weight",
        value=get_last_weight_entry(
            st.session_state["nutrition_data"], st.session_state["selected_user_id"]
        ),
        help="lol",
    )


with col2:
    st.metric(
        label="### 🍽️ Calorie Target",
        value=get_last_7d_avg_calories_target(
            st.session_state["nutrition_data"], st.session_state["selected_user_id"]
        ),
    )


# st.dataframe(
#     get_nutrition_data_for_user(
#         st.session_state["nutrition_data"], st.session_state["selected_user_id"]
#     )
# )

time_resolution = st.selectbox(
    "Time Resolution",
    ["Daily", "Weekly", "Monthly"],
    index=0,
    help="Select the time resolution for the plots.",
)

plot_weight_per_day(
    st.session_state["nutrition_data"],
    st.session_state["selected_user_id"],
    time_resolution,
)

col1, col2 = st.columns(2)
with col1:
    plot_calories_per_day(
        st.session_state["nutrition_data"],
        st.session_state["selected_user_id"],
        time_resolution,
    )
with col2:
    plot_macros_per_day(
        st.session_state["nutrition_data"],
        st.session_state["selected_user_id"],
        time_resolution,
    )

col1, col2 = st.columns(2)
with col1:
    plot_expenditure_per_day(
        st.session_state["nutrition_data"],
        st.session_state["selected_user_id"],
        time_resolution,
    )

with col2:
    plot_steps_per_day(
        st.session_state["nutrition_data"],
        st.session_state["selected_user_id"],
        time_resolution,
    )


st.subheader("Upload Nutrition Data")

uploaded_file = st.file_uploader(
    "Upload a CSV file with your nutrition data",
    type=["xlsx"],
    help="The CSV file should contain columns: 'Date', 'Calories (kcal)', 'Protein (g)', 'Carbs (g)', 'Fats (g)', 'Expenditure', 'Steps'.",
)
if uploaded_file is not None:
    pd.read_excel(uploaded_file)  # Validate the file format
    try:
        updated_nutrition_data = st.session_state[
            "supabase_client"
        ].upload_nutrition_data(
            nutrition_data=pd.read_excel(uploaded_file),
            user_id=[st.session_state["selected_user_id"]],
        )
        if updated_nutrition_data:
            st.session_state["nutrition_data"] = fetch_and_preprocess_nutrition_data(
                user_id=[st.session_state["selected_user_id"]]
            )
            st.success("Nutrition data uploaded successfully!")
    except Exception as e:
        st.error(f"Error uploading file: {e}")
