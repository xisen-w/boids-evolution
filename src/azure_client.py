"""
Minimal Azure OpenAI client wrapper.
Just the essentials: init, chat(), chat_to_json(), structured_output()
"""
import os
import json
from typing import Optional, Dict, Any, List, TypeVar, Type
from openai import AzureOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Type variable for structured output
T = TypeVar('T', bound=BaseModel)


class AzureOpenAIClient:
    """Enhanced wrapper for Azure OpenAI API with multiple model support."""
    
    def __init__(self, model_name: str = "default"):
        """Initialize with environment variables and model selection."""
        self.model_name = model_name
        
        if model_name == "gpt-4.1-nano":
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("GPT_4_1_NANO_ENDPOINT"),
                api_key=os.getenv("GPT_4_1_NANO_API_KEY"),
                api_version=os.getenv("GPT_4_1_NANO_API_VERSION", "2024-12-01-preview")
            )
            self.deployment_name = os.getenv("GPT_4_1_NANO_DEPLOYMENT", "gpt-4.1-nano")
            self.max_tokens_limit = int(os.getenv("GPT_4_1_NANO_MAX_TOKENS", "13107"))
            
        elif model_name == "gpt-4o-mini":
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("GPT_4O_MINI_ENDPOINT"),
                api_key=os.getenv("GPT_4O_MINI_API_KEY"),
                api_version=os.getenv("GPT_4O_MINI_API_VERSION", "2024-12-01-preview")
            )
            self.deployment_name = os.getenv("GPT_4O_MINI_DEPLOYMENT", "gpt-4o-mini")
            self.max_tokens_limit = int(os.getenv("GPT_4O_MINI_MAX_TOKENS", "4096"))
            
        elif model_name == "deepseek-v3":
            from openai import OpenAI
            self.client = OpenAI(
                base_url=os.getenv("DEEPSEEK_V3_ENDPOINT"),
                api_key=os.getenv("DEEPSEEK_V3_API_KEY")
            )
            self.deployment_name = os.getenv("DEEPSEEK_V3_DEPLOYMENT", "DeepSeek-V3-0324")
            self.max_tokens_limit = int(os.getenv("DEEPSEEK_V3_MAX_TOKENS", "8192"))
            
        else:  # default - use original configuration
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-nano")
            self.max_tokens_limit = 13107
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = None) -> str:
        """
        Simple chat completion.
        
        Args:
            messages: List of {"role": "user/system/assistant", "content": "..."}
            temperature: 0.0-1.0 randomness
            max_tokens: Max response length (defaults to model limit)
            
        Returns:
            String response
        """
        try:
            # Use model-specific token limit if not specified
            if max_tokens is None:
                max_tokens = min(self.max_tokens_limit, 4000)  # Conservative default
            else:
                max_tokens = min(max_tokens, self.max_tokens_limit)
                
            # GPT-5 uses max_completion_tokens and only supports temperature=1.0
            if "gpt-5" in self.deployment_name.lower():
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=1.0  # GPT-5 only supports default temperature
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            content = response.choices[0].message.content
            return content.strip() if content else "No response content"
            
        except Exception as e:
            print(f"Chat error ({self.model_name}): {e}")
            return f"Error: {str(e)}"
    
    def chat_to_json(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = None) -> Dict[str, Any]:
        """
        Chat completion with JSON mode - forces structured output.
        
        Args:
            messages: List of messages (system message should specify JSON format)
            temperature: Lower for more consistent JSON
            max_tokens: Max response length (defaults to model limit)
            
        Returns:
            Parsed JSON dict, or error dict if parsing fails
        """
        try:
            # Use model-specific token limit if not specified
            if max_tokens is None:
                max_tokens = min(self.max_tokens_limit, 4000)
            else:
                max_tokens = min(max_tokens, self.max_tokens_limit)
                
            # GPT-5 uses max_completion_tokens and only supports temperature=1.0
            if "gpt-5" in self.deployment_name.lower():
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=1.0,  # GPT-5 only supports default temperature
                    response_format={"type": "json_object"}  # Force JSON mode
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"}  # Force JSON mode
                )
            
            content = response.choices[0].message.content
            if not content:
                return {"error": "empty_response", "message": "No content in response"}
                
            content = content.strip()
            
            # Handle markdown code blocks (common with DeepSeek)
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()
            elif content.startswith("```") and content.endswith("```"):
                content = content[3:-3].strip()
                
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error ({self.model_name}): {e}")
            return {"error": "invalid_json", "raw_content": content}
        except Exception as e:
            print(f"Chat JSON error ({self.model_name}): {e}")
            return {"error": "api_error", "message": str(e)}
    
    def structured_output(self, messages: List[Dict[str, str]], response_model: Type[T], 
                         temperature: float = 0.1, max_tokens: int = None) -> T:
        """
        Chat completion with structured Pydantic output - guaranteed type safety.
        
        Args:
            messages: List of messages 
            response_model: Pydantic model class for the expected response
            temperature: Lower for more consistent results
            max_tokens: Max response length (defaults to model limit)
            
        Returns:
            Parsed Pydantic model instance
        """
        try:
            # Use model-specific token limit if not specified
            if max_tokens is None:
                max_tokens = min(self.max_tokens_limit, 4000)
            else:
                max_tokens = min(max_tokens, self.max_tokens_limit)
                
            # GPT-5 uses max_completion_tokens and only supports temperature=1.0
            if "gpt-5" in self.deployment_name.lower():
                response = self.client.beta.chat.completions.parse(
                    model=self.deployment_name,
                    messages=messages,
                    response_format=response_model,
                    max_completion_tokens=max_tokens,
                    temperature=1.0  # GPT-5 only supports default temperature
                )
            else:
                response = self.client.beta.chat.completions.parse(
                    model=self.deployment_name,
                    messages=messages,
                    response_format=response_model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            
            return response.choices[0].message.parsed
            
        except Exception as e:
            print(f"Structured output error ({self.model_name}): {e}")
            # Return a default instance with error info
            if hasattr(response_model, 'model_validate'):
                try:
                    # Try to create a minimal valid instance
                    return response_model.model_validate({"error": str(e)})
                except:
                    # If that fails, let the exception bubble up
                    raise e
            else:
                raise e


# Pydantic models for common boids patterns
class AgentDecision(BaseModel):
    """Standard agent decision structure."""
    action: str  # build_tool, use_tool, rest
    tool_type: Optional[str] = None  # data, logic, utility, code
    confidence: float  # 0.0-1.0
    reason: str  # brief explanation
    target_tool: Optional[str] = None  # for use_tool actions

class ToolDesign(BaseModel):
    """Tool design specification for structured output."""
    tool_name: str  # The exact tool name (e.g., "sentiment_analyzer", "pdf_processor")
    description: str  # Brief description of what the tool does
    tool_type: str  # data, logic, utility, code
    parameters: List[str] = []  # List of parameter names/types
    return_type: str = "dict"  # Return type of the tool
    composition_plan: List[str] = []  # List of other tools this tool will use
    implementation_notes: str = ""  # Additional implementation details

class ToolCreation(BaseModel):
    """Tool creation specification."""
    name: str
    tool_type: str  # data, logic, utility, code
    description: str
    dependencies: List[str] = []
    code_outline: str  # what the tool should do

class NetworkAnalysis(BaseModel):
    """Agent network analysis."""
    agent_id: str
    specialization: Optional[str] = None
    energy: int
    tool_count: int
    collaboration_score: float  # 0.0-1.0


def test_model(model_name: str, model_display_name: str):
    """Test a specific model with all functionality."""
    print(f"\n🚀 Testing {model_display_name}")
    print("=" * 60)
    
    try:
        client = AzureOpenAIClient(model_name)
        print(f"✅ Client initialized: {client.deployment_name} (max tokens: {client.max_tokens_limit})")
    except Exception as e:
        print(f"❌ Failed to initialize {model_display_name}: {e}")
        return
    
    # Test 1: Simple chat
    print(f"\n🗨️  Test 1: Simple Chat ({model_display_name})")
    print("-" * 40)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": "What is 2+2? Answer in one sentence and identify yourself."}
    ]
    
    try:
        response = client.chat(messages, max_tokens=100)
        print(f"Response: {response}")
    except Exception as e:
        print(f"❌ Chat failed: {e}")
    
    # Test 2: JSON mode
    print(f"\n📝 Test 2: JSON Mode ({model_display_name})")
    print("-" * 40)
    
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
    
    try:
        json_response = client.chat_to_json(json_messages, max_tokens=200)
        print(f"JSON Response: {json.dumps(json_response, indent=2)}")
    except Exception as e:
        print(f"❌ JSON mode failed: {e}")
    
    # Test 3: Structured output (only for Azure models, not DeepSeek)
    if model_name != "deepseek-v3":
        print(f"\n🎯 Test 3: Structured Output ({model_display_name})")
        print("-" * 40)
        
        structured_messages = [
            {"role": "system", "content": "You are a boids agent making decisions. Analyze the situation and decide what to do."},
            {"role": "user", "content": "I see my neighbors building data processing tools. I have low energy. What should I do?"}
        ]
        
        try:
            structured_response = client.structured_output(structured_messages, AgentDecision, max_tokens=300)
            print(f"Structured Response:")
            print(f"  Action: {structured_response.action}")
            print(f"  Tool Type: {structured_response.tool_type}")
            print(f"  Confidence: {structured_response.confidence}")
            print(f"  Reason: {structured_response.reason}")
            print(f"  Target Tool: {structured_response.target_tool}")
        except Exception as e:
            print(f"❌ Structured output failed: {e}")
    else:
        print(f"\n⚠️  Structured output skipped for {model_display_name} (not supported)")
    
    # Test 4: Creative writing test
    print(f"\n✍️  Test 4: Creative Writing ({model_display_name})")
    print("-" * 40)
    
    creative_messages = [
        {"role": "system", "content": "You are a creative writer. Write in a unique style."},
        {"role": "user", "content": "Write a haiku about artificial intelligence and tools."}
    ]
    
    try:
        creative_response = client.chat(creative_messages, temperature=0.8, max_tokens=150)
        print(f"Creative Response:\n{creative_response}")
    except Exception as e:
        print(f"❌ Creative writing failed: {e}")


