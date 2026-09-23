"""Day 2, Part D: ReAct agent with simple tools."""

from config import client, MODEL


# -----------------------------
# TOOL 1: Get item price
# -----------------------------
def get_item_price(item_name):
    prices = {
        "t-shirt": 450,
        "id card": 30,
        "banner": 800,
    }

    item_name = item_name.strip().lower()

    return prices.get(item_name, "Price not found")


# -----------------------------
# TOOL 2: Calculator
# -----------------------------
def calculator(expression):
    try:
        return eval(expression, {"__builtins__": {}}, {})
    except Exception:
        return "Invalid calculation"


# -----------------------------
# REACT AGENT
# -----------------------------
def agent(question, max_steps=10):

    messages = [
        {
            "role": "system",
            "content": """
You are a ReAct agent for a college hackathon.

Use the available tools when you need information or calculations.

Available tools:

1. get_item_price(item_name)
   - Gets the price of a hackathon item.

2. calculator(expression)
   - Performs arithmetic calculations.

Follow this process:

Thought → Action → Observation → Thought → Action → Observation

When you have enough information, give the final answer.

All prices are in Indian Rupees (Rs.).
Do not use dollars ($).
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]

    for step in range(1, max_steps + 1):

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_item_price",
                        "description": "Get the price of a hackathon item.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "item_name": {
                                    "type": "string",
                                    "description": "Name of the item"
                                }
                            },
                            "required": ["item_name"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "calculator",
                        "description": "Calculate a mathematical expression.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "expression": {
                                    "type": "string",
                                    "description": "Mathematical expression"
                                }
                            },
                            "required": ["expression"]
                        }
                    }
                }
            ],
        )

        message = response.choices[0].message

        # If the model wants to use a tool
        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name
                arguments = eval(
                    tool_call.function.arguments,
                    {"__builtins__": {}},
                    {}
                )

                if tool_name == "get_item_price":
                    result = get_item_price(**arguments)

                elif tool_name == "calculator":
                    result = calculator(**arguments)

                else:
                    result = "Unknown tool"

                print(
                    f"step {step}: "
                    f"{tool_name}({arguments}) -> {result}"
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    }
                )

        else:
            # Final answer
            return message.content.strip()

    return "The agent reached the maximum number of steps."


if __name__ == "__main__":

    QUESTION = (
        "What is the total cost of 40 T-shirts, "
        "40 ID cards, and 10 banners for the college hackathon?"
    )

    print("QUESTION:", QUESTION)
    print("\n--- ReAct trace ---")

    answer = agent(QUESTION, max_steps=10)

    print("\nFINAL ANSWER:", answer)