# AI Planner & Executor

A powerful natural language system that converts text instructions into executable plans with tool calls and executes them automatically.

## Overview

The AI Planner & Executor is a complete system that takes natural language instructions and available tools as input, produces a structured execution plan, and then executes that plan using the appropriate tool implementations. It breaks down complex instructions into logical steps, identifies the appropriate tools for each step, and executes them in the correct order with proper dependency management.

## Features

- **Planning Features**
  - Convert natural language instructions into structured execution plans
  - Define dependencies between steps in a plan
  - Support for various tool types with strongly typed parameters
  - Stream partial results during plan generation
  - Detailed step descriptions and result naming

- **Execution Features**
  - Execute plans by calling the appropriate tools for each step
  - Resolve arguments that reference results from previous steps
  - Handle nested object references using dot notation
  - Convert argument types automatically (strings to numbers, etc.)
  - Built-in math operations library

## Installation

Ensure you have the required dependencies:

```bash
pip install baml-py python-dotenv
```

Set up your environment variables in a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Planning & Execution

```python
from planner import generate_plan
from executor import Executor

# Define your tools
math_tools = [
    {
        "name": "sum",
        "description": "Adds two numbers together",
        "parameters": [
            {
                "name": "a",
                "type": "number",
                "description": "First number to add",
                "required": True
            },
            {
                "name": "b",
                "type": "number",
                "description": "Second number to add",
                "required": True
            }
        ],
        "returnType": "number"
    },
    # ... other tools
]

# Define tool implementations
tool_implementations = {
    "sum": lambda a, b: float(a) + float(b),
    # ... other implementations
}

# Generate a plan
instructions = "Get the sum of ten and twenty, then multiply it by hundred"
plan = generate_plan(instructions, math_tools)

# Print the plan
for i, step in enumerate(plan.steps, 1):
    print(f"Step {i}: Use tool '{step.tool_name}' with arguments {step.arguments}")
    print(f"   Result name: {step.result_name}")
    print(f"   Description: {step.description}")
    if step.depends_on:
        print(f"   Depends on: {', '.join(step.depends_on)}")

# Execute the plan
executor = Executor(tool_implementations)
result = executor.execute_plan(plan)
print(f"Final result: {result}")
```

### Using Built-in Math Tools

The executor comes with a built-in set of math operations that handle common parameter names and type conversions:

```python
from planner import generate_plan
from executor import execute_math_plan, MATH_TOOLS

# Generate a plan
instructions = "Get the sum of ten and twenty, then multiply it by hundred"
math_tools = [
    {
        "name": "sum",
        "description": "Adds two numbers together",
        "parameters": [
            {"name": "a", "type": "number", "description": "First number", "required": True},
            {"name": "b", "type": "number", "description": "Second number", "required": True}
        ],
        "returnType": "number"
    },
    {
        "name": "multiply",
        "description": "Multiplies two numbers together",
        "parameters": [
            {"name": "a", "type": "number", "description": "First number", "required": True},
            {"name": "b", "type": "number", "description": "Second number", "required": True}
        ],
        "returnType": "number"
    }
]

plan = generate_plan(instructions, math_tools)

# Execute the plan using built-in math tools
result = execute_math_plan(plan)
print(f"Result: {result}")  # Output: 3000.0
```

### Streaming Plan Generation

```python
from planner import generate_plan_stream

# Generate a plan with streaming updates
plan = generate_plan_stream(instructions, math_tools)
```

## Tool Definition

Tools are defined using a structured format:

```python
tool = {
    "name": "tool_name",                      # Name of the tool
    "description": "What the tool does",      # Description of the tool
    "parameters": [                           # List of parameters
        {
            "name": "param_name",             # Parameter name
            "type": "string|number|boolean",  # Parameter type
            "description": "Description",     # Parameter description
            "required": True|False            # Whether parameter is required
        },
        # ... more parameters
    ],
    "returnType": "return_type"               # Type of return value
}
```

## Examples

### Math Operations with Execution

