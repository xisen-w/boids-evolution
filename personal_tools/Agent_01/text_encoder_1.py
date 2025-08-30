"""
text_encoder_1 - Encodes text using Caesar cipher
Created by: Agent_01
Energy Reward: 5
"""

def execute(parameters, context=None):
    """Encode text with Caesar cipher"""
    try:
        text = str(parameters.get('text', ''))
        shift = int(parameters.get('shift', 3))
        
        result = ''
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - base + shift) % 26
                result += chr(base + shifted)
            else:
                result += char
                
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "result": f"Error: {e}"}
