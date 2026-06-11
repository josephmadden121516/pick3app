import streamlit as st
import pandas as pd
import glob
from collections import Counter

st.title("🏛️ Lotto Texas 6-Number Analyzer")
st.write("Strategic matrices specifically designed for 6-from-54 jackpot matrix structures (Lotto Texas).")

# Filter files specific to Lotto Texas historical data
# Ensure your CSV filename contains 'lottotexas' or 'lotto_texas'
csv_files = glob.glob("*.csv")
lotto_tx_files = [f for f in csv_files if "lottotexas" in f.lower() or "lotto_texas" in f.lower()]

if not lotto_tx_files:
    st.warning("No Lotto Texas data detected. Upload 'lottotexas.csv' to analyze the 6/54 game.")
else:
    selected_file = st.selectbox("Select Data Source:", lotto_tx_files)
    
    try:
        df = pd.read_csv(selected_file, header=None)
        total_rows = len(df)
        
        # 1. Identify 6 winning number columns (adjust indices based on your CSV format)
        # Assuming standard format: Year, Month, Day, Draw #, [N1, N2, N3, N4, N5, N6]
        # Common state files have numbers on 4, 5, 6, 7, 8, 9
        digit_cols = [4, 5, 6, 7, 8, 9] 
        st.info(f"Analyzing {total_rows:,} historical drawings.")
        
        all_drawings = df[digit_cols].dropna().astype(int).values
        
        # 2. Generate Frequency Map
        flat_list = all_drawings.flatten()
        freq_counts = Counter(flat_list)
        
        # Convert to sorted DataFrame
        freq_df = pd.DataFrame.from_dict(freq_counts, orient='index', columns=['Frequency']).sort_index()
        freq_df.index.name = 'Number'
        
        # 3. Calculate "Gap" (Skip interval / Overdue Draws)
        # Track when each number (1-54) last hit (row index). 0 = most recent draw.
        overdue_tracker = {i: "Never Hit" for i in range(1, 55)}
        
        # We process chronologically bottom to top (like previous pages)
        # We need row indices, so iterate normally from 0 (most recent) to len(all_drawings) (oldest)
        for row_idx, row in enumerate(all_drawings):
            for number in row:
                if isinstance(overdue_tracker[number], str) and overdue_tracker[number] == "Never Hit":
                    overdue_tracker[number] = row_idx
        
        gap_df = pd.DataFrame.from_dict(overdue_tracker, orient='index', columns=['Draws Overdue']).sort_index()
        gap_df.index.name = 'Number'
        
        # 4. Merging and displaying matrix
        combined_matrix = pd.merge(freq_df, gap_df, left_index=True, right_index=True).sort_values(by='Draws Overdue', ascending=False)
        combined_matrix = combined_matrix.reset_index()
        
        # Displays the strategic scorecard
        st.markdown("### 🏆 Numerical Skip/Hit Matrix (1-54 Field)")
        st.write("Analyze frequency versus current overdue streaks. High Overdue values indicate 'Cold' numbers.")
        st.dataframe(combined_matrix, use_container_width=True)
        
        # Strategic Cards
        st.markdown("---")
        coldest_number = combined_matrix.iloc[0]['Number']
        coldest_gap = combined_matrix.iloc[0]['Draws Overdue']
        
        st.metric(label="📊 Overdue Cold Number", value=f"Number {coldest_number}", delta=f"{coldest_gap} Draws Missed", delta_color="inverse")
        
    except Exception as e:
        st.error(f"Error parsing Lotto Texas 6/54 data: {e}")
