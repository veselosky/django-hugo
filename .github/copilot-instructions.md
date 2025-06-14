Guidelines for Python code:

- Use Python 3.10+ syntax and features.
- Always use absolute imports.
- When using Pydantic, prefer Pydantic V2 features and syntax.
- Use type hints for function parameters and return types.
- Use `from __future__ import annotations` to enable postponed evaluation of type annotations.
- In Django code, ensure user-visible strings are marked for translation using `gettext` or `gettext_lazy`.
- In Django templates, ensure user-visible strings are marked for translation using the `translate` template tag.
- When generating tests, prefer the `unittest` framework from the standard library.
- When testing Django-specific code, use Django's `TestCase` class and related tools.
- Place new test files in the top-level `tests` directory, with a name beginning with "test_".
- Ensure each Python source file contains the copyright notice from `.vscode/AGPLNotice.code-snippets`.
