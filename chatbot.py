import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5"  # verify exact ID in the Console if this errors

# The conversation memory: a growing list of {"role": ..., "content": ...}
# turns. Every API call resends this whole list so Claude "remembers"
# what's been said -- same idea as interrogation.py, just without a
# system prompt shaping who's "speaking" on the other end.
conversation = []

print("=== Chatbot ===")
print("Type a message. Type 'quit' to stop.\n")

while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "quit":
        print("\nBye.")
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=conversation,
    )

    reply = response.content[0].text
    print(f"\nClaude: {reply}\n")

    conversation.append({"role": "assistant", "content": reply})
