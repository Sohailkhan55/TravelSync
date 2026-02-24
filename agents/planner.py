from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .utils import get_llm

search_tool = DuckDuckGoSearchRun()

def plan_itinerary(destination: str):
    """
    Generates a list of suggested places for a given destination.
    """
    llm = get_llm()
    
    # Step 1: Search for top places
    query = f"Top 20 best tourist places to visit in {destination} India"
    search_results = search_tool.run(query)
    
    # Step 2: Parse into structured list
    parser = JsonOutputParser()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a travel assistant. Content provided is search results about a city. Extract a comprehensive list of top tourist places (aim for 10-15 distinct places if available, minimum 2). Return ONLY a JSON list of objects, e.g. [{{\"name\": \"Place A\", \"description\": \"Short description\"}}]."),
        ("human", "Search Results: {results}\n\nList the top 15 places:")
    ])
    
    chain = prompt | llm | parser
    
    try:
        places = chain.invoke({"results": search_results})
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
