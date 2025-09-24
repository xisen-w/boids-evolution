#!/usr/bin/env python3
"""
🎉 FUN AI TOOLS DEMO
Test the new AI-powered tools with creative examples!
"""

import sys
import os
import json

# Add paths
sys.path.append('src')
sys.path.append('shared_tools_template')

def demo_ai_text_generator():
    """Demo the AI text generation tool with fun examples."""
    print("🤖 AI TEXT GENERATOR DEMO")
    print("=" * 50)
    
    try:
        import ai_text_generate
        
        # Test cases with fun prompts
        demos = [
            {
                "name": "Creative Story",
                "params": {
                    "prompt": "Write a short story about an AI agent that discovers it can paint with mathematical equations",
                    "style": "creative",
                    "temperature": 0.8,
                    "max_tokens": 200
                }
            },
            {
                "name": "Technical Explanation", 
                "params": {
                    "prompt": "Explain how neural networks learn, but make it sound like a cooking recipe",
                    "style": "technical",
                    "temperature": 0.6,
                    "max_tokens": 150
                }
            },
            {
                "name": "Humorous Take",
                "params": {
                    "prompt": "Write a funny conversation between a programmer and their rubber duck about debugging",
                    "style": "humorous",
                    "temperature": 0.9,
                    "max_tokens": 180
                }
            },
            {
                "name": "Professional Email",
                "params": {
                    "prompt": "Write a professional email announcing that our AI agents have started their own startup company",
                    "style": "professional",
                    "temperature": 0.4,
                    "max_tokens": 120
                }
            }
        ]
        
        for i, demo in enumerate(demos, 1):
            print(f"\n📝 Demo {i}: {demo['name']}")
            print("-" * 30)
            print(f"Prompt: {demo['params']['prompt']}")
            print(f"Style: {demo['params']['style']} | Temp: {demo['params']['temperature']} | Tokens: {demo['params']['max_tokens']}")
            print()
            
            result = ai_text_generate.execute(demo['params'])
            
            if result.get('success'):
                print("✅ Generated Text:")
                print(f'"{result["result"]}"')
                print(f"\n📊 Stats: {result['word_count']} words, {result['char_count']} characters")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_ai_json_generator():
    """Demo the AI JSON generation tool with practical examples."""
    print("\n🔧 AI JSON GENERATOR DEMO")
    print("=" * 50)
    
    try:
        import ai_json_generate
        
        # Test cases with practical JSON structures
        demos = [
            {
                "name": "User Profile API",
                "params": {
                    "prompt": "Generate a user profile for a social media app with personal info, preferences, and settings",
                    "format_type": "api",
                    "temperature": 0.2
                }
            },
            {
                "name": "AI Agent Config",
                "params": {
                    "prompt": "Generate a configuration file for an AI agent with behavior settings, tool preferences, and learning parameters",
                    "format_type": "config",
                    "temperature": 0.1
                }
            },
            {
                "name": "Product Catalog",
                "params": {
                    "prompt": "Generate an array of AI-powered products with names, descriptions, prices, and features",
                    "format_type": "array",
                    "temperature": 0.3
                }
            },
            {
                "name": "Research Data Schema",
                "params": {
                    "prompt": "Generate a JSON schema for storing experimental results from AI agent interactions",
                    "format_type": "schema",
                    "temperature": 0.1
                }
            },
            {
                "name": "Custom Tool Metadata",
                "params": {
                    "prompt": "Generate metadata for a custom tool that can analyze sentiment in social media posts",
                    "schema": '{"name": "string", "description": "string", "parameters": {}, "capabilities": [], "ai_powered": "boolean"}',
                    "format_type": "data",
                    "temperature": 0.2
                }
            }
        ]
        
        for i, demo in enumerate(demos, 1):
            print(f"\n🔍 Demo {i}: {demo['name']}")
            print("-" * 30)
            print(f"Prompt: {demo['params']['prompt']}")
            print(f"Format: {demo['params']['format_type']} | Temp: {demo['params']['temperature']}")
            if 'schema' in demo['params']:
                print(f"Schema: {demo['params']['schema']}")
            print()
            
            result = ai_json_generate.execute(demo['params'])
            
            if result.get('success'):
                print("✅ Generated JSON:")
                print(result['json_string'])
                
                structure_info = result.get('structure_info', {})
                print(f"\n📊 Structure: Type={structure_info.get('type', 'unknown')}")
                if structure_info.get('keys'):
                    print(f"    Keys: {', '.join(structure_info['keys'][:5])}{'...' if len(structure_info['keys']) > 5 else ''}")
                if structure_info.get('length'):
                    print(f"    Length: {structure_info['length']} items")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

def demo_error_handling():
    """Demo error handling for both tools."""
    print("\n⚠️  ERROR HANDLING DEMO")
    print("=" * 50)
    
    try:
        import ai_text_generate
        import ai_json_generate
        
        print("🧪 Testing error cases...")
        
        # Test missing prompts
        print("\n1. Missing prompt test:")
        text_result = ai_text_generate.execute({})
        json_result = ai_json_generate.execute({})
        
        print(f"   Text tool: {'✅ Handled gracefully' if not text_result.get('success') else '❌ Should have failed'}")
        print(f"   JSON tool: {'✅ Handled gracefully' if not json_result.get('success') else '❌ Should have failed'}")
        
        # Test parameter validation
        print("\n2. Parameter validation test:")
        text_result = ai_text_generate.execute({
            "prompt": "Test",
            "temperature": 5.0,  # Invalid
            "max_tokens": 10000  # Invalid
        })
        
        if text_result.get('success'):
            settings = text_result.get('settings', {})
            temp_ok = settings.get('temperature', 0) <= 1.0
            tokens_ok = settings.get('max_tokens', 0) <= 1000
            print(f"   Parameter clamping: {'✅ Working' if temp_ok and tokens_ok else '❌ Not working'}")
        else:
            print("   Parameter validation: ❌ Tool failed unexpectedly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling demo failed: {e}")
        return False

def main():
    """Run all AI tools demos."""
    print("🚀 AI TOOLS SHOWCASE")
    print("=" * 60)
    print("Testing the new AI-powered tools in shared_tools_template!")
    print()
    
    # Check if Azure client is available
    try:
        from src.azure_client import AzureOpenAIClient
        print("✅ Azure OpenAI client available")
        
        # Check environment variables
        import os
        if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
            print("⚠️  Azure OpenAI credentials not set - tools will show connection errors")
            print("   Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY in .env file")
        else:
            print("✅ Azure OpenAI credentials configured")
    except ImportError:
        print("❌ Azure OpenAI client not available - tools will fail")
        return
    
    print()
    
    # Run demos
    results = []
    
    # Demo 1: Text Generation
    results.append(demo_ai_text_generator())
    
    # Demo 2: JSON Generation  
    results.append(demo_ai_json_generator())
    
    # Demo 3: Error Handling
    results.append(demo_error_handling())
    
    # Summary
    print("\n🎯 DEMO SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"Demos passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All demos completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Set up your Azure OpenAI credentials")
        print("   2. Run experiments with these AI tools")
        print("   3. Watch agents create amazing AI-powered tools!")
    else:
        print("⚠️  Some demos had issues - check Azure OpenAI setup")
    
    print(f"\n📁 New AI tools added to shared_tools_template:")
    print("   • ai_text_generate.py - Creative text generation")
    print("   • ai_json_generate.py - Structured JSON generation")
    print("   • Both tools include comprehensive tests!")

if __name__ == "__main__":
    main() 