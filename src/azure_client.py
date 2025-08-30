"""
Minimal Azure OpenAI client wrapper.
Just the essentials: init, chat(), chat_to_json()
"""
import os
import json
from typing import Optional, Dict, Any, List
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class AzureOpenAIClient:
    """Minimal wrapper for Azure OpenAI API."""
    
    def __init__(self):
        """Initialize with environment variables."""
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Simple chat completion.
        
        Args:
            messages: List of {"role": "user/system/assistant", "content": "..."}
            temperature: 0.0-1.0 randomness
            max_tokens: Max response length
            
        Returns:
            String response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Chat error: {e}")
            return f"Error: {str(e)}"
    
    def chat_to_json(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 300) -> Dict[str, Any]:
        """
        Chat completion with JSON mode - forces structured output.
        
        Args:
            messages: List of messages (system message should specify JSON format)
            temperature: Lower for more consistent JSON
            max_tokens: Max response length
            
        Returns:
            Parsed JSON dict, or error dict if parsing fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"}  # Force JSON mode
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"error": "invalid_json", "raw_content": content}
        except Exception as e:
            print(f"Chat JSON error: {e}")
            return {"error": "api_error", "message": str(e)}


def main():
    """Test the Azure client with examples."""
    
    print("🧪 Testing Minimal Azure OpenAI Client")
    print("=" * 50)
    
    # Check if environment variables are set
    required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("   Set them in .env file or environment")
        return
    
    client = AzureOpenAIClient()
    
    # Test 1: Simple chat
    print("\n🗨️  Test 1: Simple Chat")
    print("-" * 30)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": "What is 2+2? Answer in one sentence."}
    ]
    
    response = client.chat(messages)
    print(f"Response: {response}")
    
    # Test 2: JSON mode
    print("\n📝 Test 2: JSON Mode")
    print("-" * 30)
    
    json_messages = [
        {"role": "system", "content": """You must respond with valid JSON in this exact format:
{
    "action": "build_tool" or "use_tool" or "rest",
    "tool_type": "data" or "logic" or "utility" or "code",
    "confidence": 0.0 to 1.0,
    "reason": "brief explanation"
}"""},
        {"role": "user", "content": "I want to create a tool that processes text data. What should I do?"}
    ]
    
    json_response = client.chat_to_json(json_messages)
    print(f"JSON Response: {json.dumps(json_response, indent=2)}")
    
    # Test 3: Error handling
    print("\n⚠️  Test 3: Error Handling")
    print("-" * 30)
    
    bad_messages = [
        {"role": "system", "content": "Respond with invalid JSON format."},
        {"role": "user", "content": "Give me broken JSON"}
    ]
    
    error_response = client.chat_to_json(bad_messages)
    print(f"Error Response: {json.dumps(error_response, indent=2)}")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main() 