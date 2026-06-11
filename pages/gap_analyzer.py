import streamlit as st
import pandas as pd
import glob

st.title("⏳ Gap Analyzer (Skip Tracking)")
st.write("Track the exact number of drawings that have passed since each digit last appeared.")

csv_files = glob.glob("*.csv")

if not csv_files:
    st.warning("Please make sure your lottery CSV files are in the folder.")
else:
    selected_file = st.selectbox("Choose data file for gap analysis:", csv_files)
    
    try:
        # Load raw data
        df = pd.read_csv(selected_file, header=None)
        total_rows = len(df)
        
        # Determine game style layout
        if len(df.columns) >= 8:
            digit_cols = [4, 5, 6, 7]
            col_labels = ["Digit 1", "Digit 2", "Digit 3", "Digit 4"]
            st.info(f"Loaded Daily 4 Data: {total_rows:,} drawings.")
        else:
            digit_cols = [4, 5, 6]
            col_labels = ["Digit 1", "Digit 2", "Digit 3"]
            st.info(f"Loaded Pick 3 Data: {total_rows:,} drawings.")
            
        # Add a view selector: Global vs Position Specific
        analysis_type = st.radio("Analysis Mode:", ["Global (Any Position)", "By Specific Position"])
        
        # We assume the CSV is ordered chronologically from top (oldest) to bottom (newest).
        # To find the current gap, we scan backward from the latest drawing (the last row).
        
        gaps = {}
        
        if analysis_type == "Global (Any Position)":
            st.markdown("### Current Gaps across All Combined Positions")
            st.write("How many drawings have passed since the digit appeared *anywhere* in the winning combo?")
            
            # Loop through digits 0-9
            for digit in range(10):
                gap_count = 0
                found = False
                # Scan from bottom of dataframe to top
                for idx in range(total_rows - 1, -1, -1):
                    row_digits = df.iloc[idx, digit_cols].values
                    # Clean values to integers
                    row_digits = [int(x) for x in row_digits if pd.notna(x) and str(x).strip().isdigit()]
                    
                    if digit in row_digits:
                        found = True
                        break
                    gap_count += 1
                gaps[digit] = gap_count if found else total_rows
                
            # Display Result Table
            gap_df = pd.DataFrame({
                'Digit': gaps.keys(),
                'Current Skip (Drawings)': gaps.values()
            }).sort_values(by='Current Skip (Drawings)', ascending=False)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.dataframe(gap_df.set_index('Digit'), use_container_width=True)
            with col2:
                most_overdue = gap_df.iloc[0]['Digit']
                max_gap = gap_df.iloc[0]['Current Skip (Drawings)']
                st.metric(label="🚨 Most Overdue Global Digit", value=f"Digit {most_overdue}", delta=f"Skipped {max_gap} games")

        else:
            selected_pos_label = st.selectbox("Select Position to Analyze:", col_labels)
            target_col_idx = digit_cols[col_labels.index(selected_pos_label)]
            
            st.markdown(f"### Current Gaps for `{selected_pos_label}` Only")
            
            for digit in range(10):
                gap_count = 0
                found = False
                for idx in range(total_rows - 1, -1, -1):
                    val = df.iloc[idx, target_col_idx]
                    if pd.notna(val) and str(val).strip().isdigit() and int(val) == digit:
                        found = True
                        break
                    gap_count += 1
                gaps[digit] = gap_count if found else total_rows
                
            gap_df = pd.DataFrame({
                'Digit': gaps.keys(),
                'Current Skip (Drawings)': gaps.values()
            }).sort_values(by='Current Skip (Drawings)', ascending=False)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.dataframe(gap_df.set_index('Digit'), use_container_width=True)
            with col2:
                most_overdue = gap_df.iloc[0]['Digit']
                max_gap = gap_df.iloc[0]['Current Skip (Drawings)']
                st.metric(label=f"🚨 Most Overdue in {selected_pos_label}", value=f"Digit {most_overdue}", delta=f"Skipped {max_gap} games")
                
    except Exception as e:
        st.error(f"Error executing gap analysis: {e}")
