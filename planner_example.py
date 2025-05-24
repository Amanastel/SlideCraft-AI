from planner import generate_plan, Plan, ToolCall

# Example 1: Math operations
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
    {
        "name": "subtract",
        "description": "Subtracts second number from the first",
        "parameters": [
            {
                "name": "a",
                "type": "number",
                "description": "Number to subtract from",
                "required": True
            },
            {
                "name": "b",
                "type": "number",
                "description": "Number to subtract",
                "required": True
            }
        ],
        "returnType": "number"
    },
    {
        "name": "multiply",
        "description": "Multiplies two numbers together",
        "parameters": [
            {
                "name": "a",
                "type": "number",
                "description": "First number to multiply",
                "required": True
            },
            {
                "name": "b",
                "type": "number",
                "description": "Second number to multiply",
                "required": True
            }
        ],
        "returnType": "number"
    },
    {
        "name": "divide",
        "description": "Divides first number by the second",
        "parameters": [
            {
                "name": "a",
                "type": "number",
                "description": "Numerator",
                "required": True
            },
            {
                "name": "b",
                "type": "number",
                "description": "Denominator (cannot be zero)",
                "required": True
            }
        ],
        "returnType": "number"
    }
]

# Example 2: Task management tools
task_tools = [
    {
        "name": "create_task",
        "description": "Creates a new task with title and optional description",
        "parameters": [
            {
                "name": "title",
                "type": "string",
                "description": "Task title",
                "required": True
            },
            {
                "name": "description",
                "type": "string",
                "description": "Optional task description",
                "required": False
            }
        ],
        "returnType": "task"
    },
    {
        "name": "assign_task",
        "description": "Assigns a task to a user",
        "parameters": [
            {
                "name": "task_id",
                "type": "string",
                "description": "ID of the task",
                "required": True
            },
            {
                "name": "user_id",
                "type": "string",
                "description": "ID of the user",
                "required": True
            }
        ],
        "returnType": "boolean"
    },
    {
        "name": "set_due_date",
        "description": "Sets the due date for a task",
        "parameters": [
            {
                "name": "task_id",
                "type": "string",
                "description": "ID of the task",
                "required": True
            },
            {
                "name": "due_date",
                "type": "string",
                "description": "Due date in YYYY-MM-DD format",
                "required": True
            }
        ],
        "returnType": "boolean"
    },
    {
        "name": "set_priority",
        "description": "Sets the priority level for a task",
        "parameters": [
            {
                "name": "task_id",
                "type": "string",
                "description": "ID of the task",
                "required": True
            },
            {
                "name": "priority",
                "type": "string",
                "description": "Priority level (high, medium, low)",
                "required": True
            }
        ],
        "returnType": "boolean"
    }
]

def run_planner_examples():
    print("EXAMPLE 1: MATH OPERATIONS")
    print("-" * 50)
    math_instructions = "Get the sum of ten and twenty, then multiply it by hundred"
    math_plan = generate_plan(math_instructions, math_tools)
    print(f"Instructions: {math_instructions}")
    print("\nGenerated Plan:")
    for i, step in enumerate(math_plan.steps, 1):
        print(f"Step {i}: Use tool '{step.tool_name}' with arguments {step.arguments}")
        print(f"   Result name: {step.result_name}")
        print(f"   Description: {step.description}")
        if step.depends_on:
            print(f"   Depends on: {', '.join(step.depends_on)}")
        print()
    print("=" * 80 + "\n")

    print("EXAMPLE 2: TASK MANAGEMENT")
    print("-" * 50)
    task_instructions = "Create a high priority task called 'Complete quarterly report' and assign it to user 12345 with a due date of 2025-06-30"
    task_plan = generate_plan(task_instructions, task_tools)
    print(f"Instructions: {task_instructions}")
    print("\nGenerated Plan:")
    for i, step in enumerate(task_plan.steps, 1):
        print(f"Step {i}: Use tool '{step.tool_name}' with arguments {step.arguments}")
        print(f"   Result name: {step.result_name}")
        print(f"   Description: {step.description}")
        if step.depends_on:
            print(f"   Depends on: {', '.join(step.depends_on)}")
        print()

if __name__ == "__main__":
    run_planner_examples()
