import unittest
from planner import generate_plan, Plan, ToolCall

class TestPlanner(unittest.TestCase):
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
        
        self.file_tools = [
            {
                "name": "read_file",
                "description": "Reads content from a file",
                "parameters": [
                    {
                        "name": "file_path",
                        "type": "string",
                        "description": "Path to the file",
                        "required": True
                    }
                ],
                "returnType": "string"
            },
            {
                "name": "write_file",
                "description": "Writes content to a file",
                "parameters": [
                    {
                        "name": "file_path",
                        "type": "string",
                        "description": "Path to the file",
                        "required": True
                    },
                    {
                        "name": "content",
                        "type": "string",
                        "description": "Content to write",
                        "required": True
                    }
                ],
                "returnType": "boolean"
            },
            {
                "name": "append_file",
                "description": "Appends content to a file",
                "parameters": [
                    {
                        "name": "file_path",
                        "type": "string",
                        "description": "Path to the file",
                        "required": True
                    },
                    {
                        "name": "content",
                        "type": "string",
                        "description": "Content to append",
                        "required": True
                    }
                ],
                "returnType": "boolean"
            }
        ]

    def test_math_operations(self):
        instructions = "Get the sum of ten and twenty, then multiply it by hundred"
        plan = generate_plan(instructions, self.math_tools)
        
        # Verify plan structure
        self.assertIsInstance(plan, Plan)
        self.assertTrue(len(plan.steps) >= 2)  # Should have at least 2 steps
        
        # Check if the first step uses sum
        self.assertEqual(plan.steps[0].tool_name, "sum")
        
        # Check if the second step uses multiply
        self.assertEqual(plan.steps[1].tool_name, "multiply")
        
        # Check that resultName and description fields exist
        self.assertTrue(hasattr(plan.steps[0], 'result_name'))
        self.assertTrue(hasattr(plan.steps[0], 'description'))
        
        # Verify that the second step depends on the first
        self.assertTrue(len(plan.steps[1].depends_on) > 0)

    def test_file_operations(self):
        instructions = "Read content from input.txt, add a header, and write it to output.txt"
        plan = generate_plan(instructions, self.file_tools)
        
        # Verify plan structure
        self.assertIsInstance(plan, Plan)
        self.assertTrue(len(plan.steps) >= 2)  # Should have at least 2 steps
        
        # Check if the plan includes reading and writing files
        tool_names = [step.tool_name for step in plan.steps]
        self.assertIn("read_file", tool_names)
        self.assertIn("write_file", tool_names)
        
        # Check the order: read should come before write
        read_index = tool_names.index("read_file")
        write_index = tool_names.index("write_file")
        self.assertLess(read_index, write_index)
        
        # Check dependencies
        write_step = plan.steps[write_index]
        self.assertTrue(len(write_step.depends_on) > 0)

    def test_complex_instructions(self):
        instructions = """
        Calculate the average of 10, 20, and 30.
        Then subtract 5 from the result.
        Finally, multiply by 2.
        """
        plan = generate_plan(instructions, self.math_tools)
        
        # Verify plan has at least 3 steps
        self.assertGreaterEqual(len(plan.steps), 3)
        
        # Check if steps follow a logical order for the calculation
        tool_names = [step.tool_name for step in plan.steps]
        
        # The plan should include subtract and multiply
        self.assertIn("subtract", tool_names)
        self.assertIn("multiply", tool_names)
        
        # Check that steps have dependencies
        for i in range(1, len(plan.steps)):
            self.assertTrue(len(plan.steps[i].depends_on) > 0, 
                           f"Step {i+1} should depend on previous steps")

if __name__ == "__main__":
    unittest.main()
