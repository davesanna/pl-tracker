import streamlit as st

from src.pl_tracker.pages.utils import video_comparator


st.header("Video Analysis")
st.markdown("This page is under construction. Please check back later for updates.")

col1, col2 = st.columns(2)
with col1:
    video_comparator(
        user_id=st.session_state["selected_user_id"], key_suffix="video_comparator_1"
    )

with col2:
    video_comparator(
        user_id=st.session_state["selected_user_id"], key_suffix="video_comparator_2"
    )


st.subheader("Upload Video")
uploaded_video = st.file_uploader(
    "Upload your video here",
    type=["mp4"],
    help="Currently, only MP4 format is supported.",
)

if uploaded_video:
    with st.form("video_metadata_form"):
        st.subheader("📄 Fill in the video metadata")
        user_programs = st.session_state["user_sessions"].query(
            "user_id == @st.session_state['selected_user_id']"
        )
        program = st.selectbox(
            "Program",
            user_programs["name"].unique().tolist(),
            index=0,
        )
        exercise = st.selectbox(
            "Exercise", ["Squat", "Sumo", "Stacco", "Panca"], index=0
        )
        week = st.selectbox("Week", [1, 2, 3, 4, 5], index=0)
        day = st.selectbox("Day", [1, 2, 3, 4], index=0)
        sets = st.selectbox(
            "Sets",
            options=list(range(1, 11)),  # Assuming sets can be from 1 to 10
            index=0,
            help="Select the number of sets for this exercise.",
        )
        reps = st.selectbox(
            "Reps",
            options=list(range(1, 21)),  # Assuming reps can be from 1 to 20
            index=0,
            help="Select the number of reps for this exercise.",
        )
        effective_set = st.selectbox(
            "Effective Set",
            options=list(range(1, 11)),
            index=0,
        )
        weight = st.number_input(
            "Weight (kg)",
            min_value=0.0,
            max_value=1000.0,
            value=100.0,
            step=0.25,
            help="Enter the weight used for this exercise in kilograms.",
        )
        notes = st.text_area("Notes", value="")

        submit = st.form_submit_button("Submit")

        if submit:
            st.session_state["supabase_client"].upload_video_and_meta(
                st.session_state["selected_user_id"],
                uploaded_video,
                {
                    "program": program,
                    "exercise": exercise,
                    "week": week,
                    "day": day,
                    "Sets": sets,
                    "Reps": reps,
                    "Effective Set": effective_set,
                    "Weight": weight,
                    "notes": notes,
                    "video_name": f"{exercise}_wk{week}_d{day}.mp4",
                },
            )
