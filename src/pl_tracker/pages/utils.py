import streamlit as st


def common_nav():

    columns = st.columns([5, 1, 1, 1, 1, 1, 1], vertical_alignment="center")

    with columns[0]:
        st.title(f"✨ Hello {st.user.get("name", "username")}!")

    with columns[-1]:
        st.markdown(
            "<div style='text-align: center; font-weight: bold; margin-bottom: -350px;'>Athlete</div>",
            unsafe_allow_html=True,
        )
        if "users_list" in st.session_state and st.session_state["is_admin"]:
            username = st.selectbox(
                "",
                options=[user["name"] for user in st.session_state["users_list"]],
                key="selected_user",
                index=0,
            )

            st.session_state["selected_user_id"] = [
                user["id"]
                for user in st.session_state["users_list"]
                if user["name"] == username
            ][0]

    # if not st.user["email_verified"]:
    #     st.warning("Please verify your email and login back to unlock all features")

    with st.sidebar:

        # st.markdown("<br>", unsafe_allow_html=True)

        with st.expander(f"👤 {st.user.get("name", "username")}", expanded=False):
            if st.button("🚪 Logout"):
                st.logout()

            st.link_button(
                "Find Any Bug?",
                "mailto:sanna.davide32@gmail.com?subject=Bug%20Report:",
                icon=":material/bug_report:",
                type="tertiary",
            )


def video_comparator(key_suffix=None):
    program_selector = st.selectbox(
        "Select a Program",
        options=st.session_state["user_sessions"]["name"].unique().tolist(),
        index=0,
        key=f"program_selector_{key_suffix}" if key_suffix else "program_selector",
        help="Select a program to view the videos associated with it.",
    )

    if program_selector:
        week_selector = st.selectbox(
            "Select a Week",
            options=st.session_state["user_sessions"]
            .query(f"name == '{program_selector}'")["Week"]
            .unique()
            .tolist(),
            index=0,
            key=f"week_selector_{key_suffix}" if key_suffix else "week_selector",
            help="Select a week to view the videos associated with it.",
        )
        if week_selector:
            day_selector = st.selectbox(
                "Select a Day",
                options=st.session_state["user_sessions"]
                .query(f"name == '{program_selector}' and Week == {week_selector}")[
                    "Day"
                ]
                .unique()
                .tolist(),
                index=0,
                key=f"day_selector_{key_suffix}" if key_suffix else "day_selector",
                help="Select a day to view the videos associated with it.",
            )

            # if day_selector:
            #     video_selector = st.selectbox(
            #         "Select a Video",
            #         options=st.session_state["videos"]
            #         .query(
            #             f"name == '{program_selector}' and week == {week_selector} and day == {day_selector}"
            #         )["video"]
            #         .unique()
            #         .tolist(),
            #         index=0,
            #         key=(
            #             "video_selector_{key_suffix}"
            #             if key_suffix
            #             else "video_selector"
            #         ),
            #         help="Select a video to view.",
            #     )
            #     if video_selector:
            #         video_url = st.session_state[
            #             "supabase_client"
            #         ].get_bucket_signed_url(
            #             "videos",
            #             f"{program_selector}/{week_selector}/{day_selector}/{video_selector}",
            #         )
            #         st.video(video_url)
