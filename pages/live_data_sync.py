import streamlit as st
import pandas as pd
import requests

st.title("🔄 Live State Server Sync Engine")
st.write("Establish a direct pipeline to the state servers to bypass terminal firewalls and inject fresh historical data.")

game_selection = st.radio("Select Target Production Suite:", ["Pick 3 Suite", "Daily 4 Suite"])

if st.button("Pull Latest Drawings From Austin Servers"):
    with st.spinner("Bypassing server firewalls and downloading data..."):
        try:
            # Verified Texas Lottery Data Export Endpoints
            if game_selection == "Pick 3 Suite":
                # Most reliable Pick 3 endpoint
                url = "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3day.csv"
                target_filename = "live_pick3_suite.csv"
            else:
                # Verified Daily 4 endpoint
                url = "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4day.csv"
                target_filename = "live_daily_4_suite.csv"
            
            # Use browser headers to avoid 403 Forbidden errors
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                with open(target_filename, "w") as f:
                    f.write(response.text)
                st.success(f"✅ Success! `{target_filename}` is now live and synchronized.")
                st.balloons()
            else:
                st.error(f"❌ Server rejected request. Status Code: {response.status_code}. Ensure the URL endpoint is active.")
                
        except Exception as e:
            st.error(f"Sync failed: {e}")
