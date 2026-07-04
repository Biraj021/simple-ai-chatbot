import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = "what is history in india"
validation_rule = "Accept only programming, software development, debugging, algorithms, DSA, Git, Linux, and tech-related queries (Python, Java, C++, JS, HTML, CSS, SQL). Reject History, Politics, Movies, Sports, Medical, Travel, etc."

schema = {"type": "OBJECT", "properties": {"valid": {"type": "BOOLEAN"}}}
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=schema,
    system_instruction=f"You are an intent classifier. Evaluate the user's prompt based strictly on this rule: {validation_rule}. Return JSON with valid=true if it matches, and valid=false if it should be rejected.",
    temperature=0.0
)

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=config
    )
    print("Response:", response.text)
except Exception as e:
    print("Exception:", e)
