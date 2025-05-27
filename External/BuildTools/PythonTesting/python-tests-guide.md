---
description: Python testing guide
globs: '**/Tests/**/*.py,**/Tests/**/PLAN.md'
alwaysApply: false
---
# Python Testing Guide

1. **Kick off with a “Test Plan” doc**

   * Before typing a single pytest file, sketch a 1-2-page plan in `PLAN.md`:

     * List the key behaviours or user-visible outcomes your package must deliver.
     * For each behaviour, jot down the major scenarios (happy paths, edge cases, failure modes).
     * Prioritise scenarios by impact/likelihood.

   * If you need clarification from the User on the intent of the code under test, STOP and ask the User for feedback.
   * DO NOT GUESS the behaviours. Ensure you check the code's docstrings via `./stubs.sh` so you can correctly infer the intended behaviours. If in doubt, or if the documentation is ambiguous or missing, STOP and ask the User for clarification.
   * Avoid consulting the source code when writing tests - prefer instead to consult the stubs via `./stubs.sh`

2. **Adopt a Given-When-Then mindset**

   * For each scenario in your plan, write a one-sentence “Given… When… Then…” description.
   * Keep these descriptions in the plan doc as the source-of-truth for what each test does.

3. **Structure tests for clarity, not cleverness**

   * **One behaviour per test**: each test function asserts exactly one aspect of the behaviour.
   * **Explicit setup**: favor inline fixtures or small helper functions with descriptive names (“create_user_with_quota”) over faceless factories.
   * **No hidden logic**: avoid loops or conditionals in tests—if you find yourself writing a loop, consider splitting into multiple clearly-named tests.

4. **Use pytest idiomatically—but sparingly**

   * Rely on plain `assert` statements; avoid over-engineering with parametrisation unless you genuinely reduce duplication of **identical** scenarios.
   * Use pytest fixtures for heavyweight setup/teardown (`tmp_path`, DB connections, external services), but keep them narrow in scope.

5. **Name tests for human readers**

   * Test file names: `test_<feature>_<behaviour>.py` (e.g. `test_cart_addition.py`).
   * Test function names: `test_<action>_when_<condition>_then_<expected>()` (e.g. `test_add_item_when_out_of_stock_then_raise`).

6. **Keep tests self-documenting**

   * Favor literal values in assertions (“`assert cart.total == 29.99`”) rather than computed constants.
   * If you need a comment, question whether the test is doing too much: maybe split it.

7. **Iterate with the plan document**

   * After writing a batch of tests, update the plan: mark scenarios “✅ done,” “🔲 in progress,” or “⚠️ needs discussion.”
   * Before adding new features or fixing bugs, revisit the plan to ensure tests cover both existing and new behaviours.

8. **Run tests frequently and integrate CI**

   * Execute `pytest` in the terminal on every code change.

9. **Review tests like production code**

   * In code reviews, ask “Is this test easy to read in isolation? Does its name and body convey exactly one behaviour?”
   * Refactor only when it makes the test clearer—never just to shave lines.

10. **Maintain simplicity over “best practices”**

   * Prioritise **readability** over DRY refactoring and abstractions.
   * Prioritise **clarity** and **simplicity** over code length. Take the time and space you need.

11. **Static typing failures are test failures**

   * If a static typing test is not present for the package (`test_typing.py`), create it based on `./template_test_typing.py` (relative to this document).
   * The linter is **pylance**, and `test_typing.py` uses **pyright**.
   * You may explicitly ignore linter errors by appending `# type: ignore` to lines where non-strict typing is intended.

12. **Repo structure**

   * Packages under test should be directories under `Source` or `Source/Packages`.
   * Tests should be under `Tests`. A multi-package repo may have subdirectories for each package.
   * Test plans should be named `PLAN.md` and should be in the same directory as its associated `test_*.py` files.

13. **Inspect code via `stubs.sh`**

   * Your terminal has access to the script `./stubs.sh` (relative to this document). Run it using `./stubs.sh package_name`. This will give you the public members of the package, along with their type signatures and docstrings.

14. **Use your code interpreter**

   * You have access to a Python interpreter that you can use to interact directly with the source code. You may use this to help debug issues.
