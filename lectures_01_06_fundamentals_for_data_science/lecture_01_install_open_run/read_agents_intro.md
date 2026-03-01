# AI Assistants and Agents: A Practical Introduction

## What are AI coding assistants?

AI coding assistants are tools that understand natural language and code.
You describe what you want — in plain English or Greek — and they generate code, explain concepts, or find mistakes.

Think of them as a very knowledgeable, always available, but sometimes overconfident study partner.
They can help you learn faster, but they can also mislead you if you trust them blindly.

**Key point:** An AI assistant is a *tool*, not a teacher, not a replacement for understanding.

## AI Fluency

Anthropic offers free courses on responsible and effective AI use, built around the **4D AI Fluency Framework** (Delegation, Description, Discernment, Diligence). All courses are open-access under a Creative Commons license.

- [AI Fluency: Framework & Foundations](https://anthropic.skilljar.com/ai-fluency-framework-foundations) — Core course covering practical skills for effective, ethical AI interaction (~3–4 hours).
- [AI Fluency for Educators](https://anthropic.skilljar.com/ai-fluency-for-educators) — Applying the 4D framework to teaching practice and course design (~3 hours).
- [AI Fluency for Students](https://anthropic.skilljar.com/ai-fluency-for-students) — Developing AI skills for learning, career planning, and responsible collaboration (~3 hours).

Start with the **Framework & Foundations** course if you have time for only one. The **Students** course is the most directly relevant to this class.

See also: [AI Fluency: Key Terminology Cheat Sheet (PDF)](https://anthropic.skilljar.com/ai-fluency-for-educators/326779) - scroll to end of web page.

---

## GitHub Copilot in VS Code: Three Modes

After setting up GitHub Copilot (see `instruct_01d_IDEs_AI_copilot`), you have three main ways to interact with it.

### Ask Mode

Ask questions about Python, your code, or general programming concepts.

**Try these in Copilot Chat (Ask mode):**

```text
What does print() do in Python?
```

```text
What is the difference between interactive and script output in Python?
```

```text
Explain what sep and end do in print().
```

**What to look for:** Does the answer match what you learned in `lec_01a`? Can you verify it by running code?

### Edit Mode

Select code in your editor and ask Copilot to modify it.

**Try this:**

1. Open `lec_01a_operations_print_help.py`.
2. Select the receipt-printing lines at the bottom.
3. Ask Copilot: "Make these print statements more readable using sep and end parameters."
4. Compare the AI suggestion with the original. Which is clearer? Why?

### Agent Mode

Agent mode can plan multi-step tasks: create files, run commands, fix errors across your project.

**Important for Lecture 1:** You do not need agent mode yet.
Be aware it exists. We will use it progressively from lecture to lecture.
For now, **Ask** and **Edit** modes are your main tools.

---

## Selecting a Model

GitHub Copilot lets you choose which AI model powers it (e.g., GPT-4.1, Claude Sonnet 4, Gemini).

For now, all you need to know:

- **Different models, different strengths.** Some are better at explaining, others at generating code.
- **Start with the default.** The pre-selected model works well for beginners.
- **You can switch models** using the model selector in the Copilot Chat panel.
- **Experiment later.** Once you are comfortable, try asking the same question to different models and compare answers.

We will discuss tokens, model selection criteria, and cost in Lecture 2.

---

## Agent Versions vs Python Versions

You already learned in `instruct_01a` that Python version control matters.
AI models have a similar issue:

- Models are trained on data up to a certain date (their "knowledge cutoff").
- A model released in 2025 may not know about a Python feature or library update from late 2025.
- Just like you install Python 3.13 instead of 3.14 for stability, AI models also have "versions" that evolve.

**Practical consequence:** If an AI suggests code that uses a function you can't find in the docs,
it might be hallucinating or referencing a different version of a library. Always verify.

---

## Knowledge Cut-off Date

Every AI model is trained on data collected up to a specific point in time — its **knowledge cut-off date**.
After that date, the model has no awareness of new events, library releases, or language changes.

### What this means in practice

| Situation | Risk |
| --- | --- |
| A new Python version adds a feature after the cut-off | The AI doesn't know it exists |
| A library changes its API after the cut-off | The AI suggests the old, broken syntax |
| A security vulnerability is discovered after the cut-off | The AI may still recommend the unsafe pattern |
| You ask about a tool released after the cut-off | The AI may invent a plausible-sounding but wrong answer |

### How to find a model's cut-off date

Ask it directly:

```text
What is your knowledge cut-off date?
```

Then cross-check: if you are asking about something that changed recently,
verify with the official documentation, not just the AI's answer.

### Cut-off date vs release date

These are **not** the same:

- The **cut-off date** is when the training data ends.
- The **release date** is when the model became publicly available (always later).
- There is typically a gap of several months to over a year between the two.

**Example:** A model released in early 2026 may have a cut-off of mid-2025.
It will not know about Python or library updates from late 2025 onwards.

### Practical rule for this course

Before trusting AI code that uses a specific library function:

1. Check the library's official docs to confirm the function exists.
2. Check the library version you have installed (`pip show <library>`).
3. If in doubt, test it — run the code and read the error message.

---

## Non-Deterministic Output

Python is **deterministic**: given the same input, the same code always produces the same output.
AI models are not.

Ask the same question twice and you may get two different answers — different wording, different code,
sometimes different logic. This is by design, controlled by a parameter called **temperature**.

### What is Temperature?

- **Temperature = 0** — The model always picks the most likely next token. Output is nearly identical each time.
- **Temperature > 0** — The model introduces randomness. Output varies between runs.
- Most chat assistants run at a moderate temperature to feel natural and creative.

### Why Does This Matter for You?

| Situation | Consequence |
| --- | --- |
| You ask for code and get a working solution | Re-running the same prompt may give different code |
| You ask for an explanation and get a clear answer | The next answer may be less clear |
| You rely on AI output without testing | A previously correct answer may not reproduce |

### Demo: See it for Yourself

Ask Copilot the same question three times in a row (open a new chat each time):

```text
Write a Python one-liner that calculates the area of a circle with radius 5.
```

**What to observe:**

- Does it use `math.pi` or `3.14159` or `22/7`?
- Does it import `math` or not?
- Does it use a variable or inline the calculation?
- Is the result always numerically correct?

All versions may be valid Python — but they are not identical.
This means **you** must evaluate the output, not just accept the first answer.

### The Practical Rule

> Run it. Read it. Understand it. Then decide if it is good enough.

Copying AI output without understanding it is risky precisely because
the same prompt tomorrow may produce something different.

---

## Demo Examples: Using AI with Lecture 1 Content

### Example 1 — Ask for an explanation

**Prompt:**

```text
I'm a Python beginner. Explain what this code does, line by line:

coffee_price = 2.50
coffee_qty = 2
coffee_total = coffee_price * coffee_qty
print("Coffee total:", coffee_total)
```

**What to check:** Does the AI's explanation match your understanding from class?

### Example 2 — Ask for help with an error

**Prompt:**

```text
I wrote this Python code and got an error. What's wrong?

print(hello class)
```

**What to check:** Does the AI explain that strings need quotes? Does it mention `SyntaxError`?

### Example 3 — Ask the AI to generate code

**Prompt:**

```text
Write a Python script that calculates the total price of 3 coffees at 2.50 each,
2 sandwiches at 4.20 each, and applies a 15% discount. Print a readable receipt.
```

**What to do:**

1. Read the generated code carefully.
2. Do you understand every line?
3. Run it. Does it produce correct results?
4. Calculate the expected output by hand first, then compare.

### Example 4 — Ask for PEMDAS help

**Prompt:**

```text
What does 20 / 5 / 4 evaluate to in Python? Explain the order of operations.
```

**What to check:** The AI should mention left-to-right evaluation. Verify in the interpreter.

---

## Discussion Topics

### Hallucinations

AI models sometimes generate confident-sounding answers that are **wrong**.
This is called a "hallucination."

- An AI might invent a function that does not exist.
- It might give you code that looks correct but produces wrong results.
- It might quote documentation that was never written.

**Rule:** Never trust AI output without verifying it yourself.

### AI Slop

"AI slop" refers to low-quality, generic, filler content produced by AI.
It sounds correct and professional but adds no real value.

In coding:

- Overly verbose comments that say what the code already says.
- Generic variable names and boilerplate that obscure intent.
- Explanations that sound good but miss the actual question.

**Rule:** Quality over quantity. Brief, correct, and clear beats long and vague.

### Muscle and Brain Atrophy

If you let AI write all your code, you won't learn Python — you'll learn to prompt.
Prompting is a useful skill, but it is not programming.

- **Type the code yourself** in the first lectures. Muscle memory matters.
- **Solve exercises without AI first**, then check with AI.
- **Understand before you automate.** Use AI to learn, not to skip learning.

The course requires AI usage, but it also requires that *you* understand what the AI generates.

### Clear Communication

AI assistants respond better to clear, specific prompts.
This is exactly the same skill you need when:

- Asking a question in class.
- Writing code comments.
- Describing a bug to a colleague.
- Writing documentation.

**Vague prompt → vague answer.**
**Specific prompt → useful answer.**

Compare:

| Prompt | Quality |
| --- | --- |
| "Fix my code" | Vague — fix what? |
| "I get a NameError on line 5 when I run this script. I expected it to print 42." | Clear context, specific error, expected behavior |

---

## Human–AI Interaction: Ground Rules for This Course

1. **AI is mandatory** — Use Copilot (or another assistant) from day one.
2. **Understanding is mandatory** — If you can't explain what the code does, you haven't learned it.
3. **Verify everything** — Run the code, check the output, compare with your expectations.
4. **Start simple** — Use Ask mode for explanations, Edit mode for small improvements.
5. **Document your interaction** — If an AI helped you solve a problem, note what you asked and what you changed.
6. **Report interesting failures** — Found a hallucination? Share it in class for bonus points.

---

## Quick Checklist (Lecture 1 — Agents)

- [ ] Open Copilot Chat in VS Code and ask it to explain `print()`.
- [ ] Ask your AI assistant: "What is your knowledge cut-off date?"
- [ ] Ask the same question twice in separate chats. Note any differences in the answer.
- [ ] Try at least one prompt from the Demo Examples section above.
- [ ] Verify the AI's answer by running code in the interpreter.
- [ ] Identify at least one thing the AI got wrong or could explain better.

---

**Next:** In Lecture 2 we will discuss tokens, model selection, and how to choose the right AI tool for each task.
