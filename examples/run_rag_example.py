"""Example script for running the RAG pipeline from the command line."""

import contextlib
import io

from ragbot.rag import ask


def main() -> None:
    question = "What is capital of France?"
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        answer, _ = ask(question)

    print(answer)


if __name__ == "__main__":
    main()
