import streamlit as st
import pandas as pd
import glob

st.title("🎯 Exact Combo Matcher")
st.write("Search the historical archive to see if a specific combination has ever won.")

csv_files = glob.glob("*.csv")

if not csv_files:
    st.warning("Please make sure your lottery CSV files are in the folder.")
else:
    selected_file = st.selectbox("Select Data Source:", csv_files)
    
    try:
        df = pd.read_csv(selected_file, header=None)
        
        # Determine Daily 4 vs Pick 3
        if len(df.columns) >= 8:
            is_daily4 = True
            digit_cols = [4, 5, 6, 7]
            st.info(f"Daily 4 Mode Active.")
        else:
            is_daily4 = False
            digit_cols = [4, 5, 6]
            st.info(f"Pick 3 Mode Active.")
            
        st.markdown("### Enter Your Combination")
        
        # Build input boxes side-by-side dynamically
        inputs = []
        cols = st.columns(len(digit_cols))
        for i, col in enumerate(cols):
            with col:
                num = st.number_input(f"Digit {i+1}", min_value=0, max_value=9, value=0, key=f"search_d{i}")
                inputs.append(num)
                
        search_combo = list(inputs)
        search_str = "-".join(map(str, search_combo))
        
        if st.button(f"🔍 Scan History for {search_str}"):
            # Extract just the numbers matrix
            matrix = df[digit_cols].fillna(0).astype(int).values
            
            straight_matches = []
            box_matches = []
            
            sorted_search = sorted(search_combo)
            
            for idx, row in enumerate(matrix):
                row_list = list(row)
                
                # Check Straight (Exact Order Match)
                if row_list == search_combo:
                    straight_matches.append(idx)
                # Check Box (Any Order Match)
                elif sorted(row_list) == sorted_search:
                    box_matches.append(idx)
                    
            # Display metrics
            st.markdown("---")
            c1, c2 = st.columns(2)
            c1.metric("Straight Hits (Exact)", len(straight_matches))
            c2.metric("Box Hits (Any Order)", len(box_matches))
            
            # Combine all matching index hits
            all_hit_indices = straight_matches + box_matches
            
            if all_hit_indices:
                st.success(f"Found match histories!")
                
                # Build a clean results dataframe
                results_raw = df.iloc[all_hit_indices].copy()
                
                # Reconstruct dates and winning numbers for layout
                summary_df = pd.DataFrame({
                    'Date': results_raw[1].astype(str) + "/" + results_raw[2].astype(str) + "/" + results_raw[3].astype(str),
                    'Winning Combo': results_raw[4].astype(str) + "-" + results_raw[5].astype(str) + "-" + results_raw[6].astype(str) + (("-" + results_raw[7].astype(str)) if is_daily4 else ""),
                    'Match Type': ["Straight (Exact)" if idx in straight_matches else "Box (Any Order)" for idx in results_raw.index]
                })
                
                st.dataframe(summary_df.set_index('Date'), use_container_width=True)
            else:
                st.subheader("Never Drawn")
                st.write("This exact combination has never appeared in this drawing style's history.")
                
    except Exception as e:
        st.error(f"Error executing combo search: {e}")
