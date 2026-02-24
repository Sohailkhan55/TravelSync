from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .utils import get_llm

class LocalChatbotAgent:
    def __init__(self):
        self.llm = get_llm()

    def handle_chat_query(self, query: str, destination: str) -> str:
        """
        Processes a chat query about the given destination using the LLM.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are TravelAI, a helpful, enthusiastic, and knowledgeable travel assistant inside a group chat for a trip to {destination}. Provide concise, accurate, and friendly answers. If asked for recommendations, keep them brief and relevant to {destination}. Use emojis to keep it fun!"),
            ("human", "User Question: {query}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            # Strip the trigger word to save context window and avoid self-reference loops
            clean_query = query.replace("@TravelAI", "").strip()
            return chain.invoke({
                "destination": destination or "an unknown destination", 
                "query": clean_query
            })
        except Exception as e:
            print(f"Chatbot Error: {e}")
            return "Oops! I encountered an error while thinking about that. Please try again! 🤖🌦️"
