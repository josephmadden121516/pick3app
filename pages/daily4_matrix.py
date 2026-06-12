import streamlit as st
import pandas as pd
import glob
from collections import Counter
import itertools

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
            st.error(f"❌ `{selected_file}` does not contain valid lottery data rows.")
        else:
            clean_df = pd.DataFrame(valid_rows)
            if clean_df.shape[1] >= 8:
                digit_cols = [4, 5, 6, 7]
            else:
                digit_cols = list(range(clean_df.shape[1]-4, clean_df.shape[1]))
            
            st.info(f"Analyzing {len(clean_df):,} valid drawings.")
            
            # --- MATH PROCESSING ENGINE ---
            box_types = []
            digit_distribution = {i: [0, 0, 0, 0] for i in range(10)} # 10 digits, 4 positions
            matrix = clean_df[digit_cols].astype(int).values
            
            for row in matrix:
                # Track positional frequencies
                for pos_idx, digit in enumerate(row[:4]):
                    if 0 <= digit <= 9:
                        digit_distribution[digit][pos_idx] += 1
                
                # Categorize Box Structures
                counts = Counter(row[:4])
                unique_counts = sorted(list(counts.values()), reverse=True)
                if unique_counts == [1, 1, 1, 1]: box_types.append("Single (24-Way)")
                elif unique_counts == [2, 1, 1]: box_types.append("Single Pair (12-Way)")
                elif unique_counts == [2, 2]: box_types.append("Double-Double (6-Way)")
                elif unique_counts == [3, 1]: box_types.append("Triple (4-Way)")
                elif unique_counts == [4]: box_types.append("Quad (1-Way)")
            
            # Display Combination Metrics
            st.markdown("### 📐 Historical Combination Distribution")
            box_counts = pd.Series(box_types).value_counts()
            st.dataframe(pd.DataFrame({'Structure': box_counts.index, 'Hits': box_counts.values}), use_container_width=True)
            
            # --- NEW INTERACTIVE PLAY GENERATOR ENGINE ---
            st.markdown("---")
            st.markdown("### 🎯 Interactive Play Generator")
            st.write("Select your tactical filter strategy below to generate specific 4-digit numbers to play.")
            
            strategy = st.radio(
                "Choose Generation Strategy:",
                ["Positional Hot-Spot Injector", "Box Structure Filter"]
            )
            
            generated_numbers = []
            
            if strategy == "Positional Hot-Spot Injector":
                st.write("Extracting the top 3 mathematical 'hottest' digits for *each individual position* from your live file...")
                
                # Find top 3 digits for each of the 4 positions
                top_digits_per_pos = []
                for pos in range(4):
                    # Sort digits 0-9 by their count in this specific position
                    sorted_digits = sorted(range(10), key=lambda d: digit_distribution[d][pos], reverse=True)
                    top_digits_per_pos.append(sorted_digits[:3])
                    st.write(f"Position {pos+1} Hot Digits: **{sorted_digits[:3]}**")
                
                # Generate all permutations from these hot zones
                all_combos = list(itertools.product(*top_digits_per_pos))
                generated_numbers = ["".join(map(str, combo)) for combo in all_combos[:15]] # Limit to top 15 plays
                
            elif strategy == "Box Structure Filter":
                target_structure = st.selectbox("Select Target Play Structure:", box_counts.index)
                st.write(f"Isolating combinations that conform tightly to the **{target_structure}** archetype...")
                
                # Pull raw recent winning numbers that match this exact type to use as anchors
                matching_straights = []
                for row in matrix:
                    counts = Counter(row[:4])
                    unique_counts = sorted(list(counts.values()), reverse=True)
                    
                    current_struct = ""
                    if unique_counts == [1, 1, 1, 1]: current_struct = "Single (24-Way)"
                    elif unique_counts == [2, 1, 1]: current_struct = "Single Pair (12-Way)"
                    elif unique_counts == [2, 2]: current_struct = "Double-Double (6-Way)"
                    elif unique_counts == [3, 1]: current_struct = "Triple (4-Way)"
                    elif unique_counts == [4]: current_struct = "Quad (1-Way)"
                    
                    if current_struct == target_structure:
                        matching_straights.append("".join(map(str, row[:4])))
                
                # Display unique suggestions based on historical recurrence
                generated_numbers = list(set(matching_straights))[:12]
            
            # --- OUTPUT DELIVERABLE PANEL ---
            if generated_numbers:
                st.success(f"### 🔥 Target Tactical Plays ({len(generated_numbers)} Suggestions)")
                
                # Display nicely formatted large blocks for your phone screen
                cols = st.columns(4)
                for idx, num in enumerate(generated_numbers):
                    with cols[idx % 4]:
                        st.markdown(f"""
                        <div style="background-color:#1E293B; border-radius:10px; padding:15px; text-align:center; border: 2px solid #00F260; margin-bottom:10px;">
                            <span style="font-size:24px; font-weight:800; color:#00F260; letter-spacing:3px;">{num}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
    except Exception as e:
        st.error(f"Error parsing data: {e}")
       
