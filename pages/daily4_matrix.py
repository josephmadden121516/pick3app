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
    # Option 1: Seamlessly toggle between live master files and historical fragments
    selected_file = st.selectbox("Select Daily 4 Data Stream:", sorted(daily4_files))
    
    try:
        df = pd.read_csv(selected_file, header=None)
        total_rows = len(df)
        
        # Dynamically map digit offsets based on column counts (handling fireball offsets)
        if len(df.columns) >= 9:
            digit_cols = [4, 5, 6, 7] # standard layout with fireball
        else:
            digit_cols = [4, 5, 6, 7] # fallback default layout
            
        st.info(f"Analyzing {total_rows:,} drawings from `{selected_file}`.")
        
        # Pattern classifications containers
        box_types = []
        digit_distribution = {i: [0, 0, 0, 0] for i in range(10)} # Positional tracks
        
        matrix = df[digit_cols].dropna().astype(int).values
        
        for row in matrix:
            # Track digit position frequencies
            for pos_idx, digit in enumerate(row):
                if 0 <= digit <= 9:
                    digit_distribution[digit][pos_idx] += 1
            
            # Categorize the combination layout (Box Bet classifications)
            counts = Counter(row)
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
        st.write("Track which mechanical configurations hit most often to optimize your strategy selections.")
        
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
        st.write("Track exact historical frequency weights for each individual position (1st digit through 4th digit).")
        
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
            hottest_structure = box_df.iloc[0]['Combination Structure']
            st.metric(label="Dominant Layout", value=hottest_structure.split("(")[0].strip())
        with col2:
            hottest_digit = matrix_df.iloc[0]['Digit']
            hottest_digit_count = matrix_df.iloc[0]['Total Lifetime Hits']
            st.metric(label="Overall Hottest Digit", value=f" Digit {hottest_digit}", delta=f"{hottest_digit_count} hits")

    except Exception as e:
        st.error(f"Error parsing Daily 4 structural data streams: {e}")
