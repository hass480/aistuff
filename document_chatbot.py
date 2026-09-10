"""
Document-grounded chatbot -- ask questions about a specific text file.

This is the "naive but works" version of RAG (retrieval-augmented
generation): instead of relying on whatever Claude already knows, we
hand it a specific document as context and tell it to answer ONLY
based on that document. No embeddings or vector search yet -- we're
just pasting the whole file into the system prompt. That's fine as
long as the document is small enough to fit; once you try this on
something huge (a whole book, hundreds of files), you'll hit a real
limit -- and THAT'S the moment real retrieval (searching for just the
relevant chunk instead of sending everything) starts to matter. You
don't need it yet, so we're not building it yet.

Setup: same as always -- pip install -r requirements.txt, a .env file
with your real ANTHROPIC_API_KEY, and this script + DOCUMENT_PATH
below in the same folder.

Run with:
    python document_chatbot.py
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5"  # verify exact ID in the Console if this errors

# The file to ground answers in. Swap this to any .txt file you want
# to ask questions about -- notes, an assignment, whatever.
DOCUMENT_PATH = "resume.txt"

with open(DOCUMENT_PATH, "r", encoding="utf-8") as f:
    document_text = f.read()

SYSTEM_PROMPT = f"""
You answer questions about the document below. Only use information
that's actually in the document. If something isn't in there, say
"That's not in the document" instead of guessing or using outside
knowledge.

DOCUMENT:
{document_text}
"""

conversation = []

print("=== Document Chatbot ===")
print(f"Ask me anything about {DOCUMENT_PATH}. Type 'quit' to stop.\n")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "quit":
        print("\nBye.")
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=conversation,
    )

    reply = response.content[0].text
    print(f"\nClaude: {reply}\n")

    conversation.append({"role": "assistant", "content": reply})