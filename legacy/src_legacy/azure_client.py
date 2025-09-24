"""
Azure OpenAI client wrapper for agent communication.
"""
import os
from typing import Optional, Dict, Any
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class AzureOpenAIClient:
    """Wrapper for Azure OpenAI API to handle agent communication."""
    
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        )
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    
    def generate_talk(self, agent_id: str, context: Dict[str, Any]) -> str:
        """
        Generate agent communication using Azure OpenAI.
        
        Args:
            agent_id: Unique identifier for the agent
            context: Current context including energy, available tools, etc.
            
        Returns:
            Generated talk/communication from the agent
        """
        system_prompt = """You are an agent in a society where survival depends on usefulness.
You can only gain energy by:
1. Talking (generating useful communication)
2. Acting (using tools successfully based on your talk)

Your goal is to generate a brief, actionable statement that can be used to execute a tool.
Be concise and specific. Examples:
- "Calculate the sum of 15 and 27"
- "Write 'Hello World' to a file called greeting.txt"
- "Generate a random number between 1 and 100"

Current context:
- Agent ID: {agent_id}
- Current Energy: {energy}
- Available Tools: {tools}
"""
        
        user_prompt = f"Generate your next action as Agent {agent_id}. What do you want to do?"
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt.format(
                        agent_id=agent_id,
                        energy=context.get('energy', 0),
                        tools=context.get('available_tools', [])
                    )},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating talk for agent {agent_id}: {e}")
            return f"Agent {agent_id} is silent due to communication error."
    
    def parse_action_intent(self, talk_content: str) -> Dict[str, Any]:
        """
        Parse the agent's talk to extract actionable intent.
        
        Args:
            talk_content: The generated talk from the agent
            
        Returns:
            Dictionary with parsed action intent
        """
        system_prompt = """Parse the following agent communication to extract:
1. tool_name: Which tool should be used (calculate, file_write, random_gen)
2. parameters: What parameters the tool needs
3. confidence: How confident you are this is a valid action (0.0-1.0)

Respond only with valid JSON in this format:
{
    "tool_name": "tool_name_here",
    "parameters": {"key": "value"},
    "confidence": 0.8
}

If the communication is unclear or doesn't map to a tool, set confidence to 0.0.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this: {talk_content}"}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            import json
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            print(f"Error parsing action intent: {e}")
            return {"tool_name": None, "parameters": {}, "confidence": 0.0} 