import streamlit as st


# with st.form("session_form"):
#     program = st.text_input("Program")
#     week = st.number_input("Week #", value=1, min_value=1)
#     day = st.number_input("Day #", value=1, min_value=1)
#     exercise = st.text_input("Exercise")
#     video = st.file_uploader("Upload Session Video", type=["mp4", "mov", "avi"])
#     submitted = st.form_submit_button("Upload")

#     if submitted:
#         if not all([program, exercise, video]):
#             st.error("Please fill all fields & upload a video.")
#         else:
#             meta = SessionMetadata(
#                 program=program, week=week, day=day, exercise=exercise
#             )
#             supabase_client.upload_video_and_meta(video, meta, st.user)

st.header("Upload Program")

uploaded_file = st.file_uploader(
    "Upload a program file (PDF or Excel)",
    type=["pdf"],
    help="The file should contain program details including exercises, sets, and weeks.",
)


if uploaded_file is not None:
    try:
        # Process the uploaded file
        if uploaded_file.name.endswith(".pdf"):
            st.session_state["supabase_client"].upload_program_file(
                file=uploaded_file,
                user_id=st.session_state["selected_user_id"],
            )
            st.success("PDF file uploaded successfully!")
            # Here you would typically process the PDF to extract program details
        else:
            st.error("Unsupported file format. Please upload a PDF file.")
    except Exception as e:
        st.error(f"Error processing the file: {e}")