def main():
    """Test all available Azure OpenAI models."""
    
    print("🧪 TESTING MULTIPLE AZURE OPENAI MODELS")
    print("=" * 80)
    
    # Check if basic environment variables are set
    basic_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]
    missing_basic = [var for var in basic_vars if not os.getenv(var)]
    
    if missing_basic:
        print(f"❌ Missing basic environment variables: {missing_basic}")
        print("   Set them in .env file or environment")
        return
    
    # Test all models
    models_to_test = [
        ("default", "GPT-4.1-nano (Default)"),
        ("gpt-4.1-nano", "GPT-4.1-nano (Explicit)"),
        ("gpt-4o-mini", "GPT-4o-mini (Fast & Efficient)"),
        ("deepseek-v3", "DeepSeek-V3 (Alternative)")
    ]
    
    successful_tests = 0
    total_tests = len(models_to_test)
    
    for model_name, display_name in models_to_test:
        try:
            test_model(model_name, display_name)
            successful_tests += 1
        except Exception as e:
            print(f"❌ Model {display_name} testing failed completely: {e}")
    
    # Summary
    print(f"\n🎉 TESTING COMPLETE!")
    print("=" * 80)
    print(f"✅ Successfully tested: {successful_tests}/{total_tests} models")
    
    if successful_tests == total_tests:
        print("🚀 All models are ready for serious experiments!")
    elif successful_tests > 0:
        print(f"⚠️  {total_tests - successful_tests} models had issues - check configuration")
    else:
        print("❌ No models working - check your .env configuration")
    
    print("\n📋 Model Recommendations:")
    print("  • GPT-4.1-nano: Fast, reliable, good for tool generation")
    print("  • GPT-4o-mini: Very fast & efficient, cost-effective for experiments")
    print("  • DeepSeek-V3: Alternative perspective, good for diversity")


if __name__ == "__main__":
    main() 