# AI Test Gate

A small command-line tool that takes a Python file, uses an LLM to **automatically
write unit tests** for it, **runs those tests with coverage**, and then stops at a
**human approval gate** before the code is "accepted".

It is a proof-of-concept for a university project about the risks of *vibe coding*
(trusting AI-generated code without checking it). The whole point of the tool is
**verification with a human in the loop**: the AI suggests, the tests check, and a
person makes the final call.

---

## What it does, step by step

1. Reads the Python file you point it at.
2. Sends the code to an LLM and asks for a complete `pytest` test file.
3. Strips any Markdown fences from the reply and saves it to `generated_tests/`.
4. Runs the tests with `pytest --cov` to measure how much of the file is covered.
5. Prints a report: coverage %, how many tests passed/failed, and the names of any failures.
6. Recommends **APPROVE** or **REJECT** (REJECT if any test fails or coverage < 70%).
7. **Asks a human** `Approve this code for commit? [y/n]` and records the real decision.
8. Logs a one-line summary of the run to `results/run_log.txt`.

---

## Setup

### 1. Install the dependencies
```bash
pip install -r requirements.txt
```

### 2. Set the three environment variables
The tool never hardcodes secrets — it reads them from the environment.

| Variable        | What it is                          | Example |
| --------------- | ----------------------------------- | ------- |
| `LLM_API_KEY`   | Your secret API key                 | `sk-...` |
| `LLM_BASE_URL`  | API endpoint (blank = OpenAI default) | `https://api.groq.com/openai/v1` |
| `LLM_MODEL`     | Which model to use                  | `gpt-4o-mini` or `llama-3.3-70b-versatile` |

Example (Groq):
```bash
export LLM_API_KEY="your-key-here"
export LLM_BASE_URL="https://api.groq.com/openai/v1"
export LLM_MODEL="llama-3.3-70b-versatile"
```
See `.env.example` for a template.

---

## How to run it

**Clean code (should PASS → recommend APPROVE):**
```bash
python run_gate.py --target sample_code/calculator.py
```

**Buggy code (should produce a FAILING test → recommend REJECT):**
```bash
python run_gate.py --target sample_code/calculator_buggy.py
```

When prompted, type `y` or `n` to make the human decision. Each run is appended to
`results/run_log.txt`.

---

## What each file does

- **`run_gate.py`** — the entry point; it runs the whole flow (read → generate → run → report → human gate → log).
- **`src/llm_client.py`** — a tiny wrapper that sends one prompt to the LLM and returns the reply.
- **`src/test_generator.py`** — builds the prompt, asks for tests, removes Markdown fences, and saves the test file.
- **`src/runner.py`** — runs `pytest --cov` in a subprocess and parses the pass/fail counts and coverage %.
- **`sample_code/calculator.py`** — small correct functions (`add`, `divide`, `is_prime`, `factorial`) used for the clean demo.
- **`sample_code/calculator_buggy.py`** — the same functions but with one deliberate bug in `is_prime`, used for the REJECT demo.

`generated_tests/` and `results/` are created automatically the first time you run the tool.

---

## Notes
- Tests are generated at a low temperature (0.2) so they are fairly repeatable, but
  because an LLM writes them, the exact tests and coverage % can vary slightly run to run.
