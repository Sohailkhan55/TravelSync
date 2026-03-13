from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .utils import get_llm

def plan_itinerary(destination: str):
    """
    Generates a list of suggested places for a given destination.
    """
    llm = get_llm()
    
    parser = JsonOutputParser()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert travel assistant with vast knowledge of places in India. Generate a comprehensive list of top tourist places in {destination} (aim for 10-15 distinct places if available, minimum 5). Return ONLY a JSON list of objects, e.g. [{{\"name\": \"Place A\", \"description\": \"Short description\"}}]. Do not include any other text."),
        ("human", "List the top tourist places in {destination}:")
    ])
    
    chain = prompt | llm | parser
    
    try:
        places = chain.invoke({"destination": destination})
        return places
    except Exception as e:
        print(f"Planning Error: {e}")
        return ["Error fetching places. Please try again."]

def generate_detailed_itinerary(places: list, destination: str):
    """
    Creates a day-wise plan based on selected places.
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a travel planner. Create a logical itinerary for these places in {destination}. Return a JSON list of objects with keys: 'day', 'activities' (list of strings)."),
        ("human", "Places: {places}")
    ])
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        itinerary = chain.invoke({"places": str(places), "destination": destination})
        return itinerary
    except Exception as e:
        return [{"day": 1, "activities": ["Could not generate details."]}]
