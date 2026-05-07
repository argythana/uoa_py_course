# Tokens, Token Usage and Selecting the Right AI Model

**Prerequisites:** You have read `read_agents_intro.md` from Lecture 1 and have GitHub Copilot working in VS Code.

---

## What is a Token?

When you type a prompt or paste code into an AI assistant, it does not read characters or words the way humans do.
It breaks your input into **tokens** — small chunks that the model processes internally.

**Rule of thumb for English text:**

- 1 token ≈ 4 characters ≈ ¾ of a word.
- 100 words ≈ 130–150 tokens.

**But code is different:**

- Variable names, operators, and punctuation each become separate tokens.
- Long variable names like `monthly_income_after_tax` may split into several tokens.
- Comments and docstrings also consume tokens.

### Why Does This Matter?

Every AI model has a **context window** — the maximum number of tokens it can handle (input + output combined).

| Concept | Meaning |
| --- | --- |
| **Input tokens** | Your prompt + any code/context the tool sends automatically |
| **Output tokens** | The AI's response |
| **Context window** | Maximum total tokens the model can process at once |

If your conversation exceeds the context window, older messages are silently dropped.
The AI "forgets" what you said earlier in a long chat.

**Practical consequence:** Keep your prompts focused.
Don't paste an entire project into chat when you only need help with one function.

---

## Tokens in Practice: Lecture 2 Examples

### Example 1 — Count Tokens Mentally

Consider this code from `lec_02a`:

```python
hour_wage = 20
daily_hours_work = 8
days_work = 20
daily_income = hour_wage * daily_hours_work
monthly_income = daily_income * days_work
```

This is roughly 5 lines, ~25 words, ≈ 40 tokens. A tiny fraction of any model's context window.

### Example 2 — Ask an AI to Estimate Tokens

**Prompt:**

```text
How many tokens does this Python code use approximately?

coffee_price = 2.50
coffee_qty = 2
coffee_total = coffee_price * coffee_qty
print("Coffee total:", coffee_total)
```

**What to check:** The AI should give a rough estimate. The exact count depends on the model's tokenizer.
You can verify with OpenAI's tokenizer tool: <https://platform.openai.com/tokenizer>

---

## Token Usage by Model

Different models use tokens differently:

| Factor | Effect |
| --- | --- |
| **Model size** | Larger models (GPT-4.1, Claude Opus) use the same tokens but produce more nuanced output |
| **Context window size** | Ranges from ~8K tokens (older models) to 200K+ (Claude, Gemini) |
| **Speed** | Smaller models respond faster; larger models think more carefully |
| **Cost** | More tokens processed = higher cost (relevant for API usage, not for Copilot subscription) |

**For this course:** You have Copilot via the student pack, so cost is not your concern.
But understanding tokens helps you write better prompts and understand why AI sometimes "forgets" things.

---

## Selecting the Right Model for the Task

GitHub Copilot lets you switch models. Here is a practical guide:

### When to Use a Smaller/Faster Model

- Quick syntax questions: "What does `//` do in Python?"
- Simple code generation: "Write a print statement that shows two variables separated by a comma."
- Autocomplete while typing (Copilot inline suggestions).
- Checking a type conversion: "Can I do `int('10.5')`?"

### When to Use a Larger/More Capable Model

- Explaining a concept in depth: "Explain the difference between parameters and arguments with examples."
- Debugging multi-line code with subtle errors.
- Refactoring or restructuring code.
- Generating longer, structured content (documentation, exercises).

### How to Choose

1. **Start with the default model.** It handles most beginner tasks well.
2. **Switch to a larger model** when the default gives shallow or incorrect answers.
3. **Compare answers.** Ask the same question to two models. Which one is clearer? More accurate?

**Try this now:**

Open Copilot Chat in VS Code and ask both a fast and a capable model:

```text
Explain the difference between int() and float() in Python.
Give me an example where converting between them changes the result.
```

Compare: Which answer is more helpful for a beginner?

---

## Examples of Tasks for Each Agent Mode

Building on what you learned in Lecture 1, here are Lecture 2-specific examples:

### Ask Mode — Learn Concepts

| Prompt | What You Learn |
| --- | --- |
| "What are Python's built-in numeric types?" | `int`, `float` (and `complex`) |
| "What is the difference between `/` and `//` in Python?" | Division vs floor division |
| "Why does `0.1 + 0.2` not equal `0.3` in Python?" | Floating-point precision |
| "What does `type()` return?" | The type/class of an object |

### Ask Mode — Understand Functions

| Prompt | What You Learn |
| --- | --- |
| "Explain the parameters of `print()` — what are `sep`, `end`, `file`, `flush`?" | Function parameters |
| "In `pow(2, 5)`, which argument is positional and which is keyword?" | Positional vs keyword arguments |
| "What happens if I call `divmod(10)`? Why does it fail?" | Required arguments |
| "What is the difference between a parameter and an argument?" | Core terminology (see `read_py_function_parameters_arguments.md`) |

### Edit Mode — Improve Code

1. Open `lec_02a_types_assignments_numeric_operations.py`.
2. Select the wage calculation section (lines ~130–150).
3. Ask: "Add f-string print statements that show each variable with a label."
4. Review: Does the AI use f-strings correctly? Compare with `lec_02d`.

### Edit Mode — Fix Broken Code

The intentionally broken code at the bottom of `lec_02a` is a good test:

1. Select the commented-out broken wage code.
2. Ask: "Uncomment this code and fix the errors."
3. Check: Did the AI fix the order-of-assignment bug? Did it improve the variable names?

### Agent Mode — Still Not Yet

Agent mode is powerful but requires understanding of files, paths, and modules (Lecture 3).
For now, focus on Ask and Edit. You will unlock Agent mode progressively.

---

## Common Pitfalls When Using AI for Lecture 2 Topics

### 1. Type Confusion

AI might generate code that mixes types without explicit conversion:

```python
age = input("Your age: ")       # Returns a string!
next_year = age + 1              # TypeError — AI may forget input() returns str
```

Always check: does the AI remember that `input()` returns a string?

### 2. Outdated Syntax

AI models trained on older data may suggest:

```python
print "Hello"     # Python 2 syntax — does NOT work in Python 3
```

If you see `print` without parentheses, the AI is hallucinating Python 2 code.

### 3. Overly Complex Answers

You ask: "How do I convert a string to an integer?"
AI answers with `try/except` error handling, `isinstance()` checks, and type hints.

Correct answer for Lecture 2 level: `int("42")`. That's it. If the AI over-engineers, ask it to simplify.

**Prompt template for simplification:**

```text
Simplify this for an absolute beginner who only knows print(), type(), int(), float(), str().
```

---

## Quick Checklist (Lecture 2 — Agents)

- [ ] Ask an AI to explain the difference between `int` and `float`.
- [ ] Ask an AI how many tokens a piece of code uses (estimate vs exact).
- [ ] Try switching models in Copilot Chat and compare an answer.
- [ ] Use Edit mode on the wage calculation code from `lec_02a`.
- [ ] Ask an AI what happens when you run `int("10.5")` — then verify it yourself.

---

**Previous:** `read_agents_intro.md` in Lecture 1 — Copilot modes, hallucinations, ground rules.
**Next:** Lecture 3 will introduce paths, modules, and virtual environments — and we will start using Agent mode.
