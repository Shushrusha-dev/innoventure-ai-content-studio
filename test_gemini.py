
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

if not key:
    print("API KEY NOT FOUND")
else:
    client = genai.Client(api_key=key)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Say Hello Innoventure!"
    )

    print(response.text)