```python
from planner import generate_plan
from executor import execute_math_plan

instructions = "Calculate (25 + 15) * 3 - 10"
math_tools = [
    {"name": "sum", "description": "Adds numbers", "parameters": [...], "returnType": "number"},
    {"name": "multiply", "description": "Multiplies numbers", "parameters": [...], "returnType": "number"},
    {"name": "subtract", "description": "Subtracts numbers", "parameters": [...], "returnType": "number"}
]

plan = generate_plan(instructions, math_tools)

# Print the plan
print(plan)

# Execute the plan
result = execute_math_plan(plan)
print(f"Result: {result}")  # Output: 110.0
```

Example plan output:
```
Step 1: Use tool 'sum' with arguments {'a': '25', 'b': '15'}
   Result name: sum_result
   Description: Calculate the sum of 25 and 15

Step 2: Use tool 'multiply' with arguments {'a': 'sum_result', 'b': '3'}
   Result name: multiply_result
   Description: Multiply the sum by 3
   Depends on: sum_result

Step 3: Use tool 'subtract' with arguments {'a': 'multiply_result', 'b': '10'}
   Result name: final_result
   Description: Subtract 10 from the product
   Depends on: multiply_result
```

### Task Management with Execution

```python
from planner import generate_plan
from executor import Executor

# Define tool implementations
task_tool_implementations = {
    "create_task": lambda title: {"id": "123", "title": title},
    "set_priority": lambda task_id, priority: {"id": task_id, "priority": priority},
    "assign_task": lambda task_id, user_id: {"id": task_id, "assignee": user_id},
    "set_due_date": lambda task_id, due_date: {"id": task_id, "due_date": due_date}
}

task_instructions = "Create a high priority task called 'Complete quarterly report' and assign it to user 12345 with a due date of 2025-06-30"
task_tools = [
    {"name": "create_task", "description": "Creates a new task", "parameters": [...], "returnType": "object"},
    {"name": "set_priority", "description": "Sets task priority", "parameters": [...], "returnType": "object"},
    {"name": "assign_task", "description": "Assigns a task", "parameters": [...], "returnType": "object"},
    {"name": "set_due_date", "description": "Sets due date", "parameters": [...], "returnType": "object"}
]

task_plan = generate_plan(task_instructions, task_tools)

# Execute the task plan
executor = Executor(task_tool_implementations)
result = executor.execute_plan(task_plan)
print(f"Final task: {result}")
# Output: {'id': '123', 'due_date': '2025-06-30'}
```

## How the Executor Works

The `Executor` class takes a dictionary of tool implementations and executes a plan step by step:

1. **Tool Resolution**: Maps tool names from the plan to their implementations
2. **Argument Resolution**: Processes each argument before passing it to a tool:
   - Resolves references to previous step results (e.g., `sum_result`)
   - Handles nested object references using dot notation (e.g., `{task.id}`)
   - Converts string values to appropriate types (numbers, lists, etc.)
3. **Step Execution**: Calls each tool with resolved arguments and stores the result
4. **Result Storage**: Maintains a dictionary of results for use by subsequent steps

### Built-in Math Tools

The executor includes robust implementations for basic math operations:

- **sum**: Adds two numbers together
- **subtract**: Subtracts one number from another
- **multiply**: Multiplies two numbers together
- **divide**: Divides one number by another

These tools handle various parameter names (e.g., `a`, `num1`, `addend1`) and automatically convert string values to numbers.

## Project Structure

- `planner.py`: Core functionality for generating plans
- `planner_example.py`: Examples demonstrating planner usage
- `executor.py`: Core functionality for executing plans
- `executor_example.py`: Examples demonstrating executor usage
- `test_planner.py`: Unit tests for the planner
- `test_executor.py`: Unit tests for the executor
- `baml_src/instruction_planner.baml`: BAML definition of the planner
- `baml_src/main.baml`: BAML definition of the tool structure
- `baml_client/`: BAML client for interacting with language models

## Testing

Run the tests to ensure everything is working correctly:

```bash
python -m unittest test_planner.py test_executor.py
```

## License

This project is available under the MIT License. See the LICENSE file for more details.


