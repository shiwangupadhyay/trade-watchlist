import streamlit as st
import pandas as pd
import datetime
import base64

# Load the securities data
securities_df = pd.read_csv('securitiesData.csv')

# Initialize session state for trades
if 'trades' not in st.session_state:
    st.session_state['trades'] = []

def calculate_metrics(entry_price, target_price, date_added):
    target_returns = ((target_price - entry_price) / entry_price) * 100
    trading_days_elapsed = (datetime.datetime.now() - datetime.datetime.combine(date_added, datetime.datetime.min.time())).days
    return target_returns, trading_days_elapsed

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load custom CSS for styling
local_css("style.css")

# Sidebar for adding a new trade
st.sidebar.header('Add New Trade')
with st.sidebar.form(key='add_trade_form'):
    security = st.selectbox('Security', securities_df['Company Name'])
    entry_price = st.number_input('Entry Price', min_value=0.0, format="%.2f")
    quantity = st.number_input('Quantity', min_value=1, step=1)
    date_added = st.date_input('Date Added', datetime.date.today())
    target_price = st.number_input('Target Price', min_value=0.0, format="%.2f")
    notes = st.text_area('Notes')
    submit_button = st.form_submit_button(label='Add Trade')

# Add trade to session state
if submit_button:
    target_returns, trading_days_elapsed = calculate_metrics(entry_price, target_price, date_added)
    trade = {
        'security': security,
        'entry_price': entry_price,
        'quantity': quantity,
        'date_added': date_added,
        'target_price': target_price,
        'target_returns': target_returns,
        'trading_days_elapsed': trading_days_elapsed,
        'notes': notes
    }
    st.session_state.trades.append(trade)
    st.success('Trade added successfully!')

# Function to generate a downloadable CSV link
def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="trades.csv">Download CSV</a>'
    return href



# Callback for deleting a trade
def delete_trade(idx):
    if st.session_state.trades and idx < len(st.session_state.trades):
        st.session_state.trades.pop(idx)

# Header for the watchlist
st.header('Your Trade Watchlist')

# Display each trade in a styled card
for idx, trade in enumerate(st.session_state.trades):
    with st.expander(f"{trade['security']} (ID: {idx})"):
        st.markdown(f"""
            <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <p><strong>Entry Price:</strong> ${trade['entry_price']:.2f}</p>
                <p><strong>Quantity:</strong> {trade['quantity']}</p>
                <p><strong>Date Added:</strong> {trade['date_added'].strftime('%Y-%m-%d')}</p>
                <p><strong>Target Price:</strong> ${trade['target_price']:.2f}</p>
                <p><strong>Target Returns:</strong> {trade['target_returns']:.2f}%</p>
                <p><strong>Trading Days Elapsed:</strong> {trade['trading_days_elapsed']}</p>
                <p><strong>Notes:</strong> {trade['notes']}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button(f"Delete Trade {idx}", key=f"delete_{idx}"):
            delete_trade(idx)
            st.experimental_rerun()

# Export trades to CSV
if st.button('Export to CSV'):
    trades_df = pd.DataFrame(st.session_state.trades)
    st.markdown(get_table_download_link(trades_df), unsafe_allow_html=True)
    st.success('Trades exported successfully!')