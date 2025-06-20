import streamlit as st


def common_nav():

    columns = st.columns([4, 1, 1, 1, 1, 1, 1], vertical_alignment="center")

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
