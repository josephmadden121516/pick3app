import streamlit as st
import os

# 1. Standard Responsive Page Configuration
st.set_page_config(
    page_title="DrawPredict Tactical Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="auto"  # Allows mobile OS to handle the responsive drawer natively
)

# 2. Simple Minimalist Branding (No aggressive padding overrides)
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 15px;">
        <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: #FFFFFF;">🎯 DrawPredict</h2>
        <div style="font-size: 11px; font-weight: 700; letter-spacing: 2px; color: #00F260; text-transform: uppercase;">Tactical Suite</div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# 3. Main Landing Layout
st.title("🤖 DrawPredict Tactical Suite")
st.markdown("### Welcome to the Production Hub")
st.write("Use the slide-out menu drawer on the left to navigate between real-time data engines and backtesters.")
st.markdown("---")

# Global Data Pipeline Status
col1, col2 = st.columns(2)
with col1:
    st.info("📊 **Global Ingestion Status:** Core Historical Records Synchronized.")
with col2:
    st.success("🔥 **Automation:** Engaged and isolated across modern timelines.")
