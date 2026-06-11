import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.title("🔄 Live State Server Sync Engine")
st.write("Fetch and compile real-time drawing datasets straight from the Texas Lottery Bureau.")

# Official State Server Endpoint Directories
BASE_URLS = {
    "Pick 3 Morning": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3morning.csv",
    "Pick 3 Day": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3day.csv",
    "Pick 3 Evening": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3evening.csv",
    "Pick 3 Night": "https://www.texaslottery.com/export/sites/lottery/Games/Pick_3/Winning_Numbers/pick3night.csv",
    "Daily 4 Morning": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4morning.csv",
    "Daily 4 Day": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4day.csv",
    "Daily 4 Evening": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4evening.csv",
    "Daily 4 Night": "https://www.texaslottery.com/export/sites/lottery/Games/Daily_4/Winning_Numbers/daily4night.csv",
}

selected_game = st.radio("Select Target Data Stream:", ["Pick 3 Suite", "Daily 4 Suite"], horizontal=True)

if st.button("⚡ Pull Latest Drawings From Austin Servers", use_container_width=True):
    compiled_rows = []
    progress_bar = st.progress(0)
    
    # Filter endpoints based on user selection
    targets = {k: v for k, v in BASE_URLS.items() if (selected_game.split()[0] in k)}
    
    with st.spinner("Connecting to Texas Lottery network infrastructure..."):
        for idx, (stream_name, target_url) in enumerate(targets.items()):
            try:
                # Direct streaming text request to prevent memory buffering stalls
                response = requests.get(target_url, timeout=12)
                
                if response.status_code == 200:
                    # Break raw comma text lines down cleanly into pandas
                    lines = response.text.splitlines()
                    data_rows = [line.split(",") for line in lines if line.strip()]
                    
                    df_stream = pd.DataFrame(data_rows)
                    compiled_rows.append(df_stream)
                    st.toast(f"✅ Successfully synched {stream_name} file!")
                else:
                    st.error(f"Could not reach {stream_name} (Status code: {response.status_code})")
            except Exception as e:
                st.error(f"Error accessing {stream_name}: {e}")
            
            # Update physical UI tracking
            progress_bar.progress((idx + 1) / len(targets))
            
    if compiled_rows:
        # Merge all drawing times (Morning, Day, Evening, Night) together
        final_df = pd.concat(compiled_rows, ignore_index=True)
        
        # Format columns uniformly to mirror your database structure
        final_df.dropna(subset=[0], inplace=True)
        
        # Sort chronologically by converting Year (Col 3), Month (Col 1), Day (Col 2)
        try:
            final_df['Date'] = pd.to_datetime(final_df[3].astype(str) + '-' + final_df[1].astype(str) + '-' + final_df[2].astype(str), errors='coerce')
            final_df = final_df.sort_values(by='Date', ascending=False).drop(columns=['Date'])
        except:
            pass
            
        st.success(f"🎉 Synchronization Complete! Compiled {len(final_df):,} total historical records.")
        
        # Save a copy locally inside the temporary workspace for instant dashboard analytics
        filename = f"live_{selected_game.lower().replace(' ', '_')}.csv"
        final_df.to_csv(filename, index=False, header=False)
        
        # Display short overview preview panel
        st.markdown("### 🗺️ Recent Live Extraction Matrix")
        st.dataframe(final_df.head(10), use_container_width=True)
        st.info(f"Saved snapshot locally as `{filename}`. All other analytics pages can now select this file to scan real-time patterns!")
