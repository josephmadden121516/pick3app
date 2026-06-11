import streamlit as st

st.set_page_config(page_title="Texas Lottery Dashboard", layout="wide")

st.title("🔥 Texas Lottery Strategy Dashboard")
st.markdown("---")

st.subheader("Welcome to the Analytical Suite")
st.write("Use the sidebar on the left to navigate between the data engines.")

col1, col2 = st.columns(2)
with col1:
    st.info("📊 **Data Status:** 25,751 historical records synchronized.")
with col2:
    st.success("🔥 **Fireball Engine:** Active and isolated to 728 modern drawings.")
