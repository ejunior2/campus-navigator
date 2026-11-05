import time

import httpx
from google.genai import errors, types

from src.agent import tools
from src.agent.llm import MODEL, get_client

SYSTEM_PROMPT = (
    "You are the Campus Navigator assistant. You answer questions about "
    "Wi-Fi quality on a simulated campus. Signal is a synthetic score from "
    "0 (no signal) to 100 (excellent); below 40 is considered weak. "
    "Always use the provided tools to get data; never invent numbers. "
    "If a question cannot be answered with the tools, say so. "
    "Answer in the same language as the user, briefly."
)

TOOLS = [
    tools.get_worst_zone,
    tools.get_best_zone,
    tools.get_weak_signal_pct,
    tools.get_signal_by_hour,
    tools.get_weakest_hours,
]


def ask_agent(question: str, retries: int = 4) -> str:
    client = get_client()
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
    )
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL, contents=question, config=config
            )
            return response.text or "(no answer: the model returned no text)"
        except (errors.ServerError, httpx.TransportError):
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt * 3)


if __name__ == "__main__":
    for q in [
        "Qual zona tem o pior sinal?",
        "Como está o sinal às 10h?",
        "Qual a cor do céu?",
    ]:
        print(f"> {q}")
        print(ask_agent(q))
        print()