import os
from typing import List, Dict, Any, Callable, Union, Optional
from dotenv import load_dotenv
from baml_client.sync_client import b
from pydantic import BaseModel
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()

# Tool Parameter class
@dataclass
class Parameter:
    name: str
    type: str
    description: str
    required: bool = False

# Tool class
@dataclass
class Tool:
    name: str
    description: str
    parameters: List[Parameter]
    returnType: str

class ToolCall:
    """Represents a single tool call in the plan."""
    def __init__(self, tool_name: str, arguments: Dict[str, str], result_name: str = "", 
                 description: str = "", depends_on: List[str] = None):
        self.tool_name = tool_name
        self.arguments = arguments
        self.result_name = result_name
        self.description = description
        self.depends_on = depends_on or []
    
    def __repr__(self):
        args_str = ', '.join(f"{k}={v}" for k, v in self.arguments.items())
        deps_str = ', '.join(self.depends_on) if self.depends_on else ""
        return (f"ToolCall(tool_name='{self.tool_name}', arguments={{{args_str}}}, "
                f"result_name='{self.result_name}', description='{self.description}', "
                f"depends_on=[{deps_str}])")

class Plan:
    """Represents a plan consisting of multiple tool calls."""
    def __init__(self, steps: List[ToolCall]):
        self.steps = steps
    
    def __repr__(self):
        steps_str = ',\n  '.join(repr(step) for step in self.steps)
        return f"Plan(steps=[\n  {steps_str}\n])"

def convert_dict_to_tool(tool_dict: Dict[str, Any]) -> Tool:
    """
    Convert a dictionary representation of a tool to a Tool object.
    
    Args:
        tool_dict (Dict[str, Any]): Dictionary with tool information
        
    Returns:
        Tool: Tool object
    """
    parameters = []
    params_dict = tool_dict.get("parameters", {})
    
    if isinstance(params_dict, dict):
        # Handle the old format where parameters is a dict
        for param_name, param_desc in params_dict.items():
            parameters.append(Parameter(
                name=param_name,
                type="string",  # Default type
                description=param_desc,
                required=False  # Default required
            ))
    elif isinstance(params_dict, list):
        # Handle the new format where parameters is a list of Parameter objects
        for param in params_dict:
            parameters.append(Parameter(
                name=param.get("name", ""),
                type=param.get("type", "string"),
                description=param.get("description", ""),
                required=param.get("required", False)
            ))
    
    return Tool(
        name=tool_dict.get("name", ""),
        description=tool_dict.get("description", ""),
        parameters=parameters,
        returnType=tool_dict.get("returnType", "any")
    )

def generate_plan(instructions: str, tools: List[Dict[str, Any]]) -> Plan:
    """
    Generate a plan based on natural language instructions and available tools.
    
    Args:
        instructions (str): Natural language instructions
        tools (List[Dict[str, Any]]): List of available tools with their descriptions
        
    Returns:
        Plan: A plan consisting of tool calls
    """
    # Convert the tools dictionaries to Tool objects
    tool_objects = [convert_dict_to_tool(tool) for tool in tools]
    
    # Force the model to use the exact tool names by explicitly adding them to the instructions
    enhanced_instructions = f"{instructions}\n\nNOTE: You MUST use ONLY the exact tool names provided: {', '.join([tool.name for tool in tool_objects])}"
    
    # BAML's function guarantees GeneratePlan to always return a Plan type
    response = b.GeneratePlan(enhanced_instructions, tool_objects)
    
    # Convert BAML response to our Plan object
    tool_calls = []
    for step in response.steps:
        # Try to find a matching tool name by case-insensitive comparison
        tool_name = step.toolName
        for tool in tool_objects:
            if tool.name.lower() == step.toolName.lower():
                tool_name = tool.name
                break
        
        tool_calls.append(ToolCall(
            tool_name=tool_name,
            arguments=step.arguments,
            result_name=step.resultName,
            description=step.description,
            depends_on=step.dependsOn
        ))
    
    return Plan(tool_calls)

def generate_plan_stream(instructions: str, tools: List[Dict[str, Any]]) -> Plan:
    """
    Generate a plan with streaming response based on natural language instructions and available tools.
    
    Args:
        instructions (str): Natural language instructions
        tools (List[Dict[str, Any]]): List of available tools with their descriptions
        
    Returns:
        Plan: A plan consisting of tool calls
    """
    # Convert the tools dictionaries to Tool objects
    tool_objects = [convert_dict_to_tool(tool) for tool in tools]
    
    # Force the model to use the exact tool names by explicitly adding them to the instructions
    enhanced_instructions = f"{instructions}\n\nNOTE: You MUST use ONLY the exact tool names provided: {', '.join([tool.name for tool in tool_objects])}"
    
    stream = b.stream.GeneratePlan(enhanced_instructions, tool_objects)
    for msg in stream:
        print(msg)  # This will be a partial response
    
    # This will be a Plan type
    final = stream.get_final_response()
    
    # Convert BAML response to our Plan object
    tool_calls = []
    for step in final.steps:
        # Try to find a matching tool name by case-insensitive comparison
        tool_name = step.toolName
        for tool in tool_objects:
            if tool.name.lower() == step.toolName.lower():
                tool_name = tool.name
                break
                
        tool_calls.append(ToolCall(
            tool_name=tool_name,
            arguments=step.arguments,
            result_name=step.resultName,
            description=step.description,
            depends_on=step.dependsOn
        ))
    
    return Plan(tool_calls)
