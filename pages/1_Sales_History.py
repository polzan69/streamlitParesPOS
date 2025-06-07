# pages/1_Sales_History.py
import streamlit as st
from firebase_utils import init_firebase, get_all_sales, delete_sale, get_ph_time
import pandas as pd
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Sales History",
    page_icon="📈",
    layout="wide"
)

# --- Firebase Initialization ---
db = init_firebase()

# --- Session State Initialization ---
# Used to manage the confirmation state for deleting a sale.
if 'confirm_delete_id' not in st.session_state:
    st.session_state.confirm_delete_id = None

# --- Helper Functions ---
def get_today_sales(all_sales):
    """Filters sales to include only those from the current day in PH time."""
    today = get_ph_time().date()
    today_sales = []
    for sale in all_sales:
        # Firebase timestamp needs to be converted to a timezone-aware datetime object
        sale_time = sale.get('timestamp')
        if sale_time:
            sale_date = sale_time.astimezone(get_ph_time().tzinfo).date()
            if sale_date == today:
                today_sales.append(sale)
    return today_sales

def sales_to_excel(sales_data):
    """Converts a list of sales data into an Excel file in memory."""
    if not sales_data:
        return None
    
    # Flatten the data for the Excel sheet
    records = []
    for sale in sales_data:
        sale_time = sale['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        for item, quantity in sale['items'].items():
            records.append({
                "Sale ID": sale['id'],
                "Timestamp": sale_time,
                "Item": item,
                "Quantity": quantity,
                "Total Sale Price": sale['total_price']
            })
            
    df = pd.DataFrame(records)
    
    # Create an in-memory Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sales')
    
    processed_data = output.getvalue()
    return processed_data


# --- Main Application UI ---
st.title("📈 Sales History & Reporting")

if not db:
    st.stop() # Stop execution if DB connection fails

all_sales = get_all_sales(db)
grand_total = sum(sale['total_price'] for sale in all_sales)

# --- Metrics Display ---
st.metric(label="**Total Revenue**", value=f"PHP {grand_total:,.2f}")
st.divider()


# --- Reporting Section ---
st.header("Generate End of Day Report")
today_sales = get_today_sales(all_sales)

if not today_sales:
    st.info("No sales recorded yet for today.")
else:
    excel_data = sales_to_excel(today_sales)
    if excel_data:
        st.download_button(
            label="📥 Download Today's Sales (.xlsx)",
            data=excel_data,
            file_name=f"sales_report_{get_ph_time().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.divider()

# --- All Sales Display ---
st.header("All Sales Records")

if not all_sales:
    st.info("No sales have been recorded yet.")
else:
    for sale in all_sales:
        sale_id = sale['id']
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Display sale timestamp and total
                sale_time = sale.get('timestamp')
                time_str = sale_time.strftime("%B %d, %Y - %I:%M %p") if sale_time else "No timestamp"
                st.subheader(f"Sale on {time_str}")
                st.write(f"**Total:** PHP {sale['total_price']:,.2f}")

                # Display items in the sale
                for item, qty in sale['items'].items():
                    st.text(f"  - {item}: {qty}")
            
            with col2:
                # Delete button and confirmation logic
                if st.session_state.confirm_delete_id == sale_id:
                    st.warning("Delete this sale?")
                    if st.button("✅ Yes, Delete", key=f"confirm_{sale_id}", use_container_width=True):
                        delete_sale(db, sale_id)
                        st.session_state.confirm_delete_id = None
                        st.rerun()
                    if st.button("❌ No, Cancel", key=f"cancel_{sale_id}", use_container_width=True):
                        st.session_state.confirm_delete_id = None
                        st.rerun()
                else:
                    if st.button("🗑️ Delete", key=f"delete_{sale_id}", use_container_width=True):
                        st.session_state.confirm_delete_id = sale_id
                        st.rerun()

