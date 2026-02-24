import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    return ChatGroq(
        temperature=0, 
        model_name="llama-3.3-70b-versatile",
        groq_api_key=api_key
    )

def validate_india_location(location: str) -> bool:
    """
    Validates if the provided location is a real city or landmark in India.
    Returns True if valid, False otherwise.
    """
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a geography expert for India. Your only job is to validate if a given location is inside India."),
        ("human", "Is '{location}' a valid city, town, or tourist landmark located strictly within India? Reply with only 'YES' or 'NO'.")
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({"location": location})
        content = response.content.strip().upper()
        return "YES" in content
    except Exception as e:
        print(f"Validation Error: {e}")
        return False
