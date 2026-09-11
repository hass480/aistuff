# Project context: aistuff

## Who's building this and why

Zak is a CS student (also PM interning at Publicis Sapient, and running his
own project called Prometheus Initiative) learning **AI engineering** —
building and shipping products on top of existing models (Claude/GPT via
API), not training or fine-tuning models from scratch.

He explicitly prefers learning by building and asking questions as they come
up, over reading textbooks or structured courses cover-to-cover. When
suggesting next steps or explaining code, favor short, concrete increments
tied to something actually running, and explain *why* something works, not
just *that* it works.

Hadn't coded in about a year before starting this project, so keep
explanations of core Python mechanics welcome rather than assumed-obvious,
but don't be condescending — he picks things up fast once he sees them in
real, running code.

## Deliberate scope decision

Chose the "AI engineering" path (prompting, RAG, tool/agent use, working
with existing models via API) over "ML engineering" / from-scratch model
building. Sebastian Raschka's *Build a Large Language Model* book and a
large from-scratch ML curriculum were deliberately shelved as later,
optional deep-dives -- not needed for the current goal and should not be
suggested as a prerequisite for anything in this project.

## Files in this project

- `first_api_call.py` -- the first-ever API call: single question, no
  memory. Establishes the basic client/API-call pattern everything else
  builds on.
- `chatbot.py` -- adds real conversation memory: a growing `messages` list
  that gets resent in full on every call, since the API itself is
  stateless and remembers nothing on its own.
- `document_chatbot.py` -- a basic/naive form of RAG: answers questions
  grounded only in a document (currently `resume.txt`, gitignored for
  privacy) by pasting its full text into the system prompt. Known
  limitation, left in on purpose: this breaks down once a document is too
  big to fit in context. That limitation is the intended trigger for the
  next real increment (see below) -- don't "fix" it preemptively with
  embeddings until it's actually motivated by hitting the limit.
- `calculator_tool.py` -- tool/function calling: Claude can request a real
  Python function be run (exact arithmetic) instead of guessing an answer.
  Currently a standalone single-question demo, not yet wired into a full
  chat loop.
- `interrogation.py` -- an earlier mystery-game experiment (a suspect
  Claude roleplays, with a hidden secret backstory in the system prompt).
  Didn't land with Zak as a project direction; superseded by the plainer
  `chatbot.py`. Kept for reference, not a base to build on further unless
  he brings it back up himself.

## Setup

- `.env` (gitignored) holds `ANTHROPIC_API_KEY`. Loaded via
  `python-dotenv`'s `load_dotenv()`.
- `requirements.txt` lists `anthropic` and `python-dotenv`.
- Model IDs drift over time -- if a script errors with "model not found,"
  check the exact current ID in the Claude Console before assuming the
  code is wrong.
- Repo is pushed to `github.com/hass480/aistuff`. `.env` and `resume.txt`
  are gitignored (secrets and personal info, respectively) -- double check
  `git status` before any commit to make sure neither reappears staged.

## Concepts already covered (don't re-teach from scratch, but okay to
reference/reinforce)

APIs and clients, environment variables/`.env` for secrets (including a
real incident where a key got pasted in a chat and had to be revoked --
Zak is now appropriately careful about this), list indexing and response
content blocks, system prompts vs. the `messages` list, `while`/`break`
loops, f-strings, git/GitHub basics (including a real `.gitignore` file
that was accidentally created without its leading dot -- worth
double-checking file names like this if something isn't being ignored as
expected), and LF vs. CRLF line endings.

## Reference material (kept on hand, not required reading)

- Chip Huyen's *AI Engineering* -- conceptual/strategic reference, not a
  tutorial.
- *Building LLM-Powered Applications* by Valentina Alto -- more hands-on,
  application-layer, no fine-tuning required.
Don't push either as something to "go read" before continuing to build --
Zak prefers pulling from them situationally if a concept comes up.

## Natural next steps (pick up from here)

1. Wire tool-calling into the full chatbot loop (`calculator_tool.py` is
   currently a one-shot demo, not integrated into an ongoing conversation).
2. Real embeddings-based retrieval, once/if a document-grounded use case
   actually outgrows the "paste the whole file into the system prompt"
   approach in `document_chatbot.py`.
3. Beyond that: agents that combine memory + tools + planning are the
   long-term direction, but only introduce pieces as they become
   motivated by something Zak is actually trying to build, not as an
   abstract curriculum to complete.
