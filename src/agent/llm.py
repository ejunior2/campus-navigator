import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

MODEL = "gemini-3.1-flash-lite"

from google.genai import types


def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found. Check your .env file.")
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=30000),
    )

def ask(prompt: str, retries: int = 4) -> str:
    client = get_client()
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL, contents=prompt
            )
            return response.text
        except errors.ServerError:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt * 3)


if __name__ == "__main__":
    print(ask("Reply in Portuguese with one short sentence: what is Wi-Fi?"))