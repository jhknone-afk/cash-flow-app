import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(layout="wide", page_title="Advanced Cash Flow Manager")

# Exchange Rates
USD_TO_INR = 95.25
INR_TO_UGX = 38.84

st.sidebar.header("📂 1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Tally/Excel Export (CSV or XLSX)", type=["csv", "xlsx"])

st.sidebar.header("🛠️ 2. Scenario Planning")
delay_days = st.sidebar.slider("Delay Receivables By (Days):", 0, 90, 0)

st.title("Export Operations Cash Flow Dashboard")

# Global Currency Toggle
st.markdown("### Select Dashboard Currency")
currency = st.radio("Display Currency:", ('INR', 'USD', 'UGX Proxy'), horizontal=True)

# Function to format currency
def format_curr(val):
    if currency == 'USD': return f"$ {val/USD_TO_INR:,.2f}"
    elif currency == 'UGX Proxy': return f"UGX {val*INR_TO_UGX:,.0f}"
    return f"₹ {val:,.2f}"

# Fallback Data if nothing is uploaded
if uploaded_file is None:
    st.info("No file uploaded. Showing default forecast data.")
    data = [
        {"Date": "2026-10-15", "Entity": "Pixel Foil PI 001", "Commodity": "Alu Strip Foil", "Buyer_Supplier": "Supplier", "Mode": "AIR", "Category": "Raw Materials", "Amount_INR": -1643842, "Type": "Outflow"},
        {"Date": "2026-10-15", "Entity": "Pixel 1 Freight", "Commodity": "Logistics", "Buyer_Supplier": "Vendor", "Mode": "AIR", "Category": "Logistics", "Amount_INR": -2336800, "Type": "Outflow"},
        {"Date": "2026-10-31", "Entity": "MR Eng (Cont 2-4)", "Commodity": "PVC Film", "Buyer_Supplier": "Supplier", "Mode": "FCL", "Category": "Raw Materials", "Amount_INR": -10331185, "Type": "Outflow"},
        {"Date": "2026-10-31", "Entity": "Pixel Foil PI 002", "Commodity": "Alu Strip Foil", "Buyer_Supplier": "Supplier", "Mode": "FCL", "Category": "Raw Materials", "Amount_INR": -2639187, "Type": "Outflow"},
        {"Date": "2026-10-31", "Entity": "Sai Ram Foil PI 003", "Commodity": "Alu Blister Foil", "Buyer_Supplier": "Supplier", "Mode": "FCL", "Category": "Raw Materials", "Amount_INR": -2856754, "Type": "Outflow"},
        {"Date": "2026-10-31", "Entity": "FCL Freight (AJPPL)", "Commodity": "Logistics", "Buyer_Supplier": "Vendor", "Mode": "FCL (1x40)", "Category": "Logistics", "Amount_INR": -381000, "Type": "Outflow"},
        {"Date": "2026-12-15", "Entity": "NBG Machinery Bal", "Commodity": "Paper Bag Machine", "Buyer_Supplier": "NBG", "Mode": "N/A", "Category": "Capital Exp", "Amount_INR": -13600000, "Type": "Outflow"},
        {"Date": "2026-12-15", "Entity": "NBG Freight", "Commodity": "Logistics", "Buyer_Supplier": "Vendor", "Mode": "FCL (4x40)", "Category": "Logistics", "Amount_INR": -1905000, "Type": "Outflow"},
        {"Date": "2027-04-10", "Entity": "KPI API CIPROX", "Commodity": "Ciprofloxacin API", "Buyer_Supplier": "KPIL", "Mode": "AIR", "Category": "Receivable", "Amount_INR": 4686300, "Type": "Inflow"},
        {"Date": "2027-04-15", "Entity": "KPIL (Container 1)", "Commodity": "PVC Film", "Buyer_Supplier": "KPIL", "Mode": "FCL", "Category": "Receivable", "Amount_INR": 8813486, "Type": "Inflow"},
        {"Date": "2027-04-15", "Entity": "AJPPL (Pixel 1)", "Commodity": "Alu Strip Foil", "Buyer_Supplier": "AJPPL", "Mode": "AIR", "Category": "Receivable", "Amount_INR": 5549824, "Type": "Inflow"},
        {"Date": "2027-04-30", "Entity": "AJPPL (Pixel 2 + Sai)", "Commodity": "Alu Blister/Strip", "Buyer_Supplier": "AJPPL", "Mode": "FCL", "Category": "Receivable", "Amount_INR": 9751719, "Type": "Inflow"},
    ]
    # Recurring Expenses
    for month in range(10, 13):
        data.append({"Date": f"2026-{month:02d}-28", "Entity": "Monthly OpEx", "Commodity": "Rent/Salary", "Buyer_Supplier": "Internal", "Mode": "N/A", "Category": "OpEx", "Amount_INR": -200000, "Type": "Outflow"})
        data.append({"Date": f"2026-{month:02d}-28", "Entity": "OD Interest", "Commodity": "Finance", "Buyer_Supplier": "Saraswat Bank", "Mode": "N/A", "Category": "Finance", "Amount_INR": -200000, "Type": "Outflow"})
    for month in range(1, 6):
        data.append({"Date": f"2027-{month:02d}-28", "Entity": "Monthly OpEx", "Commodity": "Rent/Salary", "Buyer_Supplier": "Internal", "Mode": "N/A", "Category": "OpEx", "Amount_INR": -200000, "Type": "Outflow"})
        data.append({"Date": f"2027-{month:02d}-28", "Entity": "OD Interest", "Commodity": "Finance", "Buyer_Supplier": "Saraswat Bank", "Mode": "N/A", "Category": "Finance", "Amount_INR": -200000, "Type": "Outflow"})
    df = pd.DataFrame(data)
else:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# Ensure Dates are datetime and SORT ASCENDING
df['Date'] = pd.to_datetime(df['Date'])

# Apply Stress Test
if delay_days > 0:
    df.loc[df['Type'] == 'Inflow', 'Date'] += pd.to_timedelta(delay_days, unit='d')

df = df.sort_values(by='Date', ascending=True).reset_index(drop=True)

# Calculate Active Currency Column
if currency == 'USD':
    df['Display_Amount'] = df['Amount_INR'] / USD_TO_INR
elif currency == 'UGX Proxy':
    df['Display_Amount'] = df['Amount_INR'] * INR_TO_UGX
else:
    df['Display_Amount'] = df['Amount_INR']

df['Cumulative'] = df['Display_Amount'].cumsum()

# --- TOP METRICS ---
col1, col2, col3 = st.columns(3)
with col1: st.metric("Total Expected Receivables", format_curr(df[df['Type'] == 'Inflow']['Amount_INR'].sum()))
with col2: st.metric("Total Expected Payables", format_curr(abs(df[df['Type'] == 'Outflow']['Amount_INR'].sum())))
with col3: st.metric("Net Position (End of Period)", format_curr(df['Amount_INR'].sum()))

st.divider()

# --- COLOR CODED MONTHLY SUMMARY ---
st.subheader(f"🗓️ Month-wise Total ({currency})")
df['Month_Year'] = df['Date'].dt.strftime('%b %Y')
monthly_summary = df.groupby(df['Date'].dt.to_period('M')).agg(
    Month=('Month_Year', 'first'),
    Total_Inflow=('Display_Amount', lambda x: x[x > 0].sum()),
    Total_Outflow=('Display_Amount', lambda x: x[x < 0].sum()),
    Net_Cash_Needed_Or_Surplus=('Display_Amount', 'sum')
).reset_index(drop=True)

def color_net(val):
    color = '#d4edda' if val > 0 else '#f8d7da'
    text_color = '#155724' if val > 0 else '#721c24'
    return f'background-color: {color}; color: {text_color}; font-weight: bold;'

styled_monthly = monthly_summary.style.map(color_net, subset=['Net_Cash_Needed_Or_Surplus']) \
    .format({"Total_Inflow": "{:,.2f}", "Total_Outflow": "{:,.2f}", "Net_Cash_Needed_Or_Surplus": "{:,.2f}"})

st.dataframe(styled_monthly, use_container_width=True, hide_index=True)

st.divider()

# --- THE CHART ---
st.subheader(f"📈 Cash Runway & Cumulative Position ({currency})")
fig = px.line(df, x='Date', y='Cumulative', markers=True)
fig.update_traces(hovertemplate='<b>Date</b>: %{x}<br><b>Balance</b>: %{y:,.0f}<extra></extra>')
fig.add_hline(y=0, line_dash="dash", line_color="red")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- DETAILED LEDGER & EXPORTS ---
st.subheader(f"🗃️ Detailed Transaction Ledger ({currency})")

def color_type(val):
    return 'color: green; font-weight:bold;' if val == 'Inflow' else 'color: red;'

display_cols = ['Date', 'Entity', 'Buyer_Supplier', 'Commodity', 'Mode', 'Type', 'Display_Amount']
# Handle uploaded files that might be missing the advanced columns
available_cols = [col for col in display_cols if col in df.columns]
display_df = df[available_cols].copy()
display_df['Date'] = display_df['Date'].dt.strftime('%d-%b-%Y')

styled_display = display_df.style.map(color_type, subset=['Type']).format({"Display_Amount": "{:,.2f}"})
st.dataframe(styled_display, use_container_width=True, hide_index=True)

# Export Buttons
st.markdown("### 📥 Export Data")
col_ex1, col_ex2 = st.columns([1, 10])

# CSV
csv = display_df.to_csv(index=False).encode('utf-8')
with col_ex1:
    st.download_button(label="Download CSV", data=csv, file_name="cash_flow_ledger.csv", mime="text/csv")

# Excel
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    display_df.to_excel(writer, sheet_name='Ledger', index=False)
    monthly_summary.to_excel(writer, sheet_name='Monthly Summary', index=False)
with col_ex2:
    st.download_button(label="Download Excel", data=buffer.getvalue(), file_name="cash_flow_ledger.xlsx", mime="application/vnd.ms-excel")
