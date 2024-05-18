import streamlit as st
from utilities.icon import page_icon

st.set_page_config(
    page_title="About",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main():
    page_icon("⚙️")
    st.subheader("About", divider="red", anchor=False)

    st.text(body = """Here at CAS Learning Technologies....""")


if __name__ == "__main__":
    main()