import json
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .utils import get_llm

class LocalInsiderAgent:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
        self.llm = get_llm()

    def fetch_food_intel(self, city: str):
        query = f"famous authentic food must try dishes and legendary restaurants in {city}"
        raw = self._safe_search(query)
        return self._summarize_with_llm(raw, "food and restaurants", city)

    def fetch_shopping_intel(self, city: str):
        query = f"famous souvenirs things to buy and best markets in {city}"
        raw = self._safe_search(query)
        return self._summarize_with_llm(raw, "souvenirs and shopping markets", city)

    def fetch_hacks_intel(self, city: str):
        query = f"travel tips unique cultural experiences and scams to avoid in {city}"
        raw = self._safe_search(query)
        return self._summarize_with_llm(raw, "local culture, travel hacks, and safety tips", city)

    def fetch_insider_intel(self, city: str) -> dict:
        """
        Wrapper for backward compatibility or bulk fetch.
        """
        return {
            "food": self.fetch_food_intel(city),
            "shopping": self.fetch_shopping_intel(city),
            "hacks": self.fetch_hacks_intel(city)
        }

    def _safe_search(self, query):
        try:
            return self.search.run(query)
        except Exception as e:
            print(f"Search error for '{query}': {e}")
            return ""

    def _summarize_with_llm(self, raw_text, topic, city):
        if not raw_text:
            return "Could not find specific information."
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a local travel expert. Your goal is to extract useful, distinct, and practical advice from search results."),
            ("human", f"""
            Search Results for {topic} in {city}:
            {raw_text}
            
            Task:
            1. Extract 3-5 distinct, high-quality bullet points.
            2. Ignore ads, dates, promotions, or generic filler text.
            3. Fix broken sentences and make it sound professional.
            4. Return ONLY the bullet points (no intro/outro).
            """)
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        try:
            return chain.invoke({})
        except Exception as e:
            print(f"LLM Error: {e}")
            return raw_text[:300] + "..." # Fallback
