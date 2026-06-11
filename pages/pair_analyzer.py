import streamlit as st
import pandas as pd
import glob
from collections import Counter

st.title("👥 Pair Frequency Analyzer")
st.write("Track repeating two-digit combinations to identify high-probability betting pairs.")

csv_files = glob.glob("*.csv")

if not csv_files:
    st.warning("Please make sure your lottery CSV files are in the folder.")
else:
    selected_file = st.selectbox("Select Target File:", csv_files)
    
    try:
        df = pd.read_csv(selected_file, header=None)
        total_rows = len(df)
        
        # Identify game layout and setup pair positions
        if len(df.columns) >= 8:
            is_daily4 = True
            st.info(f"Daily 4 Mode: Analyzing pairs across {total_rows:,} records.")
            pair_options = {
                "Front Pair (Digit 1 & 2)": (4, 5),
                "Middle Pair (Digit 2 & 3)": (5, 6),
                "Back Pair (Digit 3 & 4)": (6, 7)
            }
        else:
            is_daily4 = False
            st.info(f"Pick 3 Mode: Analyzing pairs across {total_rows:,} records.")
            pair_options = {
                "Front Pair (Digit 1 & 2)": (4, 5),
                "Back Pair (Digit 2 & 3)": (5, 6),
                "Split Pair (Digit 1 & 3)": (4, 6)
            }
            
        selected_pair_type = st.radio("Choose Pair Position to Analyze:", list(pair_options.keys()))
        pos1, pos2 = pair_options[selected_pair_type]
        
        # Calculate pair combinations
        pair_list = []
        for idx, row in df.iterrows():
            val1 = str(row[pos1]).strip()
            val2 = str(row[pos2]).strip()
            
            # Ensure both values are valid individual digits
            if val1.isdigit() and val2.isdigit():
                pair_list.append(f"{val1}-{val2}")
                
        if pair_list:
            # Count and rank pair frequencies
            counts = Counter(pair_list)
            
            # Create data table
            pair_df = pd.DataFrame(counts.items(), columns=['Pair Combination', 'Times Drawn'])
            pair_df['Draw Percentage'] = ((pair_df['Times Drawn'] / len(pair_list)) * 100).round(2)
            pair_df = pair_df.sort_values(by='Times Drawn', ascending=False).reset_index(drop=True)
            
            # Format percentages
            pair_df['Draw Percentage'] = pair_df['Draw Percentage'].astype(str) + '%'
            
            # UI Layout
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.markdown(f"### 🏆 Top 15 Most Frequent Pairs (`{selected_pair_type}`)")
                st.dataframe(pair_df.head(15), use_container_width=True)
                
                st.markdown("### 📉 Least Frequent Pairs (Coldest)")
                st.dataframe(pair_df.tail(10), use_container_width=True)
                
            with col2:
                st.markdown("### 🔥 Hot Target")
                hottest_pair = pair_df.iloc[0]['Pair Combination']
                hottest_count = pair_df.iloc[0]['Times Drawn']
                st.metric(label="Hottest Active Pair", value=hottest_pair, delta=f"{hottest_count} total hits")
                
                st.markdown("---")
                st.markdown("💡 **Strategy Tip:** Many players look for pairs that have high historic lifetime frequencies but currently show high skip intervals in the *Gap Analyzer* to build out their plays.")
        else:
            st.error("Could not generate pairs. Please check your data values.")
            
    except Exception as e:
        st.error(f"Error calculating pair frequencies: {e}")
