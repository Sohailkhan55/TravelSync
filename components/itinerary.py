import streamlit as st

from .images import fetch_place_gallery

def display_suggested_places(places, destination=None):
    """
    Renders Place Cards with gallery and selection.
    Returns the list of selected place names.
    """
    st.subheader("📍 Suggested Places")
    selected_places = []
    
    st.write("Review the suggestions and select your favorites:")
    
    for i, place_data in enumerate(places):
        # Handle if place_data is just a string (old format) vs dict (new format)
        if isinstance(place_data, str):
            name = place_data
            description = "Explore this amazing destination."
        else:
            name = place_data.get("name", "Unknown Place")
            description = place_data.get("description", "No description available.")
            
        # Create Card
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(name)
                st.write(description)
                
                # Gallery Feature
                with st.expander(f"📸 Images of {name}"):
                    # Using a spinner because image fetching might take a moment
                    with st.spinner(f"Loading photos for {name}..."):
                        image_urls = fetch_place_gallery(name, destination)
                        # Display images in a row (3 columns now)
                        if image_urls:
                            img_cols = st.columns(len(image_urls))
                            for j, url in enumerate(image_urls):
                                with img_cols[j]:
                                    # Fix warning: For use_container_width=True, use width='stretch'
                                    st.image(url, width=300) 
                        else:
                             st.write("No images found.")

            with col2:
                # Selection Control
                # Centering vertically can be tricky, but we'll specific placement
                st.write("") # Spacer
                is_selected = st.checkbox("Add to Itinerary", value=True, key=f"select_{i}_{name}")
                if is_selected:
                    selected_places.append(name)
                    
    return selected_places

def display_food_options(restaurants):
    """
    Renders checkboxes for users to select restaurants.
    Returns the list of selected restaurants.
    """
    selected_restaurants = []
    
    if not restaurants:
        return []

    st.subheader("🍽️ Suggested Restaurants")
    
    with st.container():
        st.write("Select the restaurants you'd like to try:")
        for i, resto in enumerate(restaurants):
            label = f"**{resto.get('name', 'Unknown')}** - {resto.get('cuisine', 'Various')} ({resto.get('must_try', 'N/A')})"
            if st.checkbox(label, value=True, key=f"select_food_{i}"):
                # Store just the name or the whole object?
                # The DB function add_itinerary_item likely takes a string for 'place', 
                # but let's check. 
                # If it takes a string, we might need to serialize it or just store the name.
                # app.py calls add_itinerary_item(group_id, place, "place")
                # I'll modify app.py to handle this.
                selected_restaurants.append(resto)
        
    return selected_restaurants
