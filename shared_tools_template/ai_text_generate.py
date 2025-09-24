"""
AI Text Generator Tool - Creative text generation using Azure OpenAI
"""

def execute(parameters, context=None):
    """
    Generate creative text using Azure OpenAI.
    
    Parameters:
    - prompt: The text prompt to generate from
    - temperature: Creativity level (0.0-1.0, default 0.7)
    - max_tokens: Maximum response length (default 200)
    - style: Optional style guide (creative, professional, casual, etc.)
    
    Returns:
    - Dictionary with generated text and metadata
    """
    try:
        # Import Azure client
        import sys
        import os
        from dotenv import load_dotenv
        
        # Add project root to path - dynamic calculation based on location
        current_file = os.path.abspath(__file__)
        if 'shared_tools_template' in current_file:
            # Running from template directory - 1 level up
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        else:
            # Running from experiment directory - 3 levels up
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        # Load environment variables
        load_dotenv()  # Try current directory first
        load_dotenv(os.path.join(project_root, '.env'))  # Try project root
        
        sys.path.append(project_root)
        
        try:
            from src.azure_client import AzureOpenAIClient
        except ImportError:
            return {
                "success": False,
                "error": "Azure OpenAI client not available",
                "result": "Please set up Azure OpenAI credentials"
            }
        
        # Get parameters
        prompt = parameters.get('prompt', '')
        if not prompt:
            return {
                "success": False,
                "error": "No prompt provided",
                "result": "Please provide a 'prompt' parameter"
            }
        
        temperature = float(parameters.get('temperature', 0.7))
        max_tokens = int(parameters.get('max_tokens', 200))
        style = parameters.get('style', '')
        
        # Validate parameters
        temperature = max(0.0, min(1.0, temperature))
        max_tokens = max(10, min(1000, max_tokens))
        
        # Build system prompt based on style
        system_prompts = {
            'creative': "You are a creative writer. Be imaginative, vivid, and engaging.",
            'professional': "You are a professional writer. Be clear, concise, and authoritative.",
            'casual': "You are a friendly conversationalist. Be relaxed, approachable, and natural.",
            'technical': "You are a technical writer. Be precise, detailed, and informative.",
            'humorous': "You are a witty writer. Be funny, clever, and entertaining."
        }
        
        system_content = system_prompts.get(style.lower(), "You are a helpful AI assistant. Generate high-quality text based on the user's request.")
        
        # Create Azure client and generate text
        try:
            client = AzureOpenAIClient()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Azure client: {str(e)}",
                "result": "Please check Azure credentials"
            }
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
        
        try:
            generated_text = client.chat(messages, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            return {
                "success": False,
                "error": f"Azure API call failed: {str(e)}",
                "result": "Please check Azure credentials and network connection"
            }
        
        # Check for errors in response
        if generated_text.startswith("Error:"):
            return {
                "success": False,
                "error": "Azure OpenAI API error",
                "result": generated_text,
                "prompt": prompt,
                "settings": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "style": style
                }
            }
        
        return {
            "success": True,
            "result": generated_text,
            "prompt": prompt,
            "settings": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "style": style
            },
            "word_count": len(generated_text.split()),
            "char_count": len(generated_text)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution error: {str(e)}",
            "result": "Failed to generate text"
        }

# Add this to the end of ai_text_generate.py
if __name__ == "__main__":
    print("🧪 Testing ai_text_generate directly...")
    
    # First, let's check the .env file
    import os
    from dotenv import load_dotenv
    
    print(f"Current working directory: {os.getcwd()}")
    print(f".env file exists in current dir: {os.path.exists('.env')}")
    
    # Try to load .env
    load_dotenv()
    print(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"AZURE_OPENAI_API_KEY exists: {bool(os.getenv('AZURE_OPENAI_API_KEY'))}")
    
    # Test basic functionality
    test_params = {
        "prompt": "Write a short story about a robot learning to paint.",
        "temperature": 0.7,
        "max_tokens": 100,
        "style": "creative"
    }
    
    print(f"Testing with parameters: {test_params}")
    result = execute(test_params)
    print(f"Result: {result}")
    
    # Test error handling
    print("\n🧪 Testing error handling...")
    error_params = {"prompt": ""}
    error_result = execute(error_params)
    print(f"Error test result: {error_result}")