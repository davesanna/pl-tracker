from dotenv import load_dotenv
import streamlit as st
import os
from src.pl_tracker.auth import cache_user_data
from src.pl_tracker.pages.utils import common_nav

load_dotenv()

st.set_page_config(
    page_title="PL Tracker",
    page_icon="✨",
    initial_sidebar_state="collapsed",
    layout="wide",
)

landing_page = st.Page(
    "./src/pl_tracker/landing.py", title="Landing", icon=":material/home:"
)


admin_page = st.Page(
    "./src/pl_tracker/admin.py", title="Admin", icon=":material/admin_panel_settings:"
)
general_progress = st.Page(
    "./src/pl_tracker/pages/general_progress.py",
    title="General Progress",
    icon=":material/analytics:",
)

nutrition = st.Page(
    "./src/pl_tracker/pages/nutrition.py",
    title="Nutrition",
    icon=":material/analytics:",
)

inspect_program = st.Page(
    "./src/pl_tracker/pages/inspect_program.py",
    title="Programs",
    icon=":material/insights:",
)
load_program = st.Page(
    "./src/pl_tracker/pages/load_program.py",
    title="Load Program",
    icon=":material/upload_file:",
)

if not st.user.is_logged_in:
    pg = st.navigation(
        [landing_page],
        position="hidden",
    )
elif st.user.email == os.environ.get("ADMIN_EMAIL", None):
    cache_user_data()
    common_nav()
    pg = st.navigation(
        [general_progress, nutrition, inspect_program, load_program, admin_page],
    )
else:
    cache_user_data()
    common_nav()
    pg = st.navigation(
        [general_progress, nutrition, inspect_program, load_program],
    )

pg.run()
