import sys
import os
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from agents.food_stay import find_restaurants

print("Starting debug search for Hyderabad...")
try:
    res = find_restaurants("Hyderabad")
    print("Result:", res)
except Exception as e:
    print("Top Level Error:", e)
