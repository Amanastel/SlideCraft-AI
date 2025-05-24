from planner import generate_plan
from executor import execute_math_plan, Executor, MATH_TOOLS

def run_executor_examples():
    # Example 1: "Get the sum of ten and twenty, then multiply it by hundred"
    print("EXAMPLE 1: Sum of 10 and 20, multiply by 100")
    print("-" * 50)
    example1_instructions = "Get the sum of ten and twenty, then multiply it by hundred"
    
    # Define the math tools for the planner
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
    
    # Generate the plan
    plan = generate_plan(example1_instructions, math_tools)
    
    # Display the plan
    print(f"Instructions: {example1_instructions}")
    print("\nGenerated Plan:")
    for i, step in enumerate(plan.steps, 1):
        print(f"Step {i}: Use tool '{step.tool_name}' with arguments {step.arguments}")
        print(f"   Result name: {step.result_name}")
    
    # Execute the plan
    result = execute_math_plan(plan)
    print(f"\nResult: {result}")
    print("\n" + "=" * 80 + "\n")
    
    # Test Input 1: "divide by 10, the sum of 20 and 30"
    print("TEST INPUT 1: Divide by 10, the sum of 20 and 30")
    print("-" * 50)
    test1_instructions = "divide by 10, the sum of 20 and 30"
    
    # Generate the plan
    test1_plan = generate_plan(test1_instructions, math_tools)
    
    # Display the plan
    print(f"Instructions: {test1_instructions}")
    print("\nGenerated Plan:")
    for i, step in enumerate(test1_plan.steps, 1):
        print(f"Step {i}: Use tool '{step.tool_name}' with arguments {step.arguments}")
        print(f"   Result name: {step.result_name}")
    
    # Execute the plan
    test1_result = execute_math_plan(test1_plan)
    print(f"\nResult: {test1_result}")
    print(f"Expected Result: 5")
    print("\n" + "=" * 80 + "\n")
    
    # Test Input 2: "add 20 and 30, divide it by the sum of 2 and 3"
    print("TEST INPUT 2: Add 20 and 30, divide it by the sum of 2 and 3")
    print("-" * 50)
    test2_instructions = "add 20 and 30, divide it by the sum of 2 and 3"
    
    # Generate the plan
    test2_plan = generate_plan(test2_instructions, math_tools)
    
    # Display the plan
    print(f"Instructions: {test2_instructions}")
    print("\nGenerated Plan:")
    for i, step in enumerate(test2_plan.steps, 1):
        print(f"Step {i}: Use tool '{step.tool_name}' with arguments {step.arguments}")
        print(f"   Result name: {step.result_name}")
    
    # Execute the plan
    test2_result = execute_math_plan(test2_plan)
    print(f"\nResult: {test2_result}")
    print(f"Expected Result: 10")

if __name__ == "__main__":
    run_executor_examples()
