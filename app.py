import streamlit as st
import os
from dotenv import load_dotenv
from agents.graph import app_graph
from components.itinerary import display_suggested_places
from components.dashboard import render_dashboard
from components.login_page import render_login_page
from database.db_manager import init_db, create_group, add_itinerary_item

# Load Env
load_dotenv()

# Page Config
st.set_page_config(page_title="TravelSync India", page_icon="🇮🇳", layout="wide")

# Initialize DB
if "db_init" not in st.session_state:
    init_db()
    st.session_state["db_init"] = True

# --- Authentication Check ---
if "user_phone" not in st.session_state:
    render_login_page()
    st.stop()  # Stop execution until logged in

# --- Authenticated App ---
user_phone = st.session_state["user_phone"]
user_name = st.session_state.get("user_name", "Traveler")

# Sidebar
st.sidebar.title(f"Welcome, {user_name}!")
st.sidebar.caption(f"Phone: {user_phone}")

page = st.sidebar.radio("Navigation", ["Plan a Trip", "My Dashboard"])

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

if page == "Plan a Trip":
    st.title("🇮🇳 TravelSync India")
    st.markdown("### Your AI Agent for Indian Adventures")

    # Step 1: Input (Only show if not in selection mode or allow changing)
    destination = st.text_input("Where do you want to go?", placeholder="e.g., Jaipur, Kerala, Manali")
    
    if st.button("Start Planning"):
        if not destination:
            st.warning("Please enter a destination.")
        else:
            with st.spinner("Consulting with travel agents..."):
                initial_state = {
                    "destination": destination,
                    "is_valid_india_location": False,
                    "suggested_places": [],
                    "messages": []
                }
                
                # Run Graph
                result = app_graph.invoke(initial_state)
                
                if not result.get("is_valid_india_location"):
                    st.error(result.get("validation_error", "Invalid location."))
                else:
                    st.session_state["plan_result"] = result
                    st.session_state["step"] = "selection"
                    st.rerun()

    # Step 2: Selection
    if st.session_state.get("step") == "selection":
        st.divider()
        result = st.session_state["plan_result"]
        places = result.get("suggested_places", [])
        
        # Display selection UI
        # Display selection UI
        selected = display_suggested_places(places, result['destination'])

        st.subheader("Finalize Trip")
        group_name = st.text_input("Name your Trip", value=f"{result['destination']} Trip")
        
        if st.button("Finalize & Create Group"):
            if not selected:
                st.warning("Please select at least one place.")
            else:
                # Create group with the current user as creator
                group_id = create_group(group_name, user_phone, result['destination'])
                
                # Save items
                for place in selected:
                    add_itinerary_item(group_id, place, "place")
                
                st.success(f"Trip Created! Group ID: {group_id}")
                st.session_state["current_group_id"] = group_id
                st.balloons()
                st.info("Go to 'My Dashboard' to view your trip.")

elif page == "My Dashboard":
    render_dashboard(user_phone)
