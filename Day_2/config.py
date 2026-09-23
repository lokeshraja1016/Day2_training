import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("MODEL", "openai/gpt-oss-120b")

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def banner(title):
    print("=" * 72)
    print(f"=== {title} ===")
    print("=" * 72)