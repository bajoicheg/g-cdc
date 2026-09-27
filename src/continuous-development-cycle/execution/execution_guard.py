"""CDC Execution Guard v1.

Prevents execution commands from degrading into plan-only loops.
"""

EXECUTION_COMMANDS = {
    "продолжай",
    "продолжить",
    "разрабатывай",
    "делай",
    "внедряй",
}

ALLOWED_RESULTS = {
    "ACTION_RESULT",
    "CONFIRMED_BLOCKER",
}

PLAN_ONLY = "PLAN_ONLY"


def classify_response(response: str) -> str:
    text = response.strip().lower()
    if text.startswith("план:") or ("следующий шаг" in text and "сделаю" in text):
        return PLAN_ONLY
    if "blocker:" in text:
        return "CONFIRMED_BLOCKER"
    return "ACTION_RESULT"


def guard_command(command: str, response: str) -> str:
    if command.strip().lower() not in EXECUTION_COMMANDS:
        return "ALLOW"

    response_type = classify_response(response)
    if response_type == PLAN_ONLY:
        return "REJECT"

    if response_type in ALLOWED_RESULTS:
        return "ALLOW"

    return "REJECT"
