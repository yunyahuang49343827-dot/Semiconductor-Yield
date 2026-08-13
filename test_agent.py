from agent import ask_factory_agent


questions = [
    "What is the current overall yield?",
    "Which three lots have the lowest yield?",
    "Show me the manufacturing record for LOT_0024 wafer W001."
]


for question in questions:

    print("\n==============================")
    print("Question:")
    print(question)

    answer = ask_factory_agent(question)

    print("\nAnswer:")
    print(answer)