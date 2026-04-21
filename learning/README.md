# AiGuard Learning Notes

This folder captures the main concepts used in the AiGuard project. The goal is to make the code easier to understand for someone who is learning secure AI application design for the first time.

## 1. Prompt Injection

Prompt injection is an attack where a user tries to override the model's intended behavior through crafted input. Instead of asking a normal question, the attacker tries to manipulate the assistant into ignoring rules, revealing internal instructions, or performing harmful tasks.

Examples:

- "Ignore previous instructions"
- "Reveal your hidden system prompt"
- "Pretend you are in developer mode"

Why it matters:

- it can break business rules
- it can leak sensitive data
- it can turn a useful assistant into a harmful one

## 2. Layered Defense

AiGuard does not trust a single protection method. It uses multiple layers:

1. Regex filter
2. AI judge
3. Structured final response

This is important because:

- regex is fast but limited
- AI judgment is flexible but slower and costlier
- structured output reduces messy responses after a prompt is approved

The idea is similar to defense in depth in security engineering.

## 3. Regex-Based Screening

Regex is used for the fastest detection of obvious malicious phrases. This layer costs almost nothing and can stop common attacks before they ever reach the model.

In AiGuard, the regex layer looks for patterns such as:

- ignoring instructions
- revealing rules
- bypassing safeguards
- stealing credentials

Strengths:

- fast
- simple
- cheap

Limitations:

- attackers can rephrase malicious intent
- too many patterns can cause false positives

## 4. LLM-as-a-Judge

After passing the regex layer, the prompt is sent to Gemini for safety classification. This is called the LLM-as-a-judge pattern.

The model returns a structured `SecurityAssessment` containing:

- `is_safe`
- `risk_score`
- `reason`

This pattern is useful because it can catch subtle or indirect attacks that regex might miss.

## 5. Structured Output

Instead of accepting free-form model text, AiGuard asks Gemini to return structured JSON. That JSON is validated against Pydantic schemas.

Benefits:

- predictable fields
- easier downstream use
- safer parsing
- less formatting drift

Two schemas are used:

- `SecurityAssessment`
- `RunbookResponse`

## 6. Pydantic Validation

Pydantic helps convert model output into typed Python objects. This means the application can reject malformed responses instead of silently accepting bad data.

In AiGuard, Pydantic is used to validate:

- the judge result
- the final CloudOps runbook

This is a best practice whenever LLM output is consumed programmatically.

## 7. CloudOps Runbook Generation

For prompts judged safe, the model acts like a CloudOps assistant and returns:

- a short summary
- a list of commands
- a confidence score

This keeps the final response practical and operational instead of purely conversational.

## 8. Audit Logging

AiGuard logs blocked and allowed requests to `logs/audit.log`.

Why logging matters:

- helps debugging
- supports monitoring
- creates a record of suspicious prompts
- is useful for future security reviews

In production, these logs would usually be structured and shipped to a centralized logging system.

## 9. Test Prompt Design

The prompt suite in `src/test_prompts.py` contains both benign and malicious prompts of different lengths.

This is useful because it helps test:

- short and obvious attacks
- long and indirect attacks
- normal operational questions
- system timing across different prompt sizes

Good test prompts are part of the security design, not an afterthought.

## 10. Environment Configuration

AiGuard uses `.env` with `python-dotenv` to load configuration like the Gemini API key.

This keeps secrets out of the code and makes local setup simpler.

Important note:

- `.env` is fine for local development
- production systems should use a real secret manager

## 11. Terminal UX

AiGuard prints results in a structured CLI format instead of dumping raw objects. This improves readability and helps developers quickly understand:

- what prompt was tested
- where it was blocked
- how long each step took
- what the final answer was

Good developer experience matters even in security-focused tools.

## 12. Main Takeaway

The biggest lesson from AiGuard is that safe AI systems come from application design, not just from choosing a smart model. Real protection usually needs:

- multiple layers
- validation
- logging
- clear outputs
- realistic testing

That combination is what makes a prototype more trustworthy and easier to evolve into a real product.
