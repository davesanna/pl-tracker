import base64
import streamlit as st
import plotly.express as px
import pandas as pd
import requests

from src.pl_tracker.database import SupabaseClient
from src.pl_tracker.plots import plot_1rm_progress, plot_sets_per_week
import streamlit.components.v1 as components
from streamlit_pdf_viewer import pdf_viewer


st.header("Programs")
# program_name = st.text_input("Enter Program Name")
# print("Program Name:", program_name)
# if program_name:
#     program_id = (
#         st.session_state["supabase_client"]
#         .client.table("programs")
#         .select("id")
#         .eq("name", program_name)
#         .execute()
#     )

#     if program_id.data:
#         program_id = program_id.data[0]["id"]
#         print("Program ID:", program_id)
#         program = (
#             st.session_state["supabase_client"]
#             .client.table("sessions")
#             .select("*")
#             .eq("program_id", program_id)
#             .execute()
#         )
#         program_df = pd.DataFrame(program.data)
#         print("Program DataFrame:", program_df)
#         st.dataframe(
#             program_df.loc[
#                 :,
#                 [
#                     col
#                     for col in program_df.columns
#                     if "id" not in col and "created" not in col
#                 ],
#             ],
#             use_container_width=True,
#         )

#         sets_per_week = program_df.groupby("Week")["Sets"].sum().reset_index()
#         fig = px.bar(
#             sets_per_week,
#             x="Week",
#             y="Sets",
#             title="Sets per Week",
#             labels={"Week": "Week", "Sets": "Sets"},
#         )
#         fig.update_xaxes(dtick=1)

#         with st.container(border=True):
#             st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.warning("No sessions found for this program.")

st.subheader("Programs Comparison")

bucket_content = st.session_state["supabase_client"].get_bucket_content(
    "programs", user_id=st.session_state["selected_user_id"]
)

col1, col2 = st.columns(2)

if not bucket_content:
    st.warning("No PDF files found in the bucket.")
else:
    with col1:
        selected_file = st.selectbox(
            "Choose a PDF file to view (Comparison 1)",
            options=bucket_content,
            index=None,
        )

        if selected_file:
            file_url = st.session_state["supabase_client"].get_bucket_signed_url(
                "programs", selected_file
            )
            response = requests.get(file_url)
            response.raise_for_status()

            # base64_pdf = base64.b64encode(response.content).decode("utf-8")
            pdf_viewer(response.content, height=1400)

            program_name = selected_file.split(".")[0]
            if program_name in st.session_state["user_sessions"]["name"].unique():
                plot_type = st.selectbox(
                    "Select a plot type",
                    options=["Line", "Bar"],
                    key="sets_per_week_plot_type",
                )

                plot_sets_per_week(
                    st.session_state["user_sessions"],
                    "All",
                    program=program_name,
                    type=plot_type,
                )
                time_definition = st.selectbox(
                    "Select Time Definition",
                    options=["Program", "Weekly"],
                    key="time_definition",
                )
                plot_1rm_progress(
                    st.session_state["user_sessions"],
                    time_definition,
                    program=program_name,
                )

    with col2:
        selected_file_comp = st.selectbox(
            "Choose a PDF file to view (Comparison 2)",
            options=bucket_content,
            index=None,
        )

        if selected_file:
            file_url = st.session_state["supabase_client"].get_bucket_signed_url(
                "programs", selected_file_comp
            )
            response = requests.get(file_url)
            response.raise_for_status()

            # base64_pdf = base64.b64encode(response.content).decode("utf-8")

            pdf_viewer(response.content, height=1400)

            program_name_comp = selected_file_comp.split(".")[0]
            if program_name_comp in st.session_state["user_sessions"]["name"].unique():
                plot_type_comp = st.selectbox(
                    "Select a plot type",
                    options=["Line", "Bar"],
                    key="sets_per_week_plot_type_comp",
                )
                plot_sets_per_week(
                    st.session_state["user_sessions"],
                    "All",
                    program=program_name_comp,
                    type=plot_type_comp,
                )
                time_definition = st.selectbox(
                    "Select Time Definition",
                    options=["Program", "Weekly"],
                    key="time_definition_comp",
                )
                plot_1rm_progress(
                    st.session_state["user_sessions"],
                    time_definition,
                    program=program_name_comp,
                )
