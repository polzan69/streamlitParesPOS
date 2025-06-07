# app.py
import streamlit as st
from firebase_utils import init_firebase, add_sale
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Migz Paresan POS",
    page_icon="🍔",
    layout="centered"
)

# --- Firebase Initialization ---
# Initialize the Firebase app and get the Firestore client.
db = init_firebase()

# --- Menu Definition ---
# A dictionary to hold the menu items and their prices.
MENU_ITEMS = {
    "Pares Plain (PHP 50)": 50,
    "Pares /w Rice (PHP 65)": 65,
    "Pares /w Egg & Rice (PHP 80)": 80,
    "Add-ons: Egg (PHP 15)": 15,
    "Add-ons: Rice (PHP 15)": 15,
    "Add-ons: Half-rice (PHP 10)": 10,
    "Add-ons: Drinks (PHP 20)": 20,
}

# --- Session State Initialization ---
# Initialize the shopping cart in Streamlit's session state if it doesn't exist.
# This ensures the cart persists across reruns.
if 'cart' not in st.session_state:
    st.session_state.cart = {}

# --- Helper Functions ---
def add_to_cart(item):
    """Increments the quantity of an item in the cart."""
    st.session_state.cart[item] = st.session_state.cart.get(item, 0) + 1

def reset_cart():
    """Clears all items from the cart."""
    st.session_state.cart = {}

# --- Main Application UI ---
st.title("🍔 Migz Paresan POS")
st.markdown("Click on the items to add them to the current order.")

# --- Item Buttons ---
# Create columns for a cleaner layout of item buttons.
cols = st.columns(len(MENU_ITEMS))
for i, (item, price) in enumerate(MENU_ITEMS.items()):
    with cols[i]:
        if st.button(item, use_container_width=True):
            add_to_cart(item)

st.divider()

# --- Current Order Display ---
st.header("Current Order")

if not st.session_state.cart:
    st.info("Cart is empty. Add items to get started.")
else:
    total_price = 0
    # Display each item in the cart.
    for item, quantity in st.session_state.cart.items():
        price = MENU_ITEMS[item]
        subtotal = price * quantity
        total_price += subtotal
        
        st.write(f"- **{item}** `x {quantity}`: PHP {subtotal:,.2f}")
    
    st.markdown(f"### **Total: PHP {total_price:,.2f}**")

    st.divider()

    # --- Action Buttons ---
    # Create columns for the "Proceed" and "Reset" buttons.
    action_cols = st.columns(2)
    
    with action_cols[0]:
        if st.button("✅ Proceed with Sale", use_container_width=True, type="primary"):
            if db:
                sale_data = {
                    "items": st.session_state.cart,
                    "total_price": total_price
                }
                add_sale(db, sale_data)
                st.toast("✅ Sale successful!", icon="🎉")
                time.sleep(2) # A short delay to let the user see the toast
                reset_cart()
                st.rerun() # Rerun the app to reflect the cleared cart
            else:
                st.error("Database connection not available. Cannot proceed with sale.")

    with action_cols[1]:
        if st.button("🔄 Reset Order", use_container_width=True):
            reset_cart()
            st.rerun()
