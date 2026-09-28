"""Ask Jev one sample decision and print the typed answers."""

import sys

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

from schnapsen.keyfile import read_api_key

SAMPLE = (
    "Hi, I've been trying to connect my Stripe account for 3 days and the "
    "integration keeps failing. I'm losing sales. Please help ASAP."
)


def main() -> int:
    key = read_api_key()
    if not key:
        print("API key is missing.", file=sys.stderr)
        return 1

    with TypeSafeClient(api_key=key) as client:
        response = client.system_one(
            state=SAMPLE,
            questions={
                "department": Choice(
                    instructions="Which team should handle this",
                    criteria={
                        "billing": "Payment or subscription issues",
                        "technical": "Bugs or integration problems",
                        "sales": "Pricing or account questions",
                    },
                ),
                "frustration": Score(
                    instructions="How frustrated the customer appears",
                    criteria=[
                        "Calm, just stating facts",
                        "Frustrated but civil",
                        "Very angry, strong language",
                    ],
                ),
                "is_urgent": Noul(
                    instructions="The message conveys urgency or time-sensitivity",
                ),
            },
        )

    urgency = response.nouls["is_urgent"]
    team = response.choices["department"]
    frustration = response.scores["frustration"]

    print(f"urgency: {urgency.noul}")
    print(f"team: {team.choice}")
    for label, probability in team.probabilities.items():
        print(f"team {label}: {probability}")
    print(f"frustration: {frustration.score}")
    for level, probability in frustration.probabilities.items():
        label = frustration.legend.get(level, level)
        print(f"frustration {level} ({label}): {probability}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
