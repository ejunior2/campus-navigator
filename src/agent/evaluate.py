import time

from src.agent.agent import ask_agent

CASES = [
    ("Qual zona tem o pior sinal?", ["Biblioteca", "35"]),
    ("Qual zona tem o melhor sinal?", ["Patio", "47"]),
    ("Como está o sinal às 10h?", ["30.9", "30,9", "31"]),
    ("Como está o sinal às 3h da manhã?", ["44"]),
    ("Qual zona fica mais tempo com sinal fraco?", ["Biblioteca", "61"]),
    ("Qual o percentual de sinal fraco no Patio?", ["36"]),
    ("Em qual horário o sinal costuma cair?", ["10", "19"]),
    ("Qual a média de sinal às 19h?", ["30.9", "30,9", "31"]),
    ("Qual a cor do céu?", ["ferramenta", "wi-fi", "não", "desculpe"]),
    ("Qual o sinal na hora 25?", ["0 e 23", "0 a 23", "inválid", "não existe", "entre 0"]),
]


def is_correct(answer: str, expected: list[str]) -> bool:
    text = answer.lower()
    return any(item.lower() in text for item in expected)


def main():
    passed = 0
    for question, expected in CASES:
        answer = ask_agent(question)
        ok = is_correct(answer, expected)
        passed += ok
        print(f"[{'OK' if ok else 'FAIL'}] {question}")
        if not ok:
            print(f"   answer: {answer}")
        time.sleep(10)
    print(f"\nScore: {passed}/{len(CASES)}")


if __name__ == "__main__":
    main()