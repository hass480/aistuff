import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

MODEL = "claude-haiku-4-5"

response = client.messages.create(
    model=MODEL,
    max_tokens=200,
    messages=[
        {"role": "user", "content": "In one sentence, who won the battle of austerlitz"}
    ],
)

reply_text = response.content[0].text
print("\nClaude's reply:")
print(reply_text)
