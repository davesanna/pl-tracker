import plotly.express as px
import pandas as pd
from src.pl_tracker.calculations import (
    compute_1rm_tests,
    compute_sets_per_week,
    get_nutrition_data_for_user,
)
import streamlit as st
import plotly.graph_objects as go


def map_time_resolution_to_frequency(time_resolution: str) -> str:
    """
    Map the time resolution to a frequency string for grouping data.

    Args:
        time_resolution (str): The time resolution to map ('Daily', 'Weekly', 'Monthly').

    Returns:
        str: The corresponding frequency string ('D', 'W', 'M').
    """
    if time_resolution == "Weekly":
        return "W"
    elif time_resolution == "Monthly":
        return "M"
    else:
        return "D"


def plot_1rm_progress(
    user_sessions: pd.DataFrame, time_definition: str = "Program", program: str = None
) -> px.line:
    """
    Plot the 1RM progress for each user and exercise.

    Args:
        user_sessions (pd.DataFrame): DataFrame containing session data with columns 'name', 'Exercise', '1rm_th'.

    Returns:
        px.line: Plotly line chart showing the 1RM progress.
    """
    if program:
        user_sessions = user_sessions.query(f"name == '{program}'")
        key = f"{time_definition}_1rm_plot_{program}"
    else:
        key = f"{time_definition}_1rm_plot"

    exercises = ["Squat", "Panca", "Stacco", "Sumo"]

    exercise_sessions = user_sessions[user_sessions["Exercise"].isin(exercises)]

    if time_definition == "Program":
        groupby = "name"
        group_type = "sum"

        max_rm = compute_1rm_tests(exercise_sessions, groupby)

        total_progression = (
            max_rm.groupby([groupby] + ["date"], as_index=False)
            .agg({"1rm_th": group_type})
            .reset_index()
            .round()
            .sort_values("date")
        )

    elif time_definition == "Weekly":
        groupby = "program_week"
        group_type = "mean"

        max_rm = compute_1rm_tests(exercise_sessions, groupby)

        max_rm = (
            max_rm.loc[max_rm["1rm_th"] != 0, :]
            .groupby(["program_week", "date", "Exercise"], as_index=False)["1rm_th"]
            .mean()
            .reset_index()
        )

        max_rm = (
            max_rm.groupby([groupby] + ["date", "Exercise"], as_index=False)["1rm_th"]
            .mean()
            .reset_index()
        )

        total_progression = (
            max_rm.groupby([groupby] + ["date", "Exercise"], as_index=False)
            .agg({"1rm_th": group_type})
            .groupby(["date", "program_week"])["1rm_th"]
            .sum()
            .reset_index()
            .round()
            .sort_values(["date", "program_week"])
        )

    fig = go.Figure()

    trend_line = total_progression.sort_values(["date", groupby])

    fig.add_trace(
        go.Scatter(
            x=trend_line[groupby],
            y=trend_line["1rm_th"],
            mode="lines+markers",
            name="Total (Trend)",
            line=dict(color="blue", dash="dash"),
            # showlegend=False
        )
    )

    fig.add_trace(
        go.Bar(
            x=total_progression[groupby],
            y=total_progression["1rm_th"],
            name="Total",
            marker=dict(color="red"),
        )
    )

    exercise_colors = {
        "Squat": "green",
        "Panca": "yellow",
        "Stacco": "purple",
        "Sumo": "cyan",
    }

    for exercise in max_rm["Exercise"].unique():
        exercise_data = max_rm[max_rm["Exercise"] == exercise]
        fig.add_trace(
            go.Bar(
                x=exercise_data[groupby],
                y=exercise_data["1rm_th"],
                name=f"{exercise}",
                marker=dict(color=exercise_colors.get(exercise, "gray")),
            ),
        )

    fig.update_layout(
        barmode="group",
        title="1RM Development",
        xaxis=dict(title="Program Name", dtick=1),
        yaxis=dict(
            title="Weight (kg)", range=[0, max(total_progression["1rm_th"]) * 1.1]
        ),
    )

    fig.update_yaxes(matches="y")

    st.plotly_chart(fig, use_container_width=True, key=key)

    return fig


def plot_sets_per_week(
    user_sessions: pd.DataFrame, exercise: str, program: str = None, type: str = "Line"
) -> px.line:
    """
    Plot the total sets per week for a given exercise.

    Args:
        user_sessions (pd.DataFrame): DataFrame containing session data with columns 'name', 'Week', 'Exercise', 'Sets'.
        exercise (str): The exercise to filter by.

    Returns:
        px.line: Plotly line chart showing the total sets per week for the specified exercise.
    """

    sets_per_week = compute_sets_per_week(user_sessions, exercise, program)

    if exercise == "All":
        sets_per_week = (
            sets_per_week.groupby(["date", "program_week"], as_index=False)
            .agg(total_sets=("total_sets", "sum"))
            .sort_values(["date", "program_week"])
        )
    if type == "Line":
        fig = px.line(
            sets_per_week,
            x="program_week",
            y="total_sets",
            title=f"{exercise} Sets per Week",
            labels={"Week": "Week", "Sets": "Sets"},
        )
    elif type == "Bar":
        fig = px.bar(
            sets_per_week,
            x="program_week",
            y="total_sets",
            title=f"{exercise} Sets per Week",
            labels={"program_week": "Week", "total_sets": "Sets"},
        )

    fig.update_xaxes(dtick=1)

    st.plotly_chart(fig, use_container_width=True)

    return fig


