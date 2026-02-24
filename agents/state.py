from typing import TypedDict, List, Optional

class ItineraryState(TypedDict):
    """
    State for the LangGraph workflow.
    """
    # User Input
    destination: str
    user_preferences: str  # Extra context like "temples", "adventure"
    
    # Validation
    is_valid_india_location: bool
    validation_error: Optional[str]
    
    # Planning
    suggested_places: List[dict]  # List of {name, description}
    selected_places: List[str]   # User finalized places
    
    # Final Output
    final_itinerary: List[dict]  # Enriched with time/details
    
    # Booking
    flights: List[dict]
    trains: List[dict]
    hotels: List[dict]
    restaurants: List[dict]
    
    # Context
    messages: List[str]  # Chat history for context
