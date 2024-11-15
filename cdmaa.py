import streamlit as st
st.set_page_config(page_title="CDMAA Referree Sheet Generator",page_icon=":sports_medal:",layout="wide",initial_sidebar_state="expanded")

# --- PAGE SETUP ---
home_page = st.Page(
    page = "views/home.py",
    title= "Home",
    icon = ":material/home:",
    default=True,
)

project_1_page = st.Page(
    page="views/generate.py",
    title="Statistics",
    icon=":material/contacts:",
)  

project_2_page = st.Page(
    page="views/referee.py",
    title="Referee Sheet Generator",
    icon=":material/settings:",
)  

# --- NAVIGATION SETUP ---
pg = st.navigation(pages = [home_page,project_2_page,project_1_page])

# --- RUN NAVIGATION ---
pg.run()

st.logo("assets/cdmaa-logo.png")
st.sidebar.text("Made with ❤️ by Eswin Paul")
# st.markdown("---")


