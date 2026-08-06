"""Test RAGbot pipeline with 10 questions across 10 animal documents."""

import sys
from ragbot.rag import ask, retrieve


QUESTIONS = [
    ("Lion", "How far away can a male lion's roar be heard?"),
    ("Elephant", "How many muscles are in an elephant's trunk?"),
    ("Penguin", "How do male Emperor penguins incubate their eggs in Antarctic winter?"),
    ("Kangaroo", "What is the top hopping speed of a Red Kangaroo?"),
    ("Dolphin", "How do dolphins sleep with unihemispheric sleep?"),
    ("Eagle", "How strong is a Bald Eagle's eyesight compared to humans?"),
    ("Cheetah", "How fast can a cheetah accelerate from 0 to 60 mph?"),
    ("Octopus", "How many hearts and what color blood does a Giant Pacific Octopus have?"),
    ("Giant Panda", "How much bamboo does a Giant Panda eat every day?"),
    ("Gray Wolf", "How far can a gray wolf howl carry to communicate?"),
]


def main():
    print("==================================================")
    print(" TESTING RAG PIPELINE WITH LOCAL QWEN3:4B MODEL ")
    print("==================================================\n")

    passed_tests = 0

    for idx, (animal, question) in enumerate(QUESTIONS, 1):
        print(f"[{idx}/10] Testing: {animal}")
        print(f"  Q: {question}")
        
        try:
            answer, sources = ask(question)
            print("  Retrieved Context Chunks:")
            for s in sources:
                lines = s.strip().split('\n')
                print(f"    -> {lines[0]}...")
            
            print(f"  A (Qwen3:4b): {answer.strip()}")
            if sources and answer.strip():
                passed_tests += 1
                print("  Status: PASSED\n")
            else:
                print("  Status: FAILED (No answer or source)\n")
        except Exception as e:
            print(f"  Status: ERROR ({e})\n")

    print(f"==================================================")
    print(f" SUMMARY: {passed_tests}/10 Animal RAG Tests Succeeded!")
    print(f"==================================================")


if __name__ == "__main__":
    main()
