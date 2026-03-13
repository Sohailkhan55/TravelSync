from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .utils import get_llm

def find_hotels(destination: str, budget: str = "mid-range"):
    """
    Finds hotels in the destination.
    """
    llm = get_llm()
    
    parser = JsonOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert travel concierge for India. Recommend the top 3 {budget} hotels in {destination}. Return ONLY a JSON list of objects: [{{\"name\": \"Hotel Name\", \"rating\": \"X/5\", \"approx_price\": \"Rs. Y per night\"}}]."),
        ("human", "Recommend hotels in {destination}:")
    ])
    
    chain = prompt | llm | parser
    try:
        hotels = chain.invoke({"destination": destination, "budget": budget})
        return hotels
    except Exception as e:
        return [{"name": "Error fetching hotels", "rating": "N/A", "approx_price": "N/A"}]

def find_restaurants(destination: str, food_pref: str = "local food"):
    """
    Finds restaurants in the destination.
    """
    llm = get_llm()
    
    parser = JsonOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a local food guide for India. Recommend the top 3 restaurants in {destination} serving {food_pref}. Return ONLY a JSON list of objects: [{{\"name\": \"Restaurant Name\", \"cuisine\": \"Type of Cuisine\", \"must_try\": \"Signature Dish\"}}]."),
        ("human", "Recommend restaurants in {destination}:")
    ])
    
    chain = prompt | llm | parser
    try:
        food = chain.invoke({"destination": destination, "food_pref": food_pref})
        return food
    except Exception as e:
        import traceback
        traceback.print_exc()
        return [{"name": "Error fetching restaurants", "cuisine": "N/A", "must_try": "N/A"}]
