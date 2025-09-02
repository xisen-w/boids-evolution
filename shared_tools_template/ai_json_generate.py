"""
AI JSON Generator Tool - Structured JSON generation using Azure OpenAI
"""

def execute(parameters, context=None):
    """
    Generate structured JSON data using Azure OpenAI.
    
    Parameters:
    - prompt: Description of what JSON structure to generate
    - schema: Optional JSON schema or example structure
    - format_type: Type of JSON to generate (object, array, config, data, etc.)
    - temperature: Creativity level (0.0-1.0, default 0.1 for consistency)
    
    Returns:
    - Dictionary with generated JSON and metadata
    """
    try:
        # Import Azure client
        import sys
        import os
        import json
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
                "result": "Please provide a 'prompt' parameter describing the JSON to generate"
            }
        
        schema = parameters.get('schema', '')
        format_type = parameters.get('format_type', 'object')
        temperature = float(parameters.get('temperature', 0.1))
        
        # Validate parameters
        temperature = max(0.0, min(1.0, temperature))
        
        # Build system prompt for JSON generation
        system_content = """You are a JSON data generator. You must respond with valid JSON only.
        
Rules:
1. Always return valid, parseable JSON
2. Follow the user's specifications exactly
3. Use appropriate data types (strings, numbers, booleans, arrays, objects)
4. Include realistic sample data
5. Ensure all JSON is properly formatted and escaped
6. Do not include any text outside the JSON structure"""
        
        # Add schema guidance if provided
        if schema:
            system_content += f"\n\nFollow this schema or example structure:\n{schema}"
        
        # Add format type guidance
        format_guides = {
            'object': "Generate a JSON object with key-value pairs.",
            'array': "Generate a JSON array with multiple items.",
            'config': "Generate a configuration JSON with settings and options.",
            'data': "Generate realistic sample data in JSON format.",
            'api': "Generate JSON that could be returned from an API endpoint.",
            'schema': "Generate a JSON schema definition."
        }
        
        if format_type in format_guides:
            system_content += f"\n\nFormat type: {format_guides[format_type]}"
        
        # Create Azure client and generate JSON
        client = AzureOpenAIClient()
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
        
        # Use JSON mode for guaranteed valid JSON
        json_response = client.chat_to_json(messages, temperature=temperature)
        
        # Check if response contains an error
        if "error" in json_response:
            return {
                "success": False,
                "error": f"JSON generation failed: {json_response.get('error', 'Unknown error')}",
                "result": json_response,
                "prompt": prompt,
                "settings": {
                    "temperature": temperature,
                    "format_type": format_type,
                    "schema": schema
                }
            }
        
        # Validate that we got proper JSON
        try:
            # Re-serialize to ensure it's valid JSON
            json_string = json.dumps(json_response, indent=2)
            
            return {
                "success": True,
                "result": json_response,
                "json_string": json_string,
                "prompt": prompt,
                "settings": {
                    "temperature": temperature,
                    "format_type": format_type,
                    "schema": schema
                },
                "structure_info": {
                    "type": type(json_response).__name__,
                    "keys": list(json_response.keys()) if isinstance(json_response, dict) else None,
                    "length": len(json_response) if isinstance(json_response, (list, dict)) else None
                }
            }
            
        except (TypeError, ValueError) as e:
            return {
                "success": False,
                "error": f"Invalid JSON structure: {str(e)}",
                "result": json_response
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool execution error: {str(e)}",
            "result": "Failed to generate JSON"
        } 