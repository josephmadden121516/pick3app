import streamlit as st
import pandas as pd
import glob

st.title("🧮 Strategic Backtester Engine")
st.write("Simulate mechanical wagering rules across thousands of historical drawings to test performance metrics.")

csv_files = glob.glob("*.csv")

if not csv_files:
    st.warning("Please make sure your lottery CSV files are available.")
else:
    selected_file = st.selectbox("Select Historical Dataset:", sorted(csv_files), key="backtest_file")
    
    try:
        df = pd.read_csv(selected_file, header=None)
        total_draws = len(df)
        
        # Determine Game Type
        is_daily4 = "daily" in selected_file.lower()
        digit_cols = [4, 5, 6, 7] if is_daily4 else [4, 5, 6]
        game_label = "Daily 4" if is_daily4 else "Pick 3"
        
        st.info(f"Loaded {total_draws:,} historical drawings for {game_label}.")
        
        # Strategy Rules Setup UI
        st.markdown("### ⚙️ Define Strategy Rules")
        col1, col2 = st.columns(2)
        
        with col1:
            test_type = st.radio("Strategy Type:", ["Target Sum", "Target Single Digit"])
        
        with col2:
            if test_type == "Target Sum":
                max_sum = 36 if is_daily4 else 27
                target_value = st.number_input(f"Enter Target Sum (0-{max_sum}):", 0, max_sum, value=12)
            else:
                target_value = st.number_input("Enter Target Digit (0-9):", 0, 9, value=5)
                target_pos = st.selectbox("Target Position:", ["Any Position", "Position 1 (Front)", "Position 2", "Position 3", "Position 4"] if is_daily4 else ["Any Position", "Position 1 (Front)", "Position 2", "Position 3 (Back)"])

        # Simulated Payout Rules
        st.markdown("---")
        st.markdown("### 💰 Simulation Configuration")
        c1, c2 = st.columns(2)
        cost_per_play = c1.number_input("Cost per Play ($):", min_value=0.50, max_value=10.00, value=1.00, step=0.50)
        payout_amount = c2.number_input("Payout on Win ($):", min_value=1.00, max_value=5000.00, value=500.00 if not is_daily4 else 2500.00, step=50.00)

        if st.button("🚀 Execute Historical Backtest", use_container_width=True):
            matrix = df[digit_cols].fillna(0).astype(int).values
            
            total_spent = 0
            total_won = 0
            wins_count = 0
            
            current_dry_spell = 0
            max_dry_spell = 0
            
            # Run the simulation timeline chronologically (bottom of file to top)
            for row in reversed(matrix):
                total_spent += cost_per_play
                is_win = False
                
                if test_type == "Target Sum":
                    if sum(row) == target_value:
                        is_win = True
                else:
                    # Single digit check
                    if target_pos == "Any Position":
                        if target_value in row:
                            is_win = True
                    else:
                        # Extract exact positional coordinate
                        pos_map = {"Position 1 (Front)": 0, "Position 2": 1, "Position 3 (Back)": 2, "Position 3": 2, "Position 4": 3}
                        target_idx = pos_map.get(target_pos, 0)
                        if row[target_idx] == target_value:
                            is_win = True
                            
                if is_win:
                    wins_count += 1
                    total_won += payout_amount
                    if current_dry_spell > max_dry_spell:
                        max_dry_spell = current_dry_spell
                    current_dry_spell = 0
                else:
                    current_dry_spell += 1
            
            # Finalize trailing dry spell tracking
            if current_dry_spell > max_dry_spell:
                max_dry_spell = current_dry_spell
                
            net_profit = total_won - total_spent
            win_percentage = (wins_count / total_draws) * 100
            roi = (net_profit / total_spent) * 100 if total_spent > 0 else 0
            
            # Display Results Cards
            st.markdown("### 📊 Backtest Performance Overview")
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric("Total Wins / Plays", f"{wins_count:,} / {total_draws:,}", f"{win_percentage:.2f}% Win Rate")
            with metric_col2:
                st.metric("Net Profit / Loss", f"${net_profit:,.2f}", f"{roi:.2f}% ROI", delta_color="normal" if net_profit >= 0 else "inverse")
            with metric_col3:
                st.metric("Max Dry Spell", f"{max_dry_spell} Draws", "Longest Losing Streak", delta_color="inverse")
                
            # Strategic Verdict
            st.markdown("---")
            st.markdown("### 💡 Tactical Verdict")
            if net_profit > 0:
                st.success(f"📈 **Viable Strategy!** Over the tested timeline, this mechanical rule generated a net return of **${net_profit:,.2f}**. Keep an eye on the max dry spell of **{max_dry_spell}** draws to ensure your bankroll can survive the variance.")
            else:
                st.error(f"📉 **Negative Expectation.** This specific selection rule lost a net total of **${abs(net_profit):,.2f}**. The mathematical house edge or bad variance depleted the capital pool. Refine your parameters and try a different interval or combination threshold.")
                
    except Exception as e:
        st.error(f"Error executing backtest sequence: {e}")
