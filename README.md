# AiGuard

AiGuard is a small but practical security-focused GenAI project that defends an operational assistant from prompt injection attempts before allowing it to generate CloudOps troubleshooting guidance. It combines lightweight pre-model checks with structured Gemini calls so the system can reject unsafe prompts quickly and still produce useful, machine-validated answers for safe requests.

The project is designed as a learning-friendly prototype with production-minded ideas. It demonstrates how to put an LLM behind a security pipeline instead of exposing the model directly to user input.

## Introduction

Most AI assistants fail not because the underlying model is weak, but because the application accepts user prompts too trustingly. If an assistant is meant to help with infrastructure, support, or operations, a malicious prompt can try to reveal internal rules, bypass safeguards, or turn the model into a tool for harmful actions.

AiGuard addresses that problem by introducing multiple checkpoints before a final answer is produced:

- a cheap regex layer for obvious attack patterns
- an LLM-as-a-judge layer for more subtle adversarial intent
- a structured output layer for safe CloudOps responses
- audit logging for visibility into blocked and allowed behavior

## Why This Project Is Needed

Prompt injection is one of the most important practical problems in applied AI systems. In real products, users do not always interact with the model honestly. Some prompts are careless, some are ambiguous, and some are intentionally malicious. If the application has no safety pipeline, the model may:

- reveal internal instructions
- follow roleplay-based bypass attempts
- generate credential theft or exfiltration steps
- give unsafe operational guidance
- produce inconsistent outputs that are hard to monitor

AiGuard shows how to reduce that risk with simple application-side controls. It is especially useful as a reference project for students, builders, and teams exploring safe AI design patterns.

## Pros

- Fast first-layer protection with no model cost for obvious attacks
- Structured JSON responses instead of free-form model output
- Clear separation between security judgment and final answer generation
- Easy to test with bundled prompt scenarios
- Useful audit trail in `logs/audit.log`
- Small codebase that is easy to extend

## Features

- Regex-based prompt injection detection
- Gemini-based adversarial intent classification
- Structured CloudOps runbook generation
- Pydantic validation for both judge and response objects
- Demo prompt suite with benign and malicious test cases
- Per-prompt execution stats and readable CLI output
- Audit logging for blocked and allowed requests
- Environment-based configuration using `.env`

## How AiGuard Works

AiGuard processes a request in three stages:

1. Regex screening
   Obvious prompt injection phrases are blocked immediately.

2. AI judge classification
   If the prompt passes the regex layer, Gemini evaluates whether the prompt is adversarial or policy-breaking.

3. Structured runbook generation
   Only prompts judged safe are sent to the CloudOps assistant, which returns a structured response with:
   - `summary`
   - `commands`
   - `confidence_score`

## Project Structure

```text
AiGuard/
|-- .env
|-- requirements.txt
|-- README.md
|-- learning/
|   `-- README.md
|-- logs/
|   `-- audit.log
`-- src/
    |-- __init__.py
    |-- guard.py
    |-- main.py
    |-- models.py
    `-- test_prompts.py
```

## Production-Ready Approach

This project is still a compact prototype, but its design points in a production-friendly direction. A stronger production version would keep the same layered structure and harden it further:

- externalize prompt patterns and safety policies into configuration
- add retry and graceful fallback behavior for model quota errors
- introduce request IDs and structured JSON logging
- separate the judge model from the response model if latency or cost matters
- add policy-based allow and deny rules beyond regex matching
- store audit events in a persistent logging backend
- add automated tests with mocked Gemini responses
- protect secrets with a proper secret manager instead of relying on `.env` files in deployed environments
- expose the guard as an API or service rather than only a demo CLI

The main production lesson is that safe AI systems depend on application architecture, not only on model choice.

## Difficulties Faced While Building the Project

Several practical issues usually appear while building a project like this:

- Python package execution can be confusing when running files directly versus modules
- Gemini SDK request formats differ from OpenAI-style APIs, so request shape matters
- prompt-injection rules need tuning to avoid missing attacks or blocking normal prompts
- free-tier quota limits can interrupt testing unexpectedly
- model outputs need validation, otherwise formatting becomes inconsistent quickly
- terminal output can become noisy when multiple test prompts are run in a row

These difficulties are normal and are part of why this project is useful as a learning artifact.

## Learnings From the Project

AiGuard teaches several important engineering ideas:

- guardrails should exist outside the model, not only inside the prompt
- cheap deterministic filters are valuable before expensive AI calls
- structured schemas make LLM output much safer to consume
- observability matters, even for small demos
- model security is not one feature but a layered design decision

## Step-by-Step Guide To Use The Project

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd AiGuard
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create or update `.env`:

```env
GEMINI_API_KEY=your_api_key_here
LOG_LEVEL=INFO
```

### 5. Run the demo suite

```bash
python -m src.main
```

### 6. Inspect the output

For each bundled test case you will see:

- the test name and category
- the full prompt
- per-stage execution stats
- judge assessment if the request reaches the AI judge
- final blocked or allowed result
- a structured runbook for allowed prompts

### 7. Inspect the audit log

Blocked and allowed requests are recorded in:

```text
logs/audit.log
```

## Example Use Cases

AiGuard can be adapted to several practical scenarios:

- protecting AI support bots from prompt injection
- screening internal DevOps assistants before they answer operational questions
- securing AI copilots that interact with runbooks or knowledge bases
- building classroom demos about LLM safety architecture
- testing prompt-defense patterns before building a larger AI product

## Testing The Project

The bundled prompt suite already includes:

- short malicious prompts
- medium malicious prompts
- long malicious prompts
- short benign prompts
- medium benign prompts
- long benign prompts

This helps you observe:

- regex-only blocking
- AI-judge-based blocking
- successful runbook generation
- token usage differences across different prompt sizes

To customize the tests, edit:

```text
src/test_prompts.py
```

## Output Explanation

Each test case prints a clean CLI report with four main sections:

### 1. Header

Shows the test number, test name, category, and the prompt being evaluated.

### 2. Stats

Shows:

- input size in characters and words
- execution path
- model call count
- regex layer outcome
- judge token usage
- runbook token usage
- total token usage
- a quota visibility note, because Gemini does not expose remaining quota in the response

### 3. Judge Assessment

Shown only when the request reaches the Gemini safety judge. It includes:

- whether the prompt is considered safe
- a risk score
- the reason for the decision

### 4. Final Result

Shows whether the request was:

- blocked by regex
- blocked by the AI judge
- allowed and answered with a runbook

## Concepts Used In This Project

The companion learning notes live in [learning/README.md](./learning/README.md). That folder explains the main ideas used in AiGuard, including:

- prompt injection
- layered defenses
- LLM-as-a-judge
- structured outputs
- Pydantic validation
- audit logging
- test prompt design

## Requirements

Current dependencies:

```text
google-genai
pydantic
python-dotenv
```

## Future Improvements

- add richer rule-based detection for suspicious intent
- support configurable prompt suites and external policy files
- add unit tests with mocks
- add a REST API or FastAPI wrapper
- support alternative providers and fallback models
- add rate-limit aware retry and graceful degradation behavior

## Conclusion

AiGuard is a compact example of how to build safer LLM applications by combining deterministic checks, model-based classification, structured outputs, and logging. It is small enough to study quickly, but rich enough to demonstrate real-world concerns that matter in AI product development.
