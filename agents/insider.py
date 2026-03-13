import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .utils import get_llm

class LocalInsiderAgent:
    def __init__(self):
        self.llm = get_llm()

    def fetch_food_intel(self, city: str):
        return self._summarize_with_llm("famous authentic food, must-try dishes, and legendary restaurants", city)

    def fetch_shopping_intel(self, city: str):
        return self._summarize_with_llm("famous souvenirs, things to buy, and best local markets", city)

    def fetch_hacks_intel(self, city: str):
        return self._summarize_with_llm("travel tips, unique cultural experiences, and important safety/scam advice", city)

    def fetch_insider_intel(self, city: str) -> dict:
        """
        Wrapper for backward compatibility or bulk fetch.
        """
        return {
            "food": self.fetch_food_intel(city),
            "shopping": self.fetch_shopping_intel(city),
            "hacks": self.fetch_hacks_intel(city)
        }

    def _summarize_with_llm(self, topic, city):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a local travel expert for Indian cities. Your goal is to provide useful, distinct, and practical insider advice."),
            ("human", f"""
            Provide insider intel about {topic} in {city}.
            
            Task:
            1. Extract 3-5 distinct, high-quality bullet points containing names and specific details.
            2. Make it sound professional and enthusiastic.
            3. Return ONLY the bullet points (no intro/outro).
            """)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        try:
            return chain.invoke({})
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Could not fetch insider intel at this time."
