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
    type=["mp4", "mov", "avi", "jpeg"],
    help="Currently, only MP4, MOV, and AVI formats are supported.",
)

if uploaded_video:
    st.video(uploaded_video)
