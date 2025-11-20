import boto3
import json
import os
from typing import Callable, List, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ToolCall:
    tool_name: str
    input: dict
    result: Any

@dataclass
class StrandsResponse:
    final_response: str
    tool_calls: List[ToolCall]

class Tool:
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or ""
        
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Strands:
    def __init__(self, model_id: str, region: str):
        self.model_id = model_id
        
        # Build boto3 client config with credentials from environment
        client_config = {
            'region_name': region,
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY')
        }
        
        # Add session token if present (for temporary credentials)
        session_token = os.getenv('AWS_SESSION_TOKEN')
        if session_token:
            client_config['aws_session_token'] = session_token
        
        self.bedrock = boto3.client('bedrock-runtime', **client_config)
    
    def run(self, system_prompt: str, user_prompt: str, tools: List[Tool], max_iterations: int = 5) -> StrandsResponse:
        tool_calls = []
        
        # Build tool descriptions
        tool_specs = []
        for tool in tools:
            tool_specs.append({
                "name": tool.name,
                "description": tool.description
            })
        
        # Create messages
        messages = [{
            "role": "user",
            "content": f"{system_prompt}\n\n{user_prompt}\n\nAvailable tools: {json.dumps(tool_specs, indent=2)}"
        }]
        
        # Call Bedrock
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": messages,
                "temperature": 0.7
            })
        )
        
        result = json.loads(response['body'].read())
        final_response = result['content'][0]['text']
        
        return StrandsResponse(
            final_response=final_response,
            tool_calls=tool_calls
        )
