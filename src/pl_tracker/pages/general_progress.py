import streamlit as st
import plotly.express as px
from src.pl_tracker.auth import cache_user_data, fetch_user_data
from src.pl_tracker.calculations import (
    compute_sets_per_week,
    get_last_7d_avg_calories_target,
    get_last_nutrition_entry_date,
    get_last_weight_entry,
    get_nutrition_data_for_user,
)
from src.pl_tracker.database import SupabaseClient
import pandas as pd
import plotly.graph_objects as go
from src.pl_tracker.plots import (
    plot_1rm_progress,
    plot_calories_per_day,
    plot_expenditure_per_day,
    plot_sets_per_week,
    plot_steps_per_day,
    plot_weight_per_day,
)

st.header(
    f"General Stats (Last updated: {get_last_nutrition_entry_date(st.session_state['nutrition_data'], st.session_state['selected_user_id'])})"
)

st.markdown("<br>", unsafe_allow_html=True)


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


st.markdown("<br>", unsafe_allow_html=True)

# with col1:
#     fig_weight = go.Figure(
#         go.Indicator(
#             mode="gauge+number",
#             value=st.session_state["nutrition_data"]
#             .query(f"user_id == \"{st.session_state['selected_user_id']}\"")
#             .iloc[-1]["Trend Weight (kg)"],
#             title={"text": "Weight (kg)"},
#             gauge={"axis": {"range": [50, 200]}},  # Adjust range if needed
#         )
#     )

#     fig_weight.update_layout(
#         height=360,  # Make the gauge smaller
#         width=140,  # Adjust width to make the gauge smaller
#     )
#     st.plotly_chart(fig_weight, use_container_width=True)


# with col2:
#     fig_calories = go.Figure(
#         go.Indicator(
#             mode="gauge+number",
#             value=st.session_state["nutrition_data"]
#             .query(f"user_id == \"{st.session_state['selected_user_id']}\"")
#             .iloc[-1]["Target Calories (kcal)"],
#             title={"text": "Calorie Target (kcal/day)"},
#             gauge={"axis": {"range": [1000, 4000]}},  # Adjust range as needed
#         )
#     )

#     fig_calories.update_layout(
#         height=360,  # Make the gauge smaller
#         width=140,  # Adjust width to make the gauge smaller
#     )
#     st.plotly_chart(fig_calories, use_container_width=True)

time_definition = st.selectbox(
    "Select an time definition to view the 1RM progress",
    options=["Program", "Weekly"],
    key="time_definition",
)
plot_1rm_progress(
    st.session_state["user_sessions"], st.session_state.get("time_definition")
)


col1, col2 = st.columns(2)

with col1:
    plot_steps_per_day(
        st.session_state["nutrition_data"], st.session_state["selected_user_id"]
    )

with col2:
    plot_calories_per_day(
        st.session_state["nutrition_data"], st.session_state["selected_user_id"]
    )

col3, col4 = st.columns(2)
with col3:
    plot_expenditure_per_day(
        st.session_state["nutrition_data"], st.session_state["selected_user_id"]
    )

with col4:
    plot_weight_per_day(
        st.session_state["nutrition_data"], st.session_state["selected_user_id"]
    )


st.subheader("Volume per Exercise")


exercise_selection = st.selectbox(
    "Select an exercise to view the sets per week",
    options=["All", "Squat", "Panca", "Stacco", "Sumo"],
    key="exercise_selection",
)


plot_sets_per_week(st.session_state["user_sessions"], exercise_selection)
