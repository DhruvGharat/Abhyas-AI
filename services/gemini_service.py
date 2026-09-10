import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Please add it to your .env file."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


def call_gemini_with_retry(prompt: str, response_format=None, max_retries: int = 3, delay: int = 5):
    """
    Wrapper for Gemini API calls with exponential backoff retry for HTTP 429 rate limit errors.
    """
    for attempt in range(1, max_retries + 1):
        try:
            kwargs = {
                "model": MODEL_NAME,
                "input": prompt
            }
            if response_format:
                kwargs["response_format"] = response_format

            interaction = client.interactions.create(**kwargs)
            return interaction.output_text

        except Exception as error:
            error_str = str(error)
            if "429" in error_str or "too_many_requests" in error_str or "quota" in error_str.lower():
                if attempt < max_retries:
                    print(f"Gemini 429 Rate Limit hit. Retrying in {delay} seconds (Attempt {attempt}/{max_retries})...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    raise RuntimeError(
                        "Gemini API rate limit reached (20 requests/min free tier limit). "
                        "Please wait 30-60 seconds and try again."
                    )
            else:
                raise error


def ask_gemini(prompt: str) -> str:
    """
    Send a prompt to Gemini using the Interactions API with retry mechanism.
    """
    return call_gemini_with_retry(prompt)