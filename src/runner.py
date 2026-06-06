"""Run the generated tests with pytest + coverage, and parse the results.

We run pytest as a separate process and read its text output, then pull out the
numbers we care about: how many tests passed/failed, which ones failed, and the
coverage percentage.
"""

import os
import re
import subprocess


def run_tests(test_file, module_name, module_dir):
    """Run pytest on test_file, measuring coverage of the target module.

    module_name is the import name (e.g. "calculator").
    module_dir is the folder that module lives in (e.g. "sample_code"), which we
    add to PYTHONPATH so the generated test's `import calculator` works.
    Returns (results_dict, raw_output_text).
    """
    # Copy the current environment and prepend the module's folder to PYTHONPATH
    # so Python can find and import the module being tested.
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = module_dir + (os.pathsep + existing if existing else "")

    # Build the pytest command:
    #   --cov=<module>      measure coverage of just the target module
    #   --cov-report=term   print a coverage table we can parse
    #   -q                  quiet output
    #   -rf                 list the names of FAILED tests in the summary
    #   --tb=short          short tracebacks (keeps output readable)
    cmd = [
        "pytest", test_file,
        "--cov=" + module_name,
        "--cov-report=term",
        "-q", "-rf", "--tb=short",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    output = proc.stdout + proc.stderr
    return parse_results(output), output


def parse_results(output):
    """Read pytest's text output and return a dict of the key numbers.

    Keys: passed (int), failed (int), failing (list of test names), coverage (int %).
    """
    # --- passed / failed counts ---
    # pytest prints a summary like "1 failed, 5 passed in 0.10s". We search for
    # the "<n> passed" and "<n> failed" pieces; missing pieces mean zero.
    passed = _find_int(r"(\d+) passed", output) or 0
    failed = _find_int(r"(\d+) failed", output) or 0
    errors = _find_int(r"(\d+) error", output) or 0   # collection/import errors count as bad too
    failed += errors

    # --- names of failing tests ---
    # With -rf, failures appear as lines like "FAILED test_x.py::test_name - ...".
    failing = re.findall(r"FAILED\s+(\S+)", output)

    # --- coverage percentage ---
    # The coverage table ends with a TOTAL line like "TOTAL  10  2  80%".
    coverage = _find_int(r"TOTAL.*?(\d+)%", output)
    if coverage is None:
        # Fall back to the last percentage shown anywhere in the output.
        all_pcts = re.findall(r"(\d+)%", output)
        coverage = int(all_pcts[-1]) if all_pcts else 0

    return {
        "passed": passed,
        "failed": failed,
        "failing": failing,
        "coverage": coverage,
    }


def _find_int(pattern, text):
    """Return the first captured group of `pattern` in `text` as an int, or None."""
    match = re.search(pattern, text, re.DOTALL)
    return int(match.group(1)) if match else None
