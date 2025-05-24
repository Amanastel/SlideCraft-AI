from typing import Dict, Any, List, Callable, Union, Optional
from planner import Plan, ToolCall

class Executor:
    """
    Executes a plan by calling the appropriate tools for each step.
    """
    def __init__(self, tools: Dict[str, Callable]):
        """
        Initialize the executor with a dictionary of tool implementations.
        
        Args:
            tools (Dict[str, Callable]): A dictionary mapping tool names to their implementations
        """
        self.tools = tools
        self.results = {}  # Store results of each step
    
    def execute_plan(self, plan: Plan) -> Any:
        """
        Execute a plan step by step.
        
        Args:
            plan (Plan): The plan to execute
            
        Returns:
            Any: The result of the final step in the plan
        """
        if not plan.steps:
            return None
        
        # Execute each step in order
        for step in plan.steps:
            result = self._execute_step(step)
            # Store the result for future steps to use
            self.results[step.result_name] = result
        
        # Return the result of the final step
        final_step = plan.steps[-1]
        return self.results[final_step.result_name]
    
    def _execute_step(self, step: ToolCall) -> Any:
        """
        Execute a single step in the plan.
        
        Args:
            step (ToolCall): The step to execute
            
        Returns:
            Any: The result of executing the step
        """
        if step.tool_name not in self.tools:
            raise ValueError(f"Tool '{step.tool_name}' not found in available tools")
        
        # Resolve arguments that reference previous results
        resolved_args = {}
        for arg_name, arg_value in step.arguments.items():
            resolved_args[arg_name] = self._resolve_argument(arg_value)
        
        # Call the tool with resolved arguments
        return self.tools[step.tool_name](**resolved_args)
    
    def _resolve_argument(self, arg_value: Any) -> Any:
        """
        Resolve an argument value, handling references to previous results.
        
        Args:
            arg_value (Any): The argument value to resolve
            
        Returns:
            Any: The resolved argument value
        """
        # If the argument is a string that references a previous result
        if isinstance(arg_value, str):
            # Check if the argument is a reference to a previous result
            if arg_value in self.results:
                return self.results[arg_value]
            
            # Check if the argument is a string representation of a list
            if arg_value.startswith('[') and arg_value.endswith(']'):
                try:
                    # Parse the list and resolve each element
                    elements = arg_value[1:-1].split(',')
                    resolved_elements = []
                    for element in elements:
                        element = element.strip()
                        # Remove quotes if present
                        if element.startswith('"') and element.endswith('"'):
                            element = element[1:-1]
                        # Check if element is a reference to a previous result
                        if element in self.results:
                            resolved_elements.append(self.results[element])
                        else:
                            try:
                                # Try to convert to int or float
                                if '.' in element:
                                    resolved_elements.append(float(element))
                                else:
                                    resolved_elements.append(int(element))
                            except ValueError:
                                resolved_elements.append(element)
                    return resolved_elements
                except Exception as e:
                    # If parsing fails, return the original string
                    print(f"Warning: Failed to parse list argument '{arg_value}': {e}")
            
            # Handle JSON object-like references (e.g., "{task.id}")
            if arg_value.startswith('{') and arg_value.endswith('}'):
                reference = arg_value[1:-1].split('.')
                if len(reference) == 2 and reference[0] in self.results:
                    result = self.results[reference[0]]
                    if hasattr(result, reference[1]):
                        return getattr(result, reference[1])
                    elif isinstance(result, dict) and reference[1] in result:
                        return result[reference[1]]
            
            # Try to convert to appropriate type
            try:
                # Check if it's a number
                if '.' in arg_value:
                    return float(arg_value)
                try:
                    return int(arg_value)
                except ValueError:
                    # Not an integer, return as is
                    return arg_value
            except Exception:
                # If conversion fails, return as is
                return arg_value
        
        return arg_value


# Simple implementations for basic math operations
def math_sum(**kwargs):
    """Add two numbers."""
    # Extract values from various possible parameter names
    val1 = None
    val2 = None
    
    # Try to extract first value from various possible parameter names
    for param_name in ['a', 'num1', 'number1', 'addend1', 'augend', 'x', 'val1', 'arg1']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val1 = kwargs[param_name]
            break
    
    # Try to extract second value from various possible parameter names
    for param_name in ['b', 'num2', 'number2', 'addend2', 'y', 'val2', 'arg2']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val2 = kwargs[param_name]
            break
            
    # Handle the case when a single 'addend' parameter is provided
    if 'addend' in kwargs and kwargs['addend'] is not None:
        if val1 is None:
            val1 = kwargs['addend']
        elif val2 is None:
            val2 = kwargs['addend']
    
    # If 'numbers' parameter is provided, use that
    if 'numbers' in kwargs and isinstance(kwargs['numbers'], list) and len(kwargs['numbers']) >= 2:
        val1 = kwargs['numbers'][0]
        val2 = kwargs['numbers'][1]
    
    # Default values if not found
    val1 = 0 if val1 is None else val1
    val2 = 0 if val2 is None else val2
    
    # Convert to numeric if they're strings
    if isinstance(val1, str):
        try:
            val1 = float(val1) if '.' in val1 else int(val1)
        except (ValueError, TypeError):
            val1 = 0
    
    if isinstance(val2, str):
        try:
            val2 = float(val2) if '.' in val2 else int(val2)
        except (ValueError, TypeError):
            val2 = 0
    
    return val1 + val2

