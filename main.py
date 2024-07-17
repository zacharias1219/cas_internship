import streamlit as st
from utils import load_config, init_authenticator

# Load configuration
config = load_config()

# Initialize authenticator
authenticator = init_authenticator(config)

# Create login widget
name, authentication_status, username = authenticator.login(
    location='sidebar', 
    fields={
        'Form name': 'Login',
        'Username': 'Username',
        'Password': 'Password',
        'Login': 'Login'
    }
)

# Sidebar navigation
st.sidebar.title("Navigation")
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    page = st.sidebar.radio("Go to", ["Cas", "Paths 1", "Paths 2", "Admin"])
else:
    st.sidebar.warning("Please log in to access the pages.")
    page = "Home"

# Page content
if authentication_status:
    if page == "Cas":
        st.page_link("CAS.py")
    elif page == "Paths 1":
        st.page_link("Paths1.py")
    elif page == "Paths 2":
        st.page_link("Paths2.py")
    elif page == "Admin":
        st.page_link("Admin.py")
else:
    st.title("Home Page")
    st.write("Please log in to access more pages.")
    if authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')