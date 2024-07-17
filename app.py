import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

# Load the configuration file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Function to update the config file
def update_config(new_config):
    with open('config.yaml', 'w') as file:
        yaml.dump(new_config, file, default_flow_style=False)

# Create the login widget
name, authentication_status, username = authenticator.login(
    location='main', 
    fields={
        'Form name': 'Login',
        'Username': 'Username',
        'Password': 'Password',
        'Login': 'Login'
    }
)

# Display different content based on authentication status
if authentication_status:
    st.write(f'Welcome *{name}*')
    
    authenticator.logout('Logout',"main")
    st.title('Some content')

    # Add additional widgets as needed
    try:
        if authenticator.reset_password(username, fields={
            'Form name': 'Reset password',
            'Current password': 'Current password',
            'New password': 'New password',
            'Repeat password': 'Repeat password',
            'Reset': 'Reset'
        }):
            st.success('Password modified successfully')
            update_config(config)  # Update the config file
    except Exception as e:
        st.error(e)

    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
            pre_authorization=True,
            fields={
                'Form name': 'Register user',
                'Email': 'Email',
                'Username': 'Username',
                'Password': 'Password',
                'Repeat password': 'Repeat password',
                'Register': 'Register'
            }
        )
        if email_of_registered_user:
            st.success('User registered successfully')
            # Add the new user to the config
            config['credentials']['usernames'][username_of_registered_user] = {
                'email': email_of_registered_user,
                'failed_login_attempts': 0,
                'logged_in': False,
                'name': name_of_registered_user,
                'password': 'default_password'  # This will be hashed automatically
            }
            update_config(config)  # Update the config file
    except Exception as e:
        st.error(e)

    try:
        username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password(fields={
            'Form name': 'Forgot password',
            'Username': 'Username',
            'Submit': 'Submit'
        })
        if username_of_forgotten_password:
            st.success('New password to be sent securely')
            # Securely transfer the new password to the user
            update_config(config)  # Update the config file
        elif username_of_forgotten_password == False:
            st.error('Username not found')
    except Exception as e:
        st.error(e)

    try:
        username_of_forgotten_username, email_of_forgotten_username = authenticator.forgot_username(fields={
            'Form name': 'Forgot username',
            'Email': 'Email',
            'Submit': 'Submit'
        })
        if username_of_forgotten_username:
            st.success('Username to be sent securely')
            # Securely transfer the username to the user
        elif username_of_forgotten_username == False:
            st.error('Email not found')
    except Exception as e:
        st.error(e)

    try:
        if authenticator.update_user_details(username, fields={
            'Form name': 'Update user details',
            'Field': 'Field',
            'Name': 'Name',
            'Email': 'Email',
            'New value': 'New value',
            'Update': 'Update'
        }):
            st.success('Entries updated successfully')
            update_config(config)  # Update the config file
    except Exception as e:
        st.error(e)
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
