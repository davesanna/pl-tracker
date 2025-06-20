import streamlit as st

from src.pl_tracker.auth import login

st.title("📔 PL Tracker")

st.markdown(
    "Hello! Welcome to the PL Tracker app, a test application for tracking your gym progress!"
)

st.write("\n")

if st.button(
    "✨ Sign up to the PL Tracking App!",
    type="primary",
    key="checkout-button",
    use_container_width=True,
):
    login()

with st.expander("📝 Privacy & Data Security Disclaimer"):
    st.markdown(
        """
This app uses Auth0 for secure authentication, meaning your login credentials (such as email addresses) are handled and stored securely by Auth0, a trusted identity management platform.

- 🔒 Secure Storage: Your authentication data is protected by Auth0’s robust security infrastructure.
- 🗓️ Data Retention: This is a test application. All user data, including email addresses, will be permanently deleted by March 31st when the video is released.
- 🚫 No Data Reuse: Your credentials will not be shared, reused, or repurposed for any other application or service.

If you have any questions or concerns, feel free to [reach out](mailto:sanna.davide32@gmail.com)  
"""
    )


st.link_button(
    "Find Any Bug?",
    "mailto:sanna.davide32@gmail.com?subject=Bug%20Report:",
    icon=":material/bug_report:",
    type="tertiary",
)

st.html("./styles.html")
