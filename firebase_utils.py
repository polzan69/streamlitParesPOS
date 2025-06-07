# firebase_utils.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import pytz

# --- Firebase Initialization ---
# This uses Streamlit's secrets management to securely store credentials.
# The function checks if the app is already initialized to prevent errors on reruns.
def init_firebase():
    """Initializes the Firebase app using service account credentials."""
    try:
        # Check if the Firebase app is already initialized
        if not firebase_admin._apps:
            # Get credentials from st.secrets
            creds = credentials.Certificate(dict(st.secrets.firebase_credentials))
            firebase_admin.initialize_app(creds)
        
        # Return the Firestore client
        return firestore.client()

    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        st.warning("Please make sure your `secrets.toml` file is configured correctly with your Firebase credentials.")
        return None

# --- Firestore Functions ---

def add_sale(db, sale_data):
    """Adds a new sale document to the 'sales' collection."""
    if not db:
        st.error("Firestore database connection is not available.")
        return
    try:
        # Add a server-side timestamp for accuracy
        sale_data['timestamp'] = firestore.SERVER_TIMESTAMP
        db.collection('sales').add(sale_data)
    except Exception as e:
        st.error(f"Error adding sale to Firestore: {e}")

def get_all_sales(db):
    """Fetches all sales documents from the 'sales' collection, ordered by timestamp."""
    if not db:
        st.error("Firestore database connection is not available.")
        return []
    try:
        # Query sales and order them by timestamp in descending order (newest first)
        sales_ref = db.collection('sales').order_by('timestamp', direction=firestore.Query.DESCENDING)
        sales = sales_ref.stream()
        
        # Convert the stream to a list of documents with their IDs
        return [{'id': sale.id, **sale.to_dict()} for sale in sales]
    except Exception as e:
        st.error(f"Error fetching sales from Firestore: {e}")
        return []

def delete_sale(db, sale_id):
    """Deletes a specific sale document from the 'sales' collection."""
    if not db:
        st.error("Firestore database connection is not available.")
        return
    try:
        db.collection('sales').document(sale_id).delete()
    except Exception as e:
        st.error(f"Error deleting sale: {e}")

def get_ph_time():
    """Gets the current time in Philippine timezone (UTC+8)."""
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    ph_tz = pytz.timezone("Asia/Manila")
    return utc_now.astimezone(ph_tz)
