import streamlit as st
import os

# 1. Configure Layout and Branding
st.set_page_config(
    page_title="DrawPredict Tactical Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Native Mobile UI Shell and Logo Styling
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container { padding-top: 1.5rem !important; }
        [data-testid="stSidebar"] img {
            max-width: 150px;
            margin-bottom: 20px;
            margin-left: auto;
            margin-right: auto;
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Sidebar Organization for Scaling (States)
st.sidebar.image("logo.png")
st.sidebar.markdown("# 🌍 Multi-State Hub")

# In future steps, we will dynamic-link modules based on this selection.
selected_state = st.sidebar.selectbox("Select Active Region:", ["Texas", "California (In Development)", "Florida (In Development)"])
st.sidebar.markdown("---")
st.sidebar.write(f"Active Hub: **{selected_state}**")

# 4. Main Landing Layout
st.title("🤖 DrawPredict Tactical Suite")
st.markdown(f"### Welcome to the **{selected_state}** Production Hub")
st.write("Use the slide-out menu drawer on the left to navigate between real-time data engines and backtesters.")
st.markdown("---")

# Global Data Pipeline Status (Dynamic linking required here later)
col1, col2 = st.columns(2)
with col1:
    # Later we will make this sync with specific file lists
    st.info("📊 **Global Ingestion Status:** Core Historical Records Synchronized.")
with col2:
    st.success("🔥 **Automation:** Engaged and isolated across modern timelines.")
