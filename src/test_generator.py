"""Build the prompt, ask the LLM for tests, clean the reply, and save it.

This file turns a chunk of source code into a saved pytest test file.
"""

import os

# The exact instructions we send to the LLM. {module_name} and {source_code}
# get filled in before sending. We ask for ONLY code so the reply is easy to save.
PROMPT_TEMPLATE = """You are a senior Python engineer writing unit tests.
Write a COMPLETE pytest test file for the code below.
Cover: normal cases, edge cases, and cases that should raise errors.
Import the functions from the module named `{module_name}`.
Return ONLY Python code. No explanation, no Markdown fences.

CODE TO TEST:
{source_code}
"""


def build_prompt(source_code, module_name):
    """Fill the template with the real module name and source code."""
    return PROMPT_TEMPLATE.format(module_name=module_name, source_code=source_code)


def strip_fences(text):
    """Remove Markdown code fences (```python ... ```) if the LLM added them.

    LLMs often wrap code in fences even when told not to. We strip them so the
    saved file is valid Python.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]                       # drop the opening ``` (or ```python) line
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]                  # drop the closing ``` line
        text = "\n".join(lines)
    return text.strip() + "\n"


def generate_tests(source_code, module_name, ask_fn):
    """Ask the LLM for tests and return cleaned Python code.

    ask_fn is the function that talks to the LLM (passed in so this stays easy
    to read and test).
    """
    prompt = build_prompt(source_code, module_name)
    raw_reply = ask_fn(prompt)
    return strip_fences(raw_reply)


def save_tests(test_code, target_name, out_dir="generated_tests"):
    """Write the test code to generated_tests/test_<targetname>.py and return its path."""
    os.makedirs(out_dir, exist_ok=True)         # create the folder if it does not exist
    path = os.path.join(out_dir, "test_{}.py".format(target_name))
    with open(path, "w", encoding="utf-8") as f:
        f.write(test_code)
    return path
