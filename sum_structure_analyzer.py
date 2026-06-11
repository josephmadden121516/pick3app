import streamlit as st
import pandas as pd
import glob

st.title("📊 Sum & Structure Analyzer")
st.write("Analyze the mathematical weight and structural balance of historical drawings.")

csv_files = glob.glob("*.csv")

if not csv_files:
    st.warning("Please make sure your lottery CSV files are in the folder.")
else:
    selected_file = st.selectbox("Select Target File:", csv_files, key="struct_file")
    
    try:
        df = pd.read_csv(selected_file, header=None)
        total_rows = len(df)
        
        # Identify Pick 3 vs Daily 4
        if len(df.columns) >= 8:
            is_daily4 = True
            digit_cols = [4, 5, 6, 7]
            st.info(f"Daily 4 Mode Active: Analyzing {total_rows:,} drawings.")
        else:
            is_daily4 = False
            digit_cols = [4, 5, 6]
            st.info(f"Pick 3 Mode Active: Analyzing {total_rows:,} drawings.")
            
        # Lists to hold calculated stats
        sums = []
        root_sums = []
        hl_patterns = []
        oe_patterns = []
        
        # Process data matrix
        matrix = df[digit_cols].fillna(0).astype(int).values
        
        for row in matrix:
            # 1. Sum Calculation
            row_sum = sum(row)
            sums.append(row_sum)
            
            # 2. Root Sum Calculation (Digital Root)
            root = row_sum % 9
            if root == 0 and row_sum > 0:
                root = 9
            root_sums.append(root)
            
            # 3. High/Low Tracking (0-4 Low, 5-9 High)
            highs = sum(1 for d in row if d >= 5)
            lows = len(digit_cols) - highs
            hl_patterns.append(f"{highs}H-{lows}L")
            
            # 4. Odd/Even Tracking
            odds = sum(1 for d in row if d % 2 != 0)
            evens = len(digit_cols) - odds
            oe_patterns.append(f"{odds}O-{evens}E")
            
        # Aggregate Frequencies
        sum_counts = pd.Series(sums).value_counts().sort_index()
        root_counts = pd.Series(root_sums).value_counts().sort_index()
        hl_counts = pd.Series(hl_patterns).value_counts()
        oe_counts = pd.Series(oe_patterns).value_counts()
        
        # UI Layout: Tabs for cleaner organization
        tab1, tab2 = st.tabs(["🧮 Sums & Root Sums", "📐 Balanced Structure (H/L & O/E)"])
        
        with tab1:
            st.markdown("### 📈 Mathematical Sum Distributions")
            st.write("Lottery sums naturally cluster toward the center numbers due to a normal bell-curve distribution.")
            
            sum_df = pd.DataFrame({
                'Sum Total': sum_counts.index,
                'Times Drawn': sum_counts.values,
                'Percentage': ((sum_counts.values / total_rows) * 100).round(2)
            }).sort_values(by='Times Drawn', ascending=False).reset_index(drop=True)
            sum_df['Percentage'] = sum_df['Percentage'].astype(str) + "%"
            st.dataframe(sum_df.head(12), use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🧬 Root Sum Frequencies")
            st.write("Root sums collapse the total sum into a single structural digit (1-9).")
            
            root_df = pd.DataFrame({
                'Root Sum': root_counts.index,
                'Times Drawn': root_counts.values,
                'Percentage': ((root_counts.values / total_rows) * 100).round(2)
            }).sort_values(by='Times Drawn', ascending=False).reset_index(drop=True)
            root_df['Percentage'] = root_df['Percentage'].astype(str) + "%"
            st.dataframe(root_df, use_container_width=True)
            
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ☯️ High / Low Ratio")
                st.write("Shows the balance of High (5-9) vs Low (0-4) numbers.")
                hl_df = pd.DataFrame({
                    'Pattern': hl_counts.index,
                    'Times Drawn': hl_counts.values,
                    'Percentage': ((hl_counts.values / total_rows) * 100).round(2)
                })
                hl_df['Percentage'] = hl_df['Percentage'].astype(str) + "%"
                st.dataframe(hl_df, use_container_width=True)
                
            with col2:
                st.markdown("### 🔢 Odd / Even Ratio")
                st.write("Shows the balance of Odd vs Even numbers.")
                oe_df = pd.DataFrame({
                    'Pattern': oe_counts.index,
                    'Times Drawn': oe_counts.values,
                    'Percentage': ((oe_counts.values / total_rows) * 100).round(2)
                })
                oe_df['Percentage'] = oe_df['Percentage'].astype(str) + "%"
                st.dataframe(oe_df, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error compiling structural matrices: {e}")
