from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .utils import get_llm

search_tool = DuckDuckGoSearchRun()

def find_hotels(destination: str, budget: str = "mid-range"):
    """
    Finds hotels in the destination.
    """
    llm = get_llm()
    query = f"Best {budget} hotels in {destination} India with prices"
    search_results = search_tool.run(query)
    
    parser = JsonOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a travel concierge. Extract top 3 recommendation for hotels from the search results. Return a JSON list of objects: {{\"name\": str, \"rating\": str, \"approx_price\": str}}."),
        ("human", "Search Results: {results}")
    ])
    
    chain = prompt | llm | parser
    try:
        hotels = chain.invoke({"results": search_results})
        return hotels
    except Exception as e:
        return [{"name": "Error fetching hotels", "rating": "N/A", "approx_price": "N/A"}]

def find_restaurants(destination: str, food_pref: str = "local food"):
    """
    Finds restaurants in the destination.
    """
    llm = get_llm()
    query = f"Best restaurants in {destination} India for {food_pref}"
    search_results = search_tool.run(query)
    
    parser = JsonOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a food guide. Extract top 3 restaurants. Return a JSON list of objects: {{\"name\": str, \"cuisine\": str, \"must_try\": str}}."),
        ("human", "Search Results: {results}")
    ])
    
    chain = prompt | llm | parser
    try:
        food = chain.invoke({"results": search_results})
        return food
    except Exception as e:
        import traceback
        traceback.print_exc()
        return [{"name": "Error fetching restaurants", "cuisine": "N/A", "must_try": "N/A"}]
