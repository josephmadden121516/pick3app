import streamlit as st
import pandas as pd
import glob

st.title("🧩 Pattern Analyzer")
st.write("Calculate true digit frequency patterns across your historical data.")

csv_files = glob.glob("*.csv")

if not csv_files:
    st.warning("Please make sure your lottery CSV files are in the folder.")
else:
    selected_file = st.selectbox("Choose data file for pattern analysis:", csv_files)
    
    try:
        # Load file WITHOUT assuming the first row is a header
        df = pd.read_csv(selected_file, header=None)
        
        # Check if it's Daily 4 (usually 10 or 11 columns) or Pick 3 (fewer columns)
        total_cols = len(df.columns)
        st.info(f"Analyzing {len(df):,} total drawings from `{selected_file}`")
        
        if total_cols >= 8:
            # Daily 4 structure: Game, Month, Day, Year, Num1, Num2, Num3, Num4...
            digit_indices = [4, 5, 6, 7]
            st.markdown("**Targeting Daily 4 Winning Number Positions**")
        else:
            # Pick 3 structure: Game, Month, Day, Year, Num1, Num2, Num3...
            digit_indices = [4, 5, 6]
            st.markdown("**Targeting Pick 3 Winning Number Positions**")
            
        # Pull only the exact winning number columns
        winning_digits = df[digit_indices].values.flatten()
        
        # Clean data to keep only true digits 0-9
        winning_digits = [int(x) for x in winning_digits if pd.notna(x) and str(x).strip().isdigit()]
        
        if winning_digits:
            counts = pd.Series(winning_digits).value_counts().reindex(range(10), fill_value=0)
            
            freq_df = pd.DataFrame({
                'Digit': counts.index,
                'Times Drawn': counts.values,
                'Percentage': (counts.values / len(winning_digits) * 100).round(2)
            }).sort_values(by='Times Drawn', ascending=False)
            
            freq_df['Percentage'] = freq_df['Percentage'].astype(str) + '%'
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown("### 📊 Frequency Leaderboard")
                st.dataframe(freq_df.set_index('Digit'), use_container_width=True)
            
            with col2:
                st.markdown("### 🔥 Hot vs. ❄️ Cold Summary")
                hot_digit = freq_df.iloc[0]['Digit']
                cold_digit = freq_df.iloc[-1]['Digit']
                
                st.metric(label="🔥 Hottest Overall Digit", value=str(hot_digit), 
                          delta=f"{freq_df.iloc[0]['Times Drawn']} hits")
                st.metric(label="❄️ Coldest Overall Digit", value=str(cold_digit), 
                          delta=f"{freq_df.iloc[-1]['Times Drawn']} hits", delta_color="inverse")
        else:
            st.error("No valid numeric lottery numbers found in those positions.")
            
    except Exception as e:
        st.error(f"Error executing pattern analysis: {e}")
