import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import datetime

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-3.5-flash-lite"
TODAY = datetime.date.today()

interaction = client.interactions.create(model=MODEL,
                                         system_instruction="You are a chat-bot who helps students to find the best place to live in Lisbon by their needs. Be friendly.",
                                         input="Hey, how are you doing?")

print(interaction.output_text)