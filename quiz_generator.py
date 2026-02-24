import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def generate_question(context):
    prompt = f"""
    Using ONLY the telecom context below,
    generate one clear quiz question.

    Context:
    {context}
    """

    response = model.generate_content(prompt)
    return response.text