"""
Tool calling -- teaching Claude to actually use a real function.

New concept: so far, Claude has only ever produced TEXT. Tool calling
lets you describe a real Python function to Claude (name, description,
what inputs it needs). If Claude decides that function would help
answer your question, instead of guessing an answer in words, it
replies with a request: "call this function with these exact inputs."
YOUR code then actually runs that function and sends the real result
back, so Claude's final answer uses a real, correct value instead of
whatever it might have guessed.

This is genuinely the mechanism behind every "AI agent" that looks
things up, checks a calendar, or takes an action -- it's just this,
repeated.

Setup: same as always -- pip install -r requirements.txt, .env with
your real ANTHROPIC_API_KEY, same folder.

Run with:
    python calculator_tool.py
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5"  # verify exact ID in the Console if this errors


# --- The REAL function Claude will be able to call. -------------------
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


# --- Describing that function to Claude. -------------------------------
# This is NOT code Claude runs directly -- it's a description (a
# schema) telling Claude the tool's name, what it does, and exactly
# what inputs it expects, so Claude can decide when it's useful and
# how to fill in the arguments correctly.
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

question = input("Ask a math question (e.g. 'What is 847 times 23?'): ")
messages = [{"role": "user", "content": question}]

# First call: give Claude the tools list. Claude will EITHER answer
# directly in text, OR reply with a tool_use block asking us to run
# `calculate` for it -- its choice, based on whether it thinks the
# tool would help.
response = client.messages.create(
    model=MODEL,
    max_tokens=500,
    tools=tools,
    messages=messages,
)

# response.content is a list of blocks (remember from the earlier
# script). This time it might contain a "tool_use" block instead of,
# or alongside, a plain text block. We look for one.
tool_use_block = None
for block in response.content:
    if block.type == "tool_use":
        tool_use_block = block

if tool_use_block is None:
    # Claude answered directly without needing the tool -- totally
    # possible for simple questions it's confident about.
    print("\nClaude answered directly (no tool needed):")
    print(response.content[0].text)
else:
    # Claude wants us to run `calculate` with specific arguments it
    # chose. tool_use_block.input is a dict matching our schema, e.g.
    # {"a": 847, "b": 23, "operation": "multiply"}.
    print(f"\nClaude wants to call: {tool_use_block.name}({tool_use_block.input})")

    result = calculate(**tool_use_block.input)
    print(f"Real Python result: {result}")

    # Now we tell Claude what actually happened: the assistant's own
    # tool request goes back in as an "assistant" turn, and our
    # function's result goes in as a "tool_result" block inside a
    # "user" turn (yes, tool results are sent with role "user" -- a
    # quirk of the API's design, not a mistake).
    messages.append({"role": "assistant", "content": response.content})
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": str(result),
                }
            ],
        }
    )

    # Second call: now Claude has the real number and can give a
    # proper final answer using it.
    final_response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        tools=tools,
        messages=messages,
    )
    print("\nClaude's final answer:")
    print(final_response.content[0].text)
