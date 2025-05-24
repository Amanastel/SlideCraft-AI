import unittest
from planner import generate_plan, Plan, ToolCall
from executor import Executor, execute_math_plan, MATH_TOOLS

class TestExecutor(unittest.TestCase):
    def setUp(self):
        # Define common test tools
        self.math_tools = [
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
        
    def test_simple_plan_execution(self):
        """Test executing a simple plan with predefined steps."""
        # Create a simple plan manually
        steps = [
            ToolCall(
                tool_name="sum",
                arguments={"a": "10", "b": "20"},
                result_name="sum_result",
                description="Add 10 and 20",
                depends_on=[]
            ),
            ToolCall(
                tool_name="multiply",
                arguments={"a": "sum_result", "b": "100"},
                result_name="final_result",
                description="Multiply the sum by 100",
                depends_on=["sum_result"]
            )
        ]
        plan = Plan(steps)
        
        # Execute the plan
        result = execute_math_plan(plan)
        
        # Assert the result is correct
        self.assertEqual(result, 3000)

    def test_divide_sum_plan(self):
        """Test executing 'divide by 10, the sum of 20 and 30'."""
        instructions = "divide by 10, the sum of 20 and 30"
        plan = generate_plan(instructions, self.math_tools)
        result = execute_math_plan(plan)
        self.assertEqual(result, 5)
        
    def test_add_divide_plan(self):
        """Test executing 'add 20 and 30, divide it by the sum of 2 and 3'."""
        instructions = "add 20 and 30, divide it by the sum of 2 and 3"
        plan = generate_plan(instructions, self.math_tools)
        result = execute_math_plan(plan)
        self.assertEqual(result, 10)
        
    def test_complex_math_plan(self):
        """Test executing a more complex math plan."""
        instructions = "multiply the sum of 5 and 3 by the difference of 10 and 4"
        plan = generate_plan(instructions, self.math_tools)
        result = execute_math_plan(plan)
        self.assertEqual(result, 48)  # (5+3)*(10-4) = 8*6 = 48
        
    def test_error_handling(self):
        """Test error handling for divide by zero."""
        # Create a plan that attempts to divide by zero
        steps = [
            ToolCall(
                tool_name="divide",
                arguments={"a": "10", "b": "0"},
                result_name="result",
                description="Divide 10 by 0",
                depends_on=[]
            )
        ]
        plan = Plan(steps)
        
        # Assert that executing the plan raises a ValueError
        with self.assertRaises(ValueError):
            execute_math_plan(plan)
            
    def test_invalid_tool(self):
        """Test error handling for invalid tool names."""
        # Create a plan with an invalid tool name
        steps = [
            ToolCall(
                tool_name="invalid_tool",
                arguments={"a": "10", "b": "20"},
                result_name="result",
                description="Use an invalid tool",
                depends_on=[]
            )
        ]
        plan = Plan(steps)
        
        # Assert that executing the plan raises a ValueError
        with self.assertRaises(ValueError):
            execute_math_plan(plan)

if __name__ == "__main__":
    unittest.main()
