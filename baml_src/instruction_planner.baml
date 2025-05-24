
class Tool {
  name string @description("The name of the tool function")
  description string @description("Description of what the tool does")
  parameters Parameter[] @description("List of parameters the tool accepts")
  returnType string @description("The type of value this tool returns")
}

// Define the Parameter type for tool inputs
class Parameter {
  name string @description("The name of the parameter")
  type string @description("The data type of the parameter (string, number, boolean, etc.)")
  description string @description("Description of the parameter")
  required bool @description("Whether the parameter is required")
}

// Define the ToolCall type for tool execution steps
class ToolCall {
  toolName string @description("The name of the tool to call")
  arguments map<string, string> @description("Map of argument name to value")
  resultName string @description("Name to assign to the result of this tool call")
  description string @description("Human-readable description of this step")
  dependsOn string[] @description("List of previous step resultNames this step depends on")
}

// Define the Plan type
class Plan {
  steps ToolCall[] @description("The sequence of tool calls to execute")
}

// The main function that generates a plan from instructions and available tools
function GeneratePlan(instructions: string, tools: Tool[]) -> Plan {
  client "openai/gpt-4"
  
  prompt #"
    You are a planning assistant that converts natural language instructions into a sequence of tool calls.

    Available tools:
    {% for tool in tools %}
    - {{ tool.name }}: {{ tool.description }}
      Parameters:
      {% for param in tool.parameters %}
        - {{ param.name }} ({{ param.type }}{% if param.required %}, required{% endif %}): {{ param.description }}
      {% endfor %}
      Returns: {{ tool.returnType }}
    {% endfor %}

    User instructions: {{ instructions }}

    Create a plan to carry out these instructions using the available tools. For each step:
    1. Identify which tool to use
    2. Determine the arguments for the tool call
    3. Name the result that will be produced
    4. Specify any dependencies on previous steps

    {{ ctx.output_format }}
  "#
}

// Test case for the Math operations example
test MathOperationsTest {
  functions [GeneratePlan]
  args {
    instructions "Get the sum of ten and twenty, then multiply it by hundred"
    tools [
      {
        name "sum"
        description "Adds two numbers together"
        parameters [
          {
            name "a"
            type "number"
            description "First number to add"
            required true
          },
          {
            name "b"
            type "number"
            description "Second number to add"
            required true
          }
        ]
        returnType "number"
      },
      {
        name "multiply"
        description "Multiplies two numbers together"
        parameters [
          {
            name "a"
            type "number"
            description "First number to multiply"
            required true
          },
          {
            name "b"
            type "number"
            description "Second number to multiply"
            required true
          }
        ]
        returnType "number"
      },
      {
        name "subtract"
        description "Subtracts second number from the first"
        parameters [
          {
            name "a"
            type "number"
            description "Number to subtract from"
            required true
          },
          {
            name "b"
            type "number"
            description "Number to subtract"
            required true
          }
        ]
        returnType "number"
      },
      {
        name "divide"
        description "Divides first number by the second"
        parameters [
          {
            name "a"
            type "number"
            description "Numerator"
            required true
          },
          {
            name "b"
            type "number"
            description "Denominator (cannot be zero)"
            required true
          }
        ]
        returnType "number"
      }
    ]
  }
}
