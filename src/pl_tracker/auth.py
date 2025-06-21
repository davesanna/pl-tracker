import os
import streamlit as st
import pandas as pd
from src.pl_tracker.database import SupabaseClient


def login():
    st.login("auth0")


def cache_user_data():
    st.session_state["supabase_client"] = SupabaseClient(
        os.environ.get("SUPABASE_URL", st.secrets["supabase"]["supabase_url"]),
        os.environ.get("SUPABASE_API_KEY", st.secrets["supabase"]["api_key"]),
    )

    if st.user["is_logged_in"]:
        user_id = fetch_user(st.user["email"])

        if "user_sessions" not in st.session_state:
            user_sessions, nutrition_data, videos_data = fetch_user_data(user_id)
            rpe_table = fetch_rpe_table()
            st.session_state["user_sessions"] = pd.merge(
                user_sessions,
                rpe_table,
                left_on=["RPE Target", "max_reps"],
                right_on=["rpe", "reps"],
                how="left",
            )

            st.session_state["nutrition_data"] = nutrition_data
            st.session_state["videos_data"] = videos_data


def fetch_user(email):
    user_info = pd.DataFrame(
        st.session_state["supabase_client"]
        .client.table("users")
        .select("*")
        .eq("email", email)
        .execute()
        .data
    )
    if user_info.empty:
        st.error("User not found in the database.")
        return False

    is_admin = user_info["role"].iloc[0] == "admin"

    if is_admin:
        st.session_state["is_admin"] = True
        st.session_state["users_list"] = (
            st.session_state["supabase_client"]
            .client.table("users")
            .select("id, name")
            .execute()
        ).data

        user_id = [user["id"] for user in st.session_state["users_list"]]
    else:
        st.session_state["is_admin"] = False
        user_id = user_info["id"].tolist()

    return user_id


def fetch_user_data(user_id):
    """Fetch user data from the database."""

    user_programs = (
        st.session_state["supabase_client"]
        .client.table("programs")
        .select("*")
        .in_("user_id", user_id)
        .execute()
    ).data

    user_programs_dict = {program["id"]: program["name"] for program in user_programs}

    user_sessions = pd.DataFrame(
        st.session_state["supabase_client"]
        .client.table("sessions")
        .select("*")
        .in_("program_id", list(user_programs_dict.keys()))
        .execute()
        .data
    )

    user_sessions = (
        pd.merge(
            user_sessions,
            pd.DataFrame(user_programs)[["id", "name", "date", "user_id"]],
            left_on="program_id",
            right_on="id",
            suffixes=("", "_program"),
        )
        .drop(columns=["id_program"])
        .sort_values("date", ascending=True)
    )

    nutrition_data = fetch_and_preprocess_nutrition_data(user_id=user_id)

    user_sessions["program_week"] = (
        user_sessions["name"] + " - Week " + user_sessions["Week"].astype(str)
    )

    videos_data = pd.DataFrame(
        st.session_state["supabase_client"]
        .client.table("videos")
        .select("*")
        .in_("user_id", user_id)
        .execute()
        .data
    )

    return user_sessions, nutrition_data, videos_data


def fetch_rpe_table():
    """Fetch RPE table from the database."""
    rpe_table = pd.DataFrame(
        st.session_state["supabase_client"]
        .client.table("rpe_chart")
        .select("*")
        .execute()
        .data
    )
    return rpe_table


def fetch_and_preprocess_nutrition_data(
    nutrition_data: pd.DataFrame = None, user_id: str = None
):
    """Preprocess nutrition data for analysis."""
    if nutrition_data is None:
        nutrition_data = st.session_state["supabase_client"].fetch_nutrition_data(
            user_id
        )

    nutrition_data["Date"] = pd.to_datetime(nutrition_data["Date"])
    nutrition_data = nutrition_data.sort_values(by="Date", ascending=False)
    nutrition_data["Week"] = (
        nutrition_data["Date"]
        .dt.to_period("W-TUE")
        .apply(lambda x: f"WK {x.start_time.isocalendar()[1]} - {x.start_time.year}")
    )

    nutrition_data["Protein (%)"] = (
        nutrition_data["Protein (g)"] * 4
    ) / nutrition_data["Calories (kcal)"]

    nutrition_data["Carbs (%)"] = (nutrition_data["Carbs (g)"] * 4) / nutrition_data[
        "Calories (kcal)"
    ]
    nutrition_data["Fat (%)"] = (nutrition_data["Fat (g)"] * 9) / nutrition_data[
        "Calories (kcal)"
    ]

    nutrition_data["Total Macronutrients (%)"] = (
        nutrition_data["Carbs (%)"]
        + nutrition_data["Protein (%)"]
        + nutrition_data["Fat (%)"]
    )

    for column in ["Protein (%)", "Carbs (%)", "Fat (%)"]:
        nutrition_data[column] /= nutrition_data["Total Macronutrients (%)"]

    nutrition_data = nutrition_data.round(2)

    return nutrition_data
