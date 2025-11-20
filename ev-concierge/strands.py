import boto3
import json
import os
import inspect
from typing import Callable, List, Any, get_type_hints
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
        self.parameters = self._extract_parameters()
        
    def _extract_parameters(self):
        """Extract parameter schema from function signature"""
        sig = inspect.signature(self.func)
        type_hints = get_type_hints(self.func)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, str)
            
            # Map Python types to JSON schema types
            json_type = "string"
            if param_type == int:
                json_type = "integer"
            elif param_type == float:
                json_type = "number"
            elif param_type == bool:
                json_type = "boolean"
            elif param_type == list:
                json_type = "array"
            elif param_type == dict:
                json_type = "object"
            
            properties[param_name] = {"type": json_type}
            
            # Mark as required if no default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
        
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
        """
        Run the agent with tool calling support.
        Implements the full Claude tool use protocol with Bedrock.
        """
        tool_calls = []
        
        # Build tool specifications for Claude
        tool_specs = []
        tool_map = {}  # Map tool names to Tool objects
        
        for tool in tools:
            tool_map[tool.name] = tool
            tool_specs.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters
            })
        
        # Initialize conversation with system prompt and user message
        messages = [{
            "role": "user",
            "content": user_prompt
        }]
        
        # Agentic loop: keep calling Claude until we get a final response
        for iteration in range(max_iterations):
            # Prepare request body
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "system": system_prompt,
                "messages": messages,
                "temperature": 0.7
            }
            
            # Add tools if available
            if tool_specs:
                request_body["tools"] = tool_specs
            
            # Call Bedrock
            try:
                # Debug: Print request
                print(f"\n🔍 Strands SDK - Iteration {iteration + 1}")
                print(f"   Tools available: {[t['name'] for t in tool_specs]}")
                if iteration == 0 and tool_specs:
                    print(f"   Tool schemas:")
                    for tool_spec in tool_specs:
                        print(f"      - {tool_spec['name']}: {tool_spec.get('input_schema', {}).get('required', [])}")
                
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body)
                )
                
                result = json.loads(response['body'].read())
                
                # Debug: Print response
                print(f"   Stop reason: {result.get('stop_reason')}")
                print(f"   Content blocks: {len(result.get('content', []))}")
                for idx, block in enumerate(result.get('content', [])):
                    print(f"      Block {idx}: type={block.get('type')}")
                
                # Check stop reason
                stop_reason = result.get('stop_reason')
                assistant_content = result.get('content', [])
                
                # Add assistant response to conversation
                messages.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                
                # If Claude wants to use tools, execute them
                if stop_reason == 'tool_use':
                    tool_results = []
                    
                    print(f"   🔧 Claude wants to use tools!")
                    
                    for content_block in assistant_content:
                        if content_block.get('type') == 'tool_use':
                            tool_name = content_block['name']
                            tool_input = content_block['input']
                            tool_use_id = content_block['id']
                            
                            print(f"   📞 Calling tool: {tool_name}")
                            print(f"      Input: {tool_input}")
                            
                            # Execute the tool
                            try:
                                tool_func = tool_map[tool_name]
                                result = tool_func(**tool_input)
                                
                                print(f"      ✅ Result: {result}")
                                
                                # Record the tool call
                                tool_calls.append(ToolCall(
                                    tool_name=tool_name,
                                    input=tool_input,
                                    result=result
                                ))
                                
                                # Prepare tool result for Claude
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": json.dumps(result)
                                })
                                
                            except Exception as e:
                                # Handle tool execution errors
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": json.dumps({"error": str(e)}),
                                    "is_error": True
                                })
                    
                    # Send tool results back to Claude
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                    # Continue the loop to get Claude's next response
                    continue
                
                # If we got a final answer (end_turn), extract text and return
                elif stop_reason == 'end_turn':
                    final_text = ""
                    for content_block in assistant_content:
                        if content_block.get('type') == 'text':
                            final_text += content_block['text']
                    
                    return StrandsResponse(
                        final_response=final_text,
                        tool_calls=tool_calls
                    )
                
                # Handle other stop reasons
                else:
                    # Extract any text content
                    final_text = ""
                    for content_block in assistant_content:
                        if content_block.get('type') == 'text':
                            final_text += content_block['text']
                    
                    return StrandsResponse(
                        final_response=final_text or "No response generated",
                        tool_calls=tool_calls
                    )
                    
            except Exception as e:
                # Handle API errors
                return StrandsResponse(
                    final_response=f"Error calling Bedrock: {str(e)}",
                    tool_calls=tool_calls
                )
        
        # Max iterations reached
        return StrandsResponse(
            final_response="Max iterations reached without final answer",
            tool_calls=tool_calls
        )
