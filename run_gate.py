"""AI TEST GATE -- entry point.

Takes a Python file, asks an LLM to write pytest tests for it, runs those tests
with coverage, prints a report, and then STOPS at a human approval gate before
the code is "accepted". This human-in-the-loop step is the whole point of the
prototype: it verifies AI-generated code instead of trusting it blindly.

Run it like:
    python run_gate.py --target sample_code/calculator.py
"""

import argparse
import os
from datetime import datetime

# Import our three small helper modules (the "src" folder).
from src.llm_client import ask_llm
from src.test_generator import generate_tests, save_tests
from src.runner import run_tests

DEFAULT_THRESHOLD = 70   # coverage % below which we recommend REJECT


def main():
    # --- 1. Read command-line arguments ---
    parser = argparse.ArgumentParser(description="AI test gate for a Python file.")
    parser.add_argument("--target", required=True, help="Path to the Python file to test.")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                        help="Minimum coverage %% to recommend approval (default 70).")
    args = parser.parse_args()

    target_path = args.target
    if not os.path.isfile(target_path):
        raise SystemExit("ERROR: target file not found: " + target_path)

    # Work out the module name (e.g. "calculator") and its folder (e.g. "sample_code").
    module_dir = os.path.dirname(target_path) or "."
    target_name = os.path.splitext(os.path.basename(target_path))[0]

    # --- 2. Read the source code of the target file ---
    with open(target_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # --- 3. Ask the LLM to generate tests, then clean the reply ---
    print("Generating tests with the LLM... (this calls your configured model)")
    test_code = generate_tests(source_code, target_name, ask_llm)

    # --- 4. Save the tests to generated_tests/test_<name>.py ---
    test_file = save_tests(test_code, target_name)
    print("Saved generated tests to: " + test_file)

    # --- 5. Run the tests with coverage ---
    print("Running pytest with coverage...\n")
    results, raw_output = run_tests(test_file, target_name, module_dir)

    # --- 6. Print a clear report ---
    print("=" * 50)
    print("TEST GATE REPORT for {}".format(target_path))
    print("=" * 50)
    print("Coverage : {}%".format(results["coverage"]))
    print("Results  : {} passed / {} failed".format(results["passed"], results["failed"]))
    if results["failing"]:
        print("Failing tests:")
        for name in results["failing"]:
            print("  - " + name)
    print("=" * 50)

    # --- 7. Decide a recommendation, then run the HUMAN APPROVAL GATE ---
    # Recommend REJECT if any test failed OR coverage is below the threshold.
    tests_failed = results["failed"] > 0
    low_coverage = results["coverage"] < args.threshold
    recommendation = "REJECT" if (tests_failed or low_coverage) else "APPROVE"

    if recommendation == "REJECT":
        print("\n[!] RECOMMENDATION: REJECT")
        if tests_failed:
            print("    Reason: at least one generated test failed.")
        if low_coverage:
            print("    Reason: coverage {}% is below the {}% threshold."
                  .format(results["coverage"], args.threshold))
    else:
        print("\n[OK] RECOMMENDATION: APPROVE -- all tests passed and coverage is sufficient.")

    # This prompt is mandatory: a human makes the real decision.
    answer = input("\nApprove this code for commit? [y/n]: ").strip().lower()
    human_decision = "APPROVED" if answer == "y" else "REJECTED"
    print("Human decision recorded: " + human_decision)

    # --- 8. Log a summary line to results/run_log.txt ---
    log_run(target_path, results, recommendation, human_decision)
    print("Logged this run to results/run_log.txt")


def log_run(target_path, results, recommendation, human_decision):
    """Append one human-readable summary line for this run to results/run_log.txt."""
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = ("{ts} | target={target} | coverage={cov}% | "
            "passed={p} failed={f} | recommendation={rec} | human={hd}\n").format(
        ts=timestamp, target=target_path, cov=results["coverage"],
        p=results["passed"], f=results["failed"],
        rec=recommendation, hd=human_decision,
    )
    with open(os.path.join("results", "run_log.txt"), "a", encoding="utf-8") as f:
        f.write(line)


# Standard Python idiom: only run main() when this file is executed directly.
if __name__ == "__main__":
    main()
