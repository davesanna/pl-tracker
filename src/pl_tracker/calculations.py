import pandas as pd


def compute_1rm_tests(user_sessions: pd.DataFrame, groupby: str) -> pd.DataFrame:
    """
    Compute the 1RM progress for each user and exercise.

    Args:
        sessions (pd.DataFrame): DataFrame containing session data with columns 'name', 'Exercise', 'Topset'.

    Returns:
        pd.DataFrame: DataFrame with columns 'name', 'Exercise', '1rm_th' representing the 1RM progress.
    """
    if groupby == "name":
        tests_df = user_sessions.query("Test == True")
    else:
        tests_df = user_sessions.copy()

    tests_df["1rm_th"] = round(tests_df["Topset"] / tests_df["percentage"], 2)

    return tests_df


def compute_sets_per_week(
    user_sessions: pd.DataFrame, exercise: str, program: str
) -> pd.DataFrame:
    """
    Compute the total sets per week for a given exercise.

    Args:
        user_sessions (pd.DataFrame): DataFrame containing session data with columns 'name', 'Week', 'Exercise', 'Sets'.
        exercise (str): The exercise to filter by.

    Returns:
        pd.DataFrame: DataFrame with columns 'name', 'Week', 'Exercise', 'total_sets' representing the total sets per week.
    """
    import streamlit as st

    if program:
        if program.endswith(".pdf"):
            program = program.split(".")[0]
        user_sessions = user_sessions.query(f"name == '{program}'")

    if exercise != "All":
        sorted_sessions = user_sessions.query(f"Exercise == '{exercise}'").sort_values(
            by=["date", "name", "Week", "Day"]
        )
    else:
        sorted_sessions = user_sessions.sort_values(by=["date", "name", "Week", "Day"])

    sets_per_week = sorted_sessions.groupby(
        ["date", "program_week", "Exercise"], as_index=False
    ).agg(total_sets=("Sets", "sum"))

    return sets_per_week


def get_last_weight_entry(nutrition_data: pd.DataFrame, user_id: str) -> pd.DataFrame:
    """
    Get the last weight entry for a user.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date', 'Weight (kg)'.
        user_id (str): The user ID to filter by.

    Returns:
        pd.DataFrame: DataFrame with the last weight entry for the specified user.
    """
    nutrition_data["Date"] = pd.to_datetime(nutrition_data["Date"])
    user_nutrition = nutrition_data.query(f"user_id == '{user_id}'")
    last_weight_entry = user_nutrition.sort_values(by="Date", ascending=False).head(1)[
        "Trend Weight (kg)"
    ]

    return last_weight_entry


def get_last_7d_avg_calories_target(
    nutrition_data: pd.DataFrame, user_id: str
) -> pd.DataFrame:
    """
    Get the last 7 days of caloric target for a user.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date', 'Calories Target'.
        user_id (str): The user ID to filter by.

    Returns:
        pd.DataFrame: DataFrame with the last 7 days of caloric target for the specified user.
    """
    nutrition_data["Date"] = pd.to_datetime(nutrition_data["Date"])
    user_nutrition = nutrition_data.query(f"user_id == '{user_id}'")
    last_7d_avg_caloric_target = (
        user_nutrition.sort_values(by="Date", ascending=False)
        .head(7)[["Target Calories (kcal)"]]
        .reset_index(drop=True)
        .mean()
    )

    return last_7d_avg_caloric_target


def get_last_nutrition_entry_date(
    nutrition_data: pd.DataFrame, user_id: str
) -> pd.Timestamp:
    """
    Get the last entry date for a user's nutrition data.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date'.
        user_id (str): The user ID to filter by.

    Returns:
        pd.Timestamp: The last entry date for the specified user.
    """
    nutrition_data["Date"] = pd.to_datetime(nutrition_data["Date"])
    user_nutrition = nutrition_data.query(f"user_id == '{user_id}'")
    last_entry_date = user_nutrition["Date"].max()

    return last_entry_date.strftime("%d-%m-%Y")


def get_nutrition_data_for_user(
    nutrition_data: pd.DataFrame, user_id: str
) -> pd.DataFrame:
    """
    Get the nutrition data for a specific user.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date', 'Calories Target', etc.
        user_id (str): The user ID to filter by.

    Returns:
        pd.DataFrame: DataFrame containing the nutrition data for the specified user.
    """
    nutrition_data["Date"] = pd.to_datetime(nutrition_data["Date"])
    user_nutrition = (
        nutrition_data.query(f"user_id == '{user_id}'")
        .sort_values(by="Date", ascending=False)
        .reset_index(drop=True)
    )

    return user_nutrition
