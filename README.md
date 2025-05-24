# Instruction Planner

A powerful natural language instruction parser that converts text instructions into executable plans with tool calls.

## Overview

The Instruction Planner is a system that takes natural language instructions and available tools as input, then produces a structured execution plan. It breaks down complex instructions into logical steps and identifies the appropriate tools to use for each step.

## Features

- Convert natural language instructions into structured execution plans
- Define dependencies between steps in a plan
- Support for various tool types with strongly typed parameters
- Stream partial results during plan generation
- Detailed step descriptions and result naming

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

### Basic Usage

```python
from planner import generate_plan

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

# Generate a plan
instructions = "Get the sum of ten and twenty, then multiply it by hundred"
plan = generate_plan(instructions, math_tools)

# Execute the plan
for i, step in enumerate(plan.steps, 1):
    print(f"Step {i}: Use tool '{step.tool_name}' with arguments {step.arguments}")
    print(f"   Result name: {step.result_name}")
    print(f"   Description: {step.description}")
    if step.depends_on:
        print(f"   Depends on: {', '.join(step.depends_on)}")
```

### Streaming Mode

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

### Math Operations

```python
instructions = "Get the sum of ten and twenty, then multiply it by hundred"
math_plan = generate_plan(instructions, math_tools)
```

Example output:
```
Step 1: Use tool 'sum' with arguments {'a': '10', 'b': '20'}
   Result name: sum_result
   Description: Get the sum of ten and twenty

Step 2: Use tool 'multiply' with arguments {'a': 'sum_result', 'b': '100'}
   Result name: final_result
   Description: Multiply the sum by hundred
   Depends on: sum_result
```

### Task Management

```python
task_instructions = "Create a high priority task called 'Complete quarterly report' and assign it to user 12345 with a due date of 2025-06-30"
task_plan = generate_plan(task_instructions, task_tools)
```

Example output:
```
Step 1: Use tool 'create_task' with arguments {'title': 'Complete quarterly report'}
   Result name: task
   Description: Create a new task with the name 'Complete quarterly report'

Step 2: Use tool 'set_priority' with arguments {'task_id': '{task.id}', 'priority': 'high'}
   Result name: priority_set_task
   Description: Set the task's priority to high
   Depends on: task

Step 3: Use tool 'assign_task' with arguments {'task_id': '{priority_set_task.id}', 'user_id': '12345'}
   Result name: assigned_task
   Description: Assign the task to user 12345
   Depends on: priority_set_task

Step 4: Use tool 'set_due_date' with arguments {'task_id': '{assigned_task.id}', 'due_date': '2025-06-30'}
   Result name: final_task
   Description: Set the task's due date to 2025-06-30
   Depends on: assigned_task
```

## Project Structure

- `planner.py`: Core functionality for generating plans
- `planner_example.py`: Examples demonstrating planner usage
- `test_planner.py`: Unit tests for the planner
- `baml_src/instruction_planner.baml`: BAML definition of the planner
- `baml_client/`: BAML client for interacting with language models

## Testing

Run the tests to ensure everything is working correctly:

```bash
python -m unittest test_planner.py
```


