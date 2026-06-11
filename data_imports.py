import streamlit as st
import pandas as pd
import glob

st.title("📊 Data Import Engine")
st.write("Inspecting project folder files with standardized layouts...")

csv_files = glob.glob("*.csv")

if not csv_files:
    st.warning("No CSV files found.")
else:
    selected_file = st.selectbox("Select a file to inspect:", csv_files)
    
    if selected_file:
        st.markdown(f"### Previewing: `{selected_file}`")
        try:
            # Force pandas to read raw data without eating the first row
            df = pd.read_csv(selected_file, header=None)
            
            # Dynamically rename columns based on file type lengths
            if len(df.columns) >= 8:
                custom_headers = ["Game Style", "Month", "Day", "Year", "Digit 1", "Digit 2", "Digit 3", "Digit 4"]
                # Append placeholder names for any trailing columns like sum or fireball
                custom_headers += [f"Extra_{i}" for i in range(len(df.columns) - len(custom_headers))]
            else:
                custom_headers = ["Game Style", "Month", "Day", "Year", "Digit 1", "Digit 2", "Digit 3"]
                custom_headers += [f"Extra_{i}" for i in range(len(df.columns) - len(custom_headers))]
                
            df.columns = custom_headers
            
            st.metric(label="Total Drawing Records", value=f"{len(df):,}")
            st.dataframe(df.head(15), use_container_width=True)
        except Exception as e:
            st.error(f"Could not read file: {e}")
