import streamlit as st
import plotly.express as px

from auth0.authentication import GetToken
from auth0.management import Auth0
from collections import Counter
from datetime import datetime

st.title("Admin Page")


@st.cache_resource(ttl=10 * 60)
def get_client(domain, client_id, client_secret):
    get_token = GetToken(domain, client_id, client_secret)
    token = get_token.client_credentials(f"https://{domain}/api/v2/")
    mgmt_api_token = token["access_token"]
    auth0 = Auth0(domain, mgmt_api_token)
    return auth0


@st.cache_data(ttl=10 * 60)
def get_users(_auth0_client):
    users = _auth0_client.users.list(page=0, per_page=100)
    return users


domain = st.secrets["auth"]["auth0"]["domain"]
client_id = st.secrets["auth"]["auth0"]["client_id"]
client_secret = st.secrets["auth"]["auth0"]["client_secret"]

auth0 = get_client(domain, client_id, client_secret)
users = get_users(auth0)

# with st.expander("Preview list of users"):
#     st.json(users)

st.subheader(f"You have **:primary[{users['total']}]** registered users")

created_per_date = [u["created_at"] for u in users["users"]]
created_per_day = [
    datetime.strptime(d.split("T")[0], "%Y-%m-%d") for d in created_per_date
]

num_created_per_day = Counter(created_per_day)
fig_created_per_day = px.bar(
    x=list(num_created_per_day.keys()),
    y=list(num_created_per_day.values()),
    labels={"x": "Date", "y": "Number of Users Created"},
    title="Users Created per Day",
    color_discrete_sequence=["#174C4F"],
)
st.plotly_chart(fig_created_per_day)

list_connection_type = [u["user_id"].split("|")[0] for u in users["users"]]
num_connection_type = Counter(list_connection_type)
fig_connection_type = px.pie(
    values=list(num_connection_type.values()),
    names=list(num_connection_type.keys()),
    title="Users by Connection Type",
    color_discrete_sequence=["#174C4F", "#F0EB4E"],
)
st.plotly_chart(fig_connection_type)
