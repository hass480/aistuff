"""
Document grounding + tool calling + memory -- all three pieces combined.

document_chatbot.py showed grounding: pasting a document into the system
prompt so Claude answers only from it. tool_chatbot.py showed tool
calling wired into an ongoing, memory-having conversation. This file
proves those two pieces are independent and composable: the `system`
prompt (what Claude knows) and `tools` (what Claude can do) are separate
arguments to the same API call, so nothing stops you from using both at
once.

Claude now has to make a three-way decision on every message: answer
from the document, call a tool, or say "that's not in the document."
Nothing here is new mechanically -- it's the exact same tool-resolution
loop from tool_chatbot.py, just with a system prompt added on top.

New tools: save_note and list_notes. calculate and count_letter are both
*pure* functions -- same inputs always produce the same output, and
nothing about the world changes when you call them. save_note is
different: it has a side effect (it actually writes to a real file,
notes.txt). This is a small step toward what real agents do -- take
actions that change state, not just answer questions.

list_notes shows why that distinction matters: it takes no arguments
at all (an empty input_schema is valid), and it has to re-read
notes.txt fresh every time it's called, because that file's contents
can change mid-conversation. Contrast with the resume document, which
is loaded once into the system prompt and never rechecked -- a static
snapshot vs. live state.

Run with:
    python document_tool_chatbot.py
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5"  # verify exact ID in the Console if this errors

DOCUMENT_PATH = "resume.txt"

with open(DOCUMENT_PATH, "r", encoding="utf-8") as f:
    document_text = f.read()

SYSTEM_PROMPT = f"""
You answer questions about the document below. Only use information
that's actually in the document -- if something isn't in there and no
available tool can help either, say "That's not in the document"
instead of guessing or using outside knowledge.

You also have tools available for exact calculations, letter counting,
saving a note, or listing saved notes. Use them whenever a question or
request needs one, even if it isn't about the document.

DOCUMENT:
{document_text}
"""


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


def count_letter(text, letter):
    """Count exact occurrences of `letter` in `text` -- no guessing."""
    return text.lower().count(letter.lower())


def save_note(text):
    """Append a note to notes.txt -- a real side effect, unlike the
    other two tools above."""
    with open("notes.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")
    return f"Saved: {text}"


def list_notes():
    """Read notes.txt fresh, right now -- unlike the resume document
    (loaded once at startup), this file can change mid-conversation,
    so we have to actually check it each time instead of trusting
    whatever Claude remembers writing earlier."""
    if not os.path.exists("notes.txt"):
        return "No notes saved yet."
    with open("notes.txt", "r", encoding="utf-8") as f:
        return f.read()


tool_functions = {
    "calculate": calculate,
    "count_letter": count_letter,
    "save_note": save_note,
    "list_notes": list_notes,
}

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
    },
    {
        "name": "count_letter",
        "description": "Count how many times a specific letter appears in a word or phrase.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The word or phrase to search"},
                "letter": {"type": "string", "description": "The single letter to count"},
            },
            "required": ["text", "letter"],
        },
    },
    {
        "name": "save_note",
        "description": "Save a short note for later by appending it to a notes file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The note text to save"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "list_notes",
        "description": "Read back every note saved so far in this session or earlier.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

conversation = []

print("=== Document + Tool Chatbot ===")
print(f"Ask me about {DOCUMENT_PATH}, or throw in some math / letter-counting. Type 'quit' to stop.\n")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "quit":
        print("\nBye.")
        break

    conversation.append({"role": "user", "content": user_input})

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=conversation,
        )

        conversation.append({"role": "assistant", "content": response.content})

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            break

        tool_results = []
        for block in tool_use_blocks:
            print(f"\n[calling {block.name}({block.input})]")
            function_to_call = tool_functions[block.name]
            result = function_to_call(**block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                }
            )

        conversation.append({"role": "user", "content": tool_results})

    reply_text = "".join(b.text for b in response.content if b.type == "text")
    print(f"\nClaude: {reply_text}\n")
