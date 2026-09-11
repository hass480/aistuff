"""
Tool calling + memory -- the two previous lessons combined.

chatbot.py showed conversation memory (a growing `conversation` list
resent every call). calculator_tool.py showed tool calling, but only
for a single question. This file wires tool calling into an ongoing
chat loop, so Claude can reach for the calculator whenever it needs to,
in the middle of a normal back-and-forth conversation.

New wrinkle vs. calculator_tool.py: Claude might ask to call a tool,
get the result, and still not be done -- it could ask for another tool
call before giving you a final answer. So instead of "ask once, maybe
run a tool once", we loop: keep resolving tool_use blocks and calling
Claude again until it replies with no tool_use blocks left, which
means it's ready to give you a real, final answer for that turn.

Run with:
    python tool_chatbot.py
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5"  # verify exact ID in the Console if this errors


def calculate(a, b, operation):
    """Do actual, exact arithmetic -- no guessing involved."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        return f"Unknown operation: {operation}"


tools = [
    {
        "name": "calculate",
        "description": "Perform exact arithmetic between two numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number"},
                "b": {"type": "number", "description": "The second number"},
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "Which operation to perform",
                },
            },
            "required": ["a", "b", "operation"],
        },
    }
]

conversation = []

print("=== Tool-Using Chatbot ===")
print("Type a message (try some math). Type 'quit' to stop.\n")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "quit":
        print("\nBye.")
        break

    conversation.append({"role": "user", "content": user_input})

    # Inner loop: keep going as long as Claude keeps asking for tool
    # calls. Most turns will run this exactly once and break out
    # immediately, but it can loop more than once if Claude needs
    # multiple tool calls to answer a single message.
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            tools=tools,
            messages=conversation,
        )

        # Claude's reply (text and/or tool_use blocks) goes into memory
        # as an assistant turn, same as any other reply would.
        conversation.append({"role": "assistant", "content": response.content})

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            # No tool requests left -- this is Claude's real, final
            # answer for this turn. Stop looping and print it.
            break

        # Run every requested tool call for real, and collect the
        # results. (Usually there's just one, but the API allows
        # Claude to ask for several at once.)
        tool_results = []
        for block in tool_use_blocks:
            print(f"\n[calling {block.name}({block.input})]")
            result = calculate(**block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                }
            )

        # All results go back as one "user" turn (a quirk of the API,
        # same as in calculator_tool.py), then we loop and call Claude
        # again so it can use them.
        conversation.append({"role": "user", "content": tool_results})

    reply_text = "".join(b.text for b in response.content if b.type == "text")
    print(f"\nClaude: {reply_text}\n")
