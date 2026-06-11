import streamlit as st
import pandas as pd
import glob
from collections import Counter

st.title("🎲 Daily 4 Tactical Matrix")
st.write("Analyze structural classifications, box combinations, and positional trends specifically for Daily 4.")

# Automatically discover all files, prioritizing the live suite we just built
csv_files = glob.glob("*.csv")
daily4_files = [f for f in csv_files if "daily4" in f.lower() or "daily_4" in f.lower()]

if not daily4_files:
    st.warning("No Daily 4 data sources detected. Run the Live State Server Sync Engine to generate real-time files.")
else:
    selected_file = st.selectbox("Select Daily 4 Data Stream:", sorted(daily4_files))
    
    try:
        # Load file safely skipping broken rows to isolate HTML error pages
        df = pd.read_csv(selected_file, header=None, on_bad_lines='skip')
        
        # Verify that the file actually contains structural multi-column lottery rows
        valid_rows = []
        for idx, row in df.iterrows():
            row_list = row.dropna().tolist()
            if len(row_list) >= 7:
                valid_rows.append(row_list)
                
        if not valid_rows:
            st.error(f"❌ `{selected_file}` does not contain valid lottery data rows. This happens if a server firewall blocks a terminal download. Please use the **Live State Server Sync Engine** page to compile a fresh data stream.")
        else:
            clean_df = pd.DataFrame(valid_rows)
            total_rows = len(clean_df)
            
            # Map coordinates dynamically based on incoming file structure
            if clean_df.shape[1] >= 8:
                digit_cols = [4, 5, 6, 7]
            else:
                digit_cols = list(range(clean_df.shape[1]-4, clean_df.shape[1]))
                
            st.info(f"Analyzing {total_rows:,} valid drawings from `{selected_file}`.")
            
            # Pattern classifications containers
            box_types = []
            digit_distribution = {i: [0, 0, 0, 0] for i in range(10)} 
            
            matrix = clean_df[digit_cols].astype(int).values
            
            for row in matrix:
                for pos_idx, digit in enumerate(row[:4]):
                    if 0 <= digit <= 9:
                        digit_distribution[digit][pos_idx] += 1
                
                counts = Counter(row[:4])
                unique_counts = sorted(list(counts.values()), reverse=True)
                
                if unique_counts == [1, 1, 1, 1]:
                    box_types.append("Single (24-Way Box / ABCD)")
                elif unique_counts == [2, 1, 1]:
                    box_types.append("Single Pair (12-Way Box / AABC)")
                elif unique_counts == [2, 2]:
                    box_types.append("Double-Double (6-Way Box / AABB)")
                elif unique_counts == [3, 1]:
                    box_types.append("Triple (4-Way Box / AAAB)")
                elif unique_counts == [4]:
                    box_types.append("Quad (1-Way Straight Only / AAAA)")

            # 1. Box Structural Types Summary
            st.markdown("### 📐 Combination Distribution & Box Strengths")
            box_counts = pd.Series(box_types).value_counts()
            box_df = pd.DataFrame({
                'Combination Structure': box_counts.index,
                'Total Hits': box_counts.values,
                'Historical Hit %': ((box_counts.values / len(box_types)) * 100).round(2)
            })
            box_df['Historical Hit %'] = box_df['Historical Hit %'].astype(str) + "%"
            st.dataframe(box_df, use_container_width=True)
            
            # 2. Positional Heat Map Matrix
            st.markdown("---")
            st.markdown("### 🔥 Positional Heat Map Matrix")
            matrix_data = []
            for digit in range(10):
                matrix_data.append({
                    'Digit': str(digit),
                    'Pos 1 (Front)': digit_distribution[digit][0],
                    'Pos 2 (Mid-Front)': digit_distribution[digit][1],
                    'Pos 3 (Mid-Back)': digit_distribution[digit][2],
                    'Pos 4 (Back)': digit_distribution[digit][3],
                    'Total Lifetime Hits': sum(digit_distribution[digit])
                })
                
            matrix_df = pd.DataFrame(matrix_data).sort_values(by='Total Lifetime Hits', ascending=False).reset_index(drop=True)
            st.dataframe(matrix_df, use_container_width=True)
            
            # 3. Tactical Strategy Card
            st.markdown("---")
            st.markdown("### 💡 Daily 4 Strategy Insight")
            col1, col2 = st.columns(2)
            with col1:
                if not box_df.empty:
                    st.metric(label="Dominant Layout", value=box_df.iloc[0]['Combination Structure'].split("(")[0].strip())
            with col2:
                if not matrix_df.empty:
                    st.metric(label="Overall Hottest Digit", value=f" Digit {matrix_df.iloc[0]['Digit']}", delta=f"{matrix_df.iloc[0]['Total Lifetime Hits']} hits")

    except Exception as e:
        st.error(f"Error parsing Daily 4 structural data streams: {e}")
