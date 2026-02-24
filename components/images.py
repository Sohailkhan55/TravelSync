import streamlit as st
import wikipedia

@st.cache_data(show_spinner=False)
def fetch_place_gallery(place_name, destination=None):
    """
    Fetches image URLs for a given place using Wikipedia.
    Returns a list of top 5 valid image URLs.
    """
    try:
        # 1. Search for the most relevant page
        search_query = place_name
        if destination:
             search_query = f"{place_name} {destination}"
             
        search_results = wikipedia.search(search_query)
        if not search_results:
             # Try just the place name if destination combo didn't work
             if destination:
                 search_results = wikipedia.search(place_name)
        
        if not search_results:
            return [] 
            
        # 2. Get the specific page (handle disambiguation automatically-ish)
        # auto_suggest=False prevents it from jumping to "Place (film)" etc unless explicit
        try:
            page = wikipedia.page(search_results[0], auto_suggest=False)
        except wikipedia.DisambiguationError as e:
            # If ambiguous, try the first option
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
            except:
                return []
        except wikipedia.PageError:
            return []
        
        # 3. Filter the images
        real_images = []
        for img_url in page.images:
            lower_url = img_url.lower()
            # Must be common image format
            if any(ext in lower_url for ext in ['.jpg', '.jpeg', '.png']):
                # Must NOT be junk
                if not any(bad in lower_url for bad in ['.svg', 'logo', 'icon', 'map', 'flag', 'listen', 'speaker', 'symbol']):
                     real_images.append(img_url)
        
        # 4. Return top 5 valid images
        return real_images[:5]

    except Exception as e:
        print(f"Error fetching Wikipedia images for {place_name}: {e}")
        return []
