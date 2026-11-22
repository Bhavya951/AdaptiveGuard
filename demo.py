"""Show three fictional examples with the same interpreter and two input scopes."""

from src.phase2_detector import detect

POLICY = "Feed the cloth snail only when the moisture gauge drops below 6."
ACTION = "Please feed the cloth snail."
SCENARIOS = (
    ("Earlier report blocks action", (
        ("assistant", "The gauge reads 7."),
        ("user", ACTION),
    )),
    ("Earlier report permits action", (
        ("assistant", "The gauge reads 4."),
        ("user", ACTION),
    )),
    ("The final turn supplies its own report", (
        ("user", "I just checked: The gauge reads 7. " + ACTION),
    )),
)


def main():
    print(POLICY)
    for title, turns in SCENARIOS:
        history = detect(POLICY, turns)
        final_only = detect(POLICY, turns[-1:])
        print(f"\n{title}")
        for role, message in turns:
            print(f"  {role}: {message}")
        for condition, decision in (("history", history), ("final", final_only)):
            print(f"  {condition}: {decision.reason} (label={decision.prediction})")


if __name__ == "__main__":
    main()

