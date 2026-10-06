"""
AI JSON Generator Tool - Structured JSON generation using Azure OpenAI (simplified)
"""

from typing import Optional, Any, Dict
from dotenv import load_dotenv
from src.azure_client import AzureOpenAIClient


def execute(prompt: str, schema: Optional[str] = None, format_type: str = "object", temperature: float = 0.1) -> Dict[str, Any]:
    """Generate structured JSON data and return the raw JSON as Python objects."""
    load_dotenv()

    system_content = (
        "You are a JSON data generator. You must respond with valid JSON only.\n"
        "Rules:\n"
        "1. Always return valid, parseable JSON\n"
        "2. Follow the user's specifications exactly\n"
        "3. Use appropriate data types (strings, numbers, booleans, arrays, objects)\n"
        "4. Include realistic sample data\n"
        "5. Ensure all JSON is properly formatted and escaped\n"
        "6. Do not include any text outside the JSON structure"
    )
    if schema:
        system_content += f"\n\nFollow this schema or example structure:\n{schema}"

    format_guides = {
        'object': "Generate a JSON object with key-value pairs.",
        'array': "Generate a JSON array with multiple items.",
        'config': "Generate a configuration JSON with settings and options.",
        'data': "Generate realistic sample data in JSON format.",
        'api': "Generate JSON that could be returned from an API endpoint.",
        'schema': "Generate a JSON schema definition.",
    }
    if format_type in format_guides:
        system_content += f"\n\nFormat type: {format_guides[format_type]}"

    client = AzureOpenAIClient()
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": str(prompt)},
    ]
    return client.chat_to_json(messages, temperature=float(temperature))

if __name__ == "__main__":
    import json
    print(json.dumps(execute("Create a user profile object", format_type="object"), indent=2)) 