def math_subtract(**kwargs):
    """Subtract b from a."""
    # Extract values from various possible parameter names
    val1 = None
    val2 = None
    
    # Try to extract first value from various possible parameter names
    for param_name in ['a', 'num1', 'number1', 'minuend', 'x', 'val1', 'arg1']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val1 = kwargs[param_name]
            break
    
    # Try to extract second value from various possible parameter names
    for param_name in ['b', 'num2', 'number2', 'subtrahend', 'y', 'val2', 'arg2']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val2 = kwargs[param_name]
            break
    
    # Default values if not found
    val1 = 0 if val1 is None else val1
    val2 = 0 if val2 is None else val2
    
    # Convert to numeric if they're strings
    if isinstance(val1, str):
        try:
            val1 = float(val1) if '.' in val1 else int(val1)
        except (ValueError, TypeError):
            val1 = 0
    
    if isinstance(val2, str):
        try:
            val2 = float(val2) if '.' in val2 else int(val2)
        except (ValueError, TypeError):
            val2 = 0
    
    return val1 - val2

def math_multiply(**kwargs):
    """Multiply two numbers."""
    # Extract values from various possible parameter names
    val1 = None
    val2 = None
    
    # Try to extract first value from various possible parameter names
    for param_name in ['a', 'num1', 'number1', 'multiplicand', 'x', 'val1', 'arg1']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val1 = kwargs[param_name]
            break
    
    # Try to extract second value from various possible parameter names
    for param_name in ['b', 'num2', 'number2', 'multiplier', 'y', 'val2', 'arg2']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val2 = kwargs[param_name]
            break
    
    # If 'numbers' parameter is provided, use that
    if 'numbers' in kwargs and isinstance(kwargs['numbers'], list) and len(kwargs['numbers']) >= 2:
        val1 = kwargs['numbers'][0]
        val2 = kwargs['numbers'][1]
    
    # Default values if not found
    val1 = 1 if val1 is None else val1
    val2 = 1 if val2 is None else val2
    
    # Convert to numeric if they're strings
    if isinstance(val1, str):
        try:
            val1 = float(val1) if '.' in val1 else int(val1)
        except (ValueError, TypeError):
            val1 = 1
    
    if isinstance(val2, str):
        try:
            val2 = float(val2) if '.' in val2 else int(val2)
        except (ValueError, TypeError):
            val2 = 1
    
    return val1 * val2

def math_divide(**kwargs):
    """Divide a by b."""
    # Extract values from various possible parameter names
    val1 = None
    val2 = None
    
    # Try to extract first value from various possible parameter names
    for param_name in ['a', 'num1', 'number1', 'dividend', 'numerator', 'x', 'val1', 'arg1']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val1 = kwargs[param_name]
            break
    
    # Try to extract second value from various possible parameter names
    for param_name in ['b', 'num2', 'number2', 'divisor', 'denominator', 'y', 'val2', 'arg2']:
        if param_name in kwargs and kwargs[param_name] is not None:
            val2 = kwargs[param_name]
            break
    
    # Default values if not found
    val1 = 0 if val1 is None else val1
    val2 = 1 if val2 is None else val2
    
    # Convert to numeric if they're strings
    if isinstance(val1, str):
        try:
            val1 = float(val1) if '.' in val1 else int(val1)
        except (ValueError, TypeError):
            val1 = 0
    
    if isinstance(val2, str):
        try:
            val2 = float(val2) if '.' in val2 else int(val2)
        except (ValueError, TypeError):
            val2 = 1
    
    if val2 == 0:
        raise ValueError("Cannot divide by zero")
    
    return val1 / val2

# Create a dictionary of basic math tools
MATH_TOOLS = {
    "sum": math_sum,
    "subtract": math_subtract,
    "multiply": math_multiply,
    "divide": math_divide
}

def execute_math_plan(plan: Plan) -> Union[int, float]:
    """
    Execute a math plan using the basic math tools.
    
    Args:
        plan (Plan): The plan to execute
        
    Returns:
        Union[int, float]: The result of executing the plan
    """
    executor = Executor(MATH_TOOLS)
    return executor.execute_plan(plan)

# Export the executor functions and tools
__all__ = ["Executor", "execute_math_plan", "MATH_TOOLS"]
