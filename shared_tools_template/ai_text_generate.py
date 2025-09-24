"""
AI Text Generator Tool - Creative text generation using Azure OpenAI (simplified)
"""

from typing import Optional
from dotenv import load_dotenv
from src.azure_client import AzureOpenAIClient


def execute(prompt: str, temperature: float = 0.7, max_tokens: int = 200, style: Optional[str] = None) -> str:
    """Generate creative text and return raw string."""
    load_dotenv()

    system_prompts = {
        'creative': "You are a creative writer. Be imaginative, vivid, and engaging.",
        'professional': "You are a professional writer. Be clear, concise, and authoritative.",
        'casual': "You are a friendly conversationalist. Be relaxed, approachable, and natural.",
        'technical': "You are a technical writer. Be precise, detailed, and informative.",
        'humorous': "You are a witty writer. Be funny, clever, and entertaining.",
    }
    system_content = system_prompts.get((style or '').lower(), "You are a helpful AI assistant. Generate high-quality text based on the user's request.")

    client = AzureOpenAIClient()
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": str(prompt)},
    ]
    return client.chat(messages, temperature=float(temperature), max_tokens=int(max_tokens))

if __name__ == "__main__":
    print(execute("Write a short story about a robot learning to paint.", temperature=0.7, max_tokens=120, style="creative"))