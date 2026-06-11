import streamlit as st
import pandas as pd
import glob
from collections import Counter

st.title("🎲 Daily 4 Tactical Matrix")
st.write("Analyze structural classifications, box combinations, and positional trends specifically for Daily 4.")

csv_files = glob.glob("*.csv")
daily4_files = [f for f in csv_files if "daily4" in f.lower() or "daily_4" in f.lower()]

if not daily4_files:
    st.warning("No Daily 4 data sources detected. Run the Live State Server Sync Engine to generate real-time files.")
else:
    selected_file = st.selectbox("Select Daily 4 Data Stream:", sorted(daily4_files))
    try:
        df = pd.read_csv(selected_file, header=None, on_bad_lines='skip')
        valid_rows = []
        for idx, row in df.iterrows():
            row_list = row.dropna().tolist()
            if len(row_list) >= 7:
                valid_rows.append(row_list)
        if not valid_rows:
            st.error(f"❌ `{selected_file}` does not contain valid lottery data rows. Please use the Live State Server Sync Engine page.")
        else:
            clean_df = pd.DataFrame(valid_rows)
            if clean_df.shape[1] >= 8:
                digit_cols = [4, 5, 6, 7]
            else:
                digit_cols = list(range(clean_df.shape[1]-4, clean_df.shape[1]))
            st.info(f"Analyzing {len(clean_df):,} valid drawings.")
            box_types = []
            digit_distribution = {i: [0, 0, 0, 0] for i in range(10)}
            matrix = clean_df[digit_cols].astype(int).values
            for row in matrix:
                for pos_idx, digit in enumerate(row[:4]):
                    if 0 <= digit <= 9:
                        digit_distribution[digit][pos_idx] += 1
                counts = Counter(row[:4])
                unique_counts = sorted(list(counts.values()), reverse=True)
                if unique_counts == [1, 1, 1, 1]: box_types.append("Single (24-Way)")
                elif unique_counts == [2, 1, 1]: box_types.append("Single Pair (12-Way)")
                elif unique_counts == [2, 2]: box_types.append("Double-Double (6-Way)")
                elif unique_counts == [3, 1]: box_types.append("Triple (4-Way)")
                elif unique_counts == [4]: box_types.append("Quad (1-Way)")
            st.markdown("### 📐 Combination Distribution")
            box_counts = pd.Series(box_types).value_counts()
            st.dataframe(pd.DataFrame({'Structure': box_counts.index, 'Hits': box_counts.values}), use_container_width=True)
    except Exception as e:
        st.error(f"Error parsing data: {e}")
