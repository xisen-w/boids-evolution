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
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
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
        client = AzureOpenAIClient()
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
        
        generated_text = client.chat(messages, temperature=temperature, max_tokens=max_tokens)
        
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