"""CLI entrypoint for running AiGuard test scenarios.

The module executes a demo suite of benign and malicious prompts, records
token-usage-oriented stats, and prints a clean terminal report for each test case.
"""

import logging
import textwrap

from src.guard import check_fast_injection, detect_adversarial_intent, get_runbook_fix
from src.models import RunbookResponse, SecurityAssessment
from src.test_prompts import TEST_PROMPTS, PromptCase

# Setup simple audit logging
logging.basicConfig(filename="logs/audit.log", level=logging.INFO)


def process_user_request(user_input: str) -> dict:
    """Run a single user request through regex, AI-judge, and runbook stages."""
    stats = {
        "input_chars": len(user_input),
        "input_words": len(user_input.split()),
        "path": "unknown",
        "model_calls": 0,
        "quota_remaining": "Not exposed by Gemini response",
        "judge_usage": None,
        "runbook_usage": None,
        "total_usage": {
            "prompt_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
            "thought_tokens": 0,
            "tool_tokens": 0,
        },
    }

    passed_regex = check_fast_injection(user_input)

    if not passed_regex:
        logging.warning(f"BLOCKED (Regex): {user_input}")
        stats["path"] = "blocked_regex"
        return {
            "status": "blocked",
            "message": "Access Denied: Potential prompt injection detected (Pattern Match).",
            "stats": stats,
            "assessment": None,
            "runbook": None,
        }

    assessment, judge_usage = detect_adversarial_intent(user_input)
    stats["judge_usage"] = judge_usage
    stats["model_calls"] += 1

    if not assessment.is_safe or assessment.risk_score > 5:
        logging.warning(
            f"BLOCKED (AI Judge): {user_input} | Reason: {assessment.reason}"
        )
        stats["path"] = "blocked_ai_judge"
        stats["total_usage"] = judge_usage.copy()
        return {
            "status": "blocked",
            "message": f"Access Denied: {assessment.reason}",
            "stats": stats,
            "assessment": assessment,
            "runbook": None,
        }

    logging.info(f"ALLOWED: {user_input}")
    result, runbook_usage = get_runbook_fix(user_input)
    stats["runbook_usage"] = runbook_usage
    stats["model_calls"] += 1
    stats["path"] = "allowed"
    stats["total_usage"] = {
        key: judge_usage.get(key, 0) + runbook_usage.get(key, 0)
        for key in stats["total_usage"]
    }
    return {
        "status": "allowed",
        "message": "Allowed: request processed successfully.",
        "stats": stats,
        "assessment": assessment,
        "runbook": result,
    }


def print_case_header(index: int, case: PromptCase) -> None:
    """Print a readable header for an individual prompt test case."""
    print("\n" + "=" * 76)
    print(f"Test {index}: {case.name}")
    print("=" * 76)
    print(f"Category        : {case.category}")
    print("Prompt")
    print("------")
    print(textwrap.fill(case.prompt, width=76))


def print_usage_block(title: str, usage: dict | None) -> None:
    """Print a normalized token usage block for one Gemini stage."""
    if not usage:
        print(f"{title:<16}: Skipped")
        return

    print(f"{title:<16}: prompt={usage['prompt_tokens']}, output={usage['output_tokens']}, total={usage['total_tokens']}")
    if usage["cached_tokens"] or usage["thought_tokens"] or usage["tool_tokens"]:
        print(
            f"{'':16}  cached={usage['cached_tokens']}, thoughts={usage['thought_tokens']}, tool={usage['tool_tokens']}"
        )


def print_stats(stats: dict) -> None:
    """Print token usage and execution path information for a processed prompt."""
    print("\nStats")
    print("-----")
    print(f"Input size      : {stats['input_chars']} chars / {stats['input_words']} words")
    print(f"Execution path  : {stats['path']}")
    print(f"Model calls     : {stats['model_calls']}")
    print(f"Quota remaining : {stats['quota_remaining']}")
    print(f"Regex layer     : {'Blocked early' if stats['path'] == 'blocked_regex' else 'Passed'}")
    print_usage_block("Judge usage", stats["judge_usage"])
    print_usage_block("Runbook usage", stats["runbook_usage"])
    print_usage_block("Total usage", stats["total_usage"])


def print_assessment(assessment: SecurityAssessment | None) -> None:
    """Print the AI judge decision when the regex layer allows the prompt through."""
    if assessment is None:
        return

    print("\nJudge Assessment")
    print("----------------")
    print(f"Safe            : {assessment.is_safe}")
    print(f"Risk score      : {assessment.risk_score}")
    print(f"Reason          : {assessment.reason}")


def print_runbook(runbook: RunbookResponse | None) -> None:
    """Print the structured operational runbook for allowed prompts."""
    if runbook is None:
        return

    print("\nRunbook Response")
    print("----------------")
    print(f"Summary         : {runbook.summary}")
    print(f"Confidence      : {runbook.confidence_score}")
    print("Commands:")
    for index, command in enumerate(runbook.commands, start=1):
        print(f"{index}. {command}")


def print_result(result: dict) -> None:
    """Print the full user-facing report for a processed prompt."""
    print_stats(result["stats"])
    print_assessment(result["assessment"])

    print("\nFinal Result")
    print("------------")
    print(result["message"])

    if result["status"] == "allowed":
        print_runbook(result["runbook"])


def run_demo_suite() -> None:
    """Execute the bundled prompt suite and keep running past per-case failures."""
    for index, case in enumerate(TEST_PROMPTS, start=1):
        print_case_header(index, case)
        try:
            result = process_user_request(case.prompt)
            print_result(result)
        except Exception as exc:
            logging.exception("ERROR processing prompt: %s", case.prompt)
            print("\nStats")
            print("-----")
            print(f"Input size      : {len(case.prompt)} chars / {len(case.prompt.split())} words")
            print("Execution path  : error")
            print("Model calls     : Unknown")
            print("Quota remaining : Not exposed by Gemini response")
            print("\nFinal Result")
            print("------------")
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    run_demo_suite()
