import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")
print("Key loaded:", key[:10] + "..." if key else "NOT FOUND")