def plot_macros_per_day(
    nutrition_data: pd.DataFrame, user_id: str, time_resolution: str = "Daily"
) -> None:
    frequency = map_time_resolution_to_frequency(time_resolution)

    macros_data = (
        get_nutrition_data_for_user(nutrition_data, user_id)
        .groupby(pd.Grouper(key="Date", freq=frequency))
        .agg({"Protein (%)": "mean", "Carbs (%)": "mean", "Fat (%)": "mean"})
        .reset_index()
    )

    fig = px.bar(
        macros_data,
        x="Date",
        y=["Protein (%)", "Carbs (%)", "Fat (%)"],
        title=f"Macronutrients (%) - {time_resolution}",
    )

    fig.update_xaxes(rangeslider_visible=True)

    return st.plotly_chart(fig, use_container_width=True)


def plot_steps_per_day(
    nutrition_data: pd.DataFrame, user_id: str, time_resolution: str = "Daily"
) -> None:
    """
    Plot the steps per day for a given user.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date', 'Steps'.

    Returns:
        None: Displays the plot using Streamlit.
    """
    frequency = map_time_resolution_to_frequency(time_resolution)

    step_data = (
        get_nutrition_data_for_user(nutrition_data, user_id)
        .groupby(pd.Grouper(key="Date", freq=frequency))
        .agg({"Steps": "mean"})
        .reset_index()
    )

    fig = px.bar(
        step_data,
        x="Date",
        y="Steps",
        title=f"Steps - {time_resolution}",
    )

    fig.update_xaxes(rangeslider_visible=True)

    return st.plotly_chart(fig, use_container_width=True)


def plot_calories_per_day(
    nutrition_data: pd.DataFrame, user_id: str, time_resolution: str = "Daily"
) -> None:
    """
    Plot the calories per day for a given user.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date', 'Calories (kcal)'.

    Returns:
        None: Displays the plot using Streamlit.
    """

    frequency = map_time_resolution_to_frequency(time_resolution)

    calories_data = (
        get_nutrition_data_for_user(nutrition_data, user_id)
        .groupby(pd.Grouper(key="Date", freq=frequency))
        .agg({"Calories (kcal)": "mean"})
        .reset_index()
    )

    fig = px.bar(
        calories_data,
        x="Date",
        y="Calories (kcal)",
        title=f"Calories (kcal) - {time_resolution}",
        labels={"Date": "Date", "Calories (kcal)": "Calories (kcal)"},
    )

    fig.update_xaxes(rangeslider_visible=True)

    return st.plotly_chart(fig, use_container_width=True)


def plot_expenditure_per_day(
    nutrition_data: pd.DataFrame, user_id: str, time_resolution: str = "Daily"
) -> None:
    """
    Plot the expenditure per day for a given user.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date', 'Expenditure'.

    Returns:
        None: Displays the plot using Streamlit.
    """
    frequency = map_time_resolution_to_frequency(time_resolution)

    expenditure_data = (
        get_nutrition_data_for_user(nutrition_data, user_id)
        .groupby(pd.Grouper(key="Date", freq=frequency))
        .agg({"Expenditure": "mean"})
        .reset_index()
    )
    fig = px.bar(
        expenditure_data,
        x="Date",
        y="Expenditure",
        title=f"Expenditure - {time_resolution}",
    )

    fig.update_xaxes(rangeslider_visible=True)

    return st.plotly_chart(fig, use_container_width=True)


def plot_weight_per_day(
    nutrition_data: pd.DataFrame, user_id: str, time_resolution: str = "Daily"
) -> None:
    """
    Plot the weight per day for a given user.

    Args:
        nutrition_data (pd.DataFrame): DataFrame containing nutrition data with columns 'user_id', 'Date', 'Weight (kg)'.

    Returns:
        None: Displays the plot using Streamlit.
    """
    fig = go.Figure()

    frequency = map_time_resolution_to_frequency(time_resolution)

    user_nutrition = (
        get_nutrition_data_for_user(nutrition_data, user_id)
        .groupby(pd.Grouper(key="Date", freq=frequency))
        .agg({"Weight (kg)": "mean", "Trend Weight (kg)": "mean"})
        .reset_index()
    )

    user_nutrition = user_nutrition.loc[user_nutrition["Weight (kg)"] > 0, :]

    fig.add_trace(
        go.Scatter(
            x=user_nutrition["Date"],
            y=user_nutrition["Weight (kg)"],
            mode="lines+markers",
            name="Weight (kg)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=user_nutrition["Date"],
            y=user_nutrition["Trend Weight (kg)"],
            mode="lines+markers",
            name="Weight Trend (kg)",
            line=dict(color="red", dash="dash"),
        )
    )

    fig.update_layout(
        title=f"Weight (kg) - {time_resolution}",
        xaxis_title="Date",
        yaxis_title="Weight (kg)",
    )

    fig.update_xaxes(rangeslider_visible=True)

    return st.plotly_chart(fig, use_container_width=True)
