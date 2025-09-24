def execute(parameters, context=None):
    """
    Advanced Prompt Engineering Tool - Leverages AI text generation with sophisticated prompt techniques.
    
    This tool demonstrates how to use context.call_tool() to compose with existing AI tools
    while adding advanced prompt engineering techniques like few-shot learning, chain-of-thought,
    and structured prompting.
    
    Args:
        parameters (dict): Dictionary containing:
            - 'task': string (required) - The main task or question
            - 'domain': string (optional) - Domain context (e.g., 'poetry', 'science', 'business')
            - 'style': string (optional) - Output style (e.g., 'analytical', 'creative', 'technical')
            - 'examples': list (optional) - Few-shot examples for the prompt
            - 'constraints': string (optional) - Additional constraints or requirements
            
    Returns:
        dict: Result with generated content and metadata
    """
    try:
        # Extract parameters
        task = parameters.get('task', '')
        domain = parameters.get('domain', 'general')
        style = parameters.get('style', 'analytical')
        examples = parameters.get('examples', [])
        constraints = parameters.get('constraints', '')
        
        if not task:
            return {'error': 'No task provided for prompt engineering.'}
        
        # Build sophisticated prompt using advanced techniques
        prompt_parts = []
        
        # 1. System Context
        prompt_parts.append(f"You are an expert {domain} analyst with deep expertise in {style} thinking.")
        
        # 2. Task Definition
        prompt_parts.append(f"TASK: {task}")
        
        # 3. Few-shot Learning (if examples provided)
        if examples:
            prompt_parts.append("EXAMPLES:")
            for i, example in enumerate(examples[:3], 1):  # Limit to 3 examples
                if isinstance(example, dict) and 'input' in example and 'output' in example:
                    prompt_parts.append(f"Example {i}:")
                    prompt_parts.append(f"Input: {example['input']}")
                    prompt_parts.append(f"Output: {example['output']}")
                else:
                    prompt_parts.append(f"Example {i}: {example}")
        
        # 4. Chain of Thought Instructions
        prompt_parts.append("APPROACH:")
        prompt_parts.append("1. First, analyze the core requirements and context")
        prompt_parts.append("2. Break down the problem into logical components")
        prompt_parts.append("3. Apply domain-specific knowledge and techniques")
        prompt_parts.append("4. Synthesize insights with clear reasoning")
        prompt_parts.append("5. Present findings in a structured, actionable format")
        
        # 5. Constraints and Requirements
        if constraints:
            prompt_parts.append(f"CONSTRAINTS: {constraints}")
        
        # 6. Output Format
        prompt_parts.append("OUTPUT FORMAT:")
        prompt_parts.append("- Provide clear, well-reasoned analysis")
        prompt_parts.append("- Use specific examples and evidence")
        prompt_parts.append("- Structure your response logically")
        prompt_parts.append("- Include actionable insights or recommendations")
        
        # Combine all parts
        full_prompt = "\n\n".join(prompt_parts)
        
        # Call the ai_text_generate tool with enhanced parameters
        if context:
            # Use context to call the AI text generation tool
            ai_params = {
                'prompt': full_prompt,
                'temperature': 0.7,  # Balanced creativity
                'max_tokens': 800,   # Substantial response
                'style': style
            }
            
            result = context.call_tool('ai_text_generate', ai_params)
            
            if result and result.get('success'):
                return {
                    'success': True,
                    'result': result.get('result', ''),
                    'prompt_techniques_used': [
                        'system_context',
                        'few_shot_learning' if examples else 'zero_shot',
                        'chain_of_thought',
                        'structured_formatting',
                        'domain_expertise'
                    ],
                    'metadata': {
                        'domain': domain,
                        'style': style,
                        'examples_count': len(examples),
                        'prompt_length': len(full_prompt),
                        'composed_with': 'ai_text_generate'
                    }
                }
            else:
                return {
                    'error': 'Failed to generate content with AI tool',
                    'ai_error': result.get('error', 'Unknown error') if result else 'No response'
                }
        else:
            return {
                'error': 'No context provided to call ai_text_generate tool.',
                'fallback_prompt': full_prompt[:200] + "..." if len(full_prompt) > 200 else full_prompt
            }
            
    except Exception as e:
        return {'error': f'Prompt engineering failed: {str(e)}'}
