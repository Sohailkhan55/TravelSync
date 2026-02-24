from langgraph.graph import StateGraph, END
from typing import TypedDict
from .state import ItineraryState
from .utils import validate_india_location
from .planner import plan_itinerary
from .booking import get_travel_options
from .food_stay import find_hotels, find_restaurants

def validate_step(state: ItineraryState):
    """
    Node: Validates the destination.
    """
    destination = state['destination']
    is_valid = validate_india_location(destination)
    return {"is_valid_india_location": is_valid, "validation_error": None if is_valid else f"{destination} is not a valid Indian tourist destination."}

def planning_step(state: ItineraryState):
    """
    Node: Generates initial place suggestions.
    """
    if not state.get("is_valid_india_location"):
        return {}
    
    places = plan_itinerary(state['destination'])
    return {"suggested_places": places}

def booking_step(state: ItineraryState):
    """
    Node: Fetches travel options (Parallel node potentially).
    """
    # Simply using a hardcoded origin for demo or extracting from user input if available
    # For now, let's assume 'New Delhi' as default origin if not generic
    origin = "New Delhi" 
    destination = state['destination']
    date = "2025-01-15" # Mock date
    
    options = get_travel_options(origin, destination, date)
    return {"flights": options['flights'], "trains": options['trains']}

def accommodation_step(state: ItineraryState):
    """
    Node: Fetches hotels and food.
    """
    dest = state['destination']
    hotels = find_hotels(dest)
    food = find_restaurants(dest) # Always fetch food options
        
    return {"hotels": hotels, "restaurants": food}

# Build Graph
workflow = StateGraph(ItineraryState)

workflow.add_node("validate", validate_step)
workflow.add_node("planner", planning_step)
workflow.add_node("booking", booking_step)
workflow.add_node("accommodation", accommodation_step)

workflow.set_entry_point("validate")

def route_after_validation(state: ItineraryState):
    if state["is_valid_india_location"]:
        return "planner"
    else:
        return END

workflow.add_conditional_edges(
    "validate",
    route_after_validation,
    {
        "planner": "planner",
        END: END
    }
)

# Parallel execution for booking and accommodation after planner (or concurrently)
# For simplicity, let's run them after planner
workflow.add_edge("planner", "booking")
workflow.add_edge("booking", "accommodation")
workflow.add_edge("accommodation", END)

app_graph = workflow.compile()
