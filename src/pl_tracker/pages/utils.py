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


def video_comparator(user_id, key_suffix=None):
    user_sessions = st.session_state["user_sessions"].query(f"user_id == '{user_id}'")
    user_videos = st.session_state["videos_data"].query(f"user_id == '{user_id}'")

    program_selector = st.selectbox(
        "Select a Program",
        options=user_videos["program"].unique().tolist(),
        index=None,
        key=f"program_selector_{key_suffix}" if key_suffix else "program_selector",
        help="Select a program to view the videos associated with it.",
    )

    if program_selector:
        week_selector = st.selectbox(
            "Select a Week",
            options=user_videos.query(f"program == '{program_selector}'")["week"]
            .unique()
            .tolist(),
            index=None,
            key=f"week_selector_{key_suffix}" if key_suffix else "week_selector",
            help="Select a week to view the videos associated with it.",
        )

        if week_selector:
            day_selector = st.selectbox(
                "Select a Day",
                options=user_videos.query(
                    f"program == '{program_selector}' and week == {int(week_selector)}"
                )["day"]
                .unique()
                .tolist(),
                index=None,
                key=f"day_selector_{key_suffix}" if key_suffix else "day_selector",
                help="Select a day to view the videos associated with it.",
            )

            if day_selector:
                exercise_selector = st.selectbox(
                    "Select an Exercise",
                    options=user_videos.query(
                        f"program == '{program_selector}' and week == {week_selector} and day == {day_selector}"
                    )["exercise"]
                    .unique()
                    .tolist(),
                    index=None,
                    key=(
                        f"exercise_selector_{key_suffix}"
                        if key_suffix
                        else "exercise_selector"
                    ),
                    help="Select an exercise to view the videos associated with it.",
                )
                if exercise_selector:
                    video_selector = st.selectbox(
                        "Select a Video",
                        options=user_videos.query(
                            f"program == '{program_selector}' and week == {week_selector} and day == {day_selector}"
                        )["video_name"],
                        key=(
                            f"video_selector_{key_suffix}"
                            if key_suffix
                            else "video_selector"
                        ),
                        help="Select a video to view.",
                    )
                    if video_selector:
                        video_url = st.session_state["supabase_client"].get_user_video(
                            st.session_state["selected_user_id"],
                            f"{program_selector}/Week {week_selector}/Day {day_selector}/{exercise_selector}/{video_selector}",
                        )

                        width = st.slider(
                            label="Width",
                            min_value=0,
                            max_value=100,
                            value=70,
                            format="%d%%",
                            key=(
                                f"video_width_{key_suffix}"
                                if key_suffix
                                else "video_width"
                            ),
                        )

                        width = max(width, 0.01)
                        side = max((100 - width) / 2, 0.01)

                        _, container, _ = st.columns([side, width, side])
                        container.video(data=video_url)

                        st.markdown("### Video Metadata")
                        st.json(
                            user_videos.query(
                                f"program == '{program_selector}' and week == {week_selector} and day == {day_selector} and exercise == '{exercise_selector}'"
                            )[["Sets", "Reps", "Effective Set", "Weight"]].to_dict(
                                orient="records"
                            )[
                                0
                            ],
                        )
