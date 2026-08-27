

# Welcome to the *"Python for Data Science, Machine Learning and Artificial Intelligence"* Course  

This repo contains the lectures' material for the [Business Information Systems](https://bis-analytics.econ.uoa.gr/) Postgraduate Program.  

Administrative, ephemeral issues (schedule, grades, questions, announcements) and any internal communication will be done via e-class.

The course has been created, is being maintained, and taught by [Thanasis Argyriou, @linkedin](https://www.linkedin.com/in/thanasis-argyriou-06155a94/).  
[Teacher's CV, Upd: Nov. 2023](https://bis-analytics.econ.uoa.gr/fileadmin/depts/econ.uoa.gr/bis-analytics/uploads/argyriou_cv_nov_23_gr.pdf).  
Since 2026, the material is been updated with assistance from AI Agents such as Claude Code, AdaL, codex, and has been inspired by the [Anthropic Course AI Fluency for Educators](https://anthropic.skilljar.com/ai-fluency-for-educators). For more info see the docs section.

## Lectures Outline

Please visit the [docs section](https://github.com/argythana/uoa_py_course/tree/main/docs) of the repository. The content gets updated frequently and is refactored every year. The material is organized in three parts:

- Fundamentals for Data Science
- Data Science and Machine Learning
- Deep Learning

### Repository Structure

Each lecture lives in its own folder under one of three parent directories:

| Parent Directory | Lectures | Focus |
| --- | --- | --- |
| `lectures_01_06_fundamentals_for_data_science/` | 01–06 | Python fundamentals |
| `lectures_07_13_pandas_plots_scikit/` | 07–13 | Data science with pandas, plots, scikit-learn |
| `lectures_14_16_nns_pytorch/` | 14–16 | Neural networks with PyTorch |

### Naming Conventions

| File type | Pattern | Example |
| --- | --- | --- |
| Teaching scripts/notebooks | `lec_NNx_description.py/.ipynb` | `lec_02a_types_assignments_operations.py` |
| Instruction/guide docs | `instruct_NNx_description.md/.txt/.ipynb` | `instruct_03a_cli_basic_commands.txt` |
| Learning goals | `goals_NN.md` | `goals_02.md` |
| Exercises | `lec_NN_exercises.md` + `lec_NN_exercises_solutions.py` | `lec_01_exercises.md` |

Every lecture folder contains a `goals_NN.md` file with:

- Learning goals for the lecture.
- A brief description of each file in the folder.
- Complementary files with basic concepts on AI Fluency.

## Course Outline

### A lot of good news! You will learn a beautiful new language

- Designed for absolute beginners, no previous coding experience required. Starts from zero, goes beyond the basics in several advanced topics.
- It is like learning a new language. You will be able to read, write, and speak `Python`.  You can't learn a foreign language (or coding) in five months, but you can learn enough to advance on your own.
- You will be surprised by how much you can learn in a short period.
- You need to learn, more or less, 30 new concepts in each lecture and a little syntax, notation and grammar rules. Also, some idioms, some slang, and some culture and mindset, some memes and some, not funny at all, coding jokes.
- Plus a few super helpful and cool tools (coding assistants, editors, notebooks) and you are ready to go.

### More good news! You don't have to worry about grades

- Mid-course assignments and practice exercises are optional and are graded only positively (extra points if you submit).
- Grades are secondary. Don't worry about it. I mean it. The goal is to learn and enjoy it.
- No exams, a [final assignment](https://github.com/argythana/uoa_py_course/tree/main/final_assignment), on a different domain for each student.
- The final assignment topic is generic, the dataset and the domain to work on is chosen by you.

### You need to use agents. Be careful: they compete with your future brain function

- Use of AI assistants and GitHub co-pilot is "mandatory". Learn to use them effectively and avoid common pitfalls. AI Fluency material is provided as a part of all the lectures on Python fundamentals. **Worth a read:** [this study](https://ai-project-website.github.io/AI-assistance-reduces-persistence/) reports that always-on AI assistance can reduce student persistence on hard problems. The 4Ds framework (Delegate, Describe, Discern, Diligence) in the AI Fluency readings is the course's response — assistants as a *learning amplifier*, not as a way to outsource thinking.
- [Must see](https://www.youtube.com/watch?v=n97BCfyFIvw) twice. Once before the first lecture, and once before writing the final assignment.
- In short: even if an agent types most of the code, you own the result.

### Even more good news! I'm here to help, not to judge you

- My lectures are so effective that you don't have to study afterwards. No, just kidding. You need to study and practice **only** at least three hours after each lecture.
- All material is available online, and all the lectures are "live". The tutor's attendance is mandatory, students' attendance too. This allows you to ask questions, get immediate feedback and learn as part of a team.
- Each topic, if necessary, is explained three times. If you don't get it, it means I did not explain it well enough, and I am also accountable for it. Don't Repeat Yourself (DRY) is a good programming principle, but not a good teaching tenet. I can't think of a good example about it yet, just an [anecdotal Sun Tzu story](https://titusng.com/2013/03/04/the-test-of-sun-tzus-art-of-war-on-concubines/). The moral of the story above does not apply in education, so I would kindly ask you to ask questions.
- The course is designed to be fun and engaging. If you are not having fun, please let me know. I will try to make it better. Nope, just kidding again.

### It gets even better! You get bonus points for

- Asking questions during or after class. My default and honest helpful reply is "ask an AI" and DYOR.
- Pointin out taipos, misstakes, andd ani kaind of improuvements inn the materyal.
- Negative feedback on the course material and the lectures delivery.
- Good programming memes.

### One more bit of good news: you'll learn some MLOps, not just ML

Most introductory courses stop once a model is trained. This one goes further — [Lecture 13](https://github.com/argythana/uoa_py_course/tree/main/lectures_07_13_pandas_plots_scikit/lecture_13_pipelines_gridsearch_mlflow) brings in **MLflow**, the industry-standard tool for experiment tracking, model management, and reproducible pipelines that sits at the heart of modern **MLOps**. Learning it here is a real, marketable advantage: you leave the course knowing not just how to build a model, but how to track, compare, and ship it like a professional.

### Course structure and pace

- The course starts slowly and accelerates. Each lecture covers a bit more material than the previous one.
- If you skip a lecture, you miss important insights, and you should definitely catch up before the next one. Good understanding of each lecture is a necessary prerequisite for the next one.
- We cover the basics in each topic during class and there is some necessary reading before the next lecture. Reading the material before the next lecture is absolutely necessary.
- Besides the mandatory reading material, there is some extra "optional, advanced" material for those who want to read more on a topic, and for those that want to pursue a career in Data Science and AI.
- Hands-on learning: Learn by coding a lot, in class and at home.
- The course focuses on applied Data Science and Machine Learning with Python. Theoretical background is provided, but the focus is on implementation.

### Course add-ons

- Integrated development environment: Interactive Python Notebooks are great, but we need a modern editor too.
- Working with Python requires working knowledge of the Command Line. We use it extensively.
- Using Git and GitHub is recommended, and all material is uploaded on e-class too.
- **Python 3.12+** is required to run the course material and notebooks.

### Course Philosophy: Continuous Learning

- Learning Python means learning new things all the time.
- Updates: Python is a fast-evolving language. First you need to learn version control and how to keep up with updates.
- Refactoring: The "*if it ain't broke don't fix it*" mentality is true in very limited cases. We would still live in caves if we followed this mantra.
- As a matter of fact, my "job" is to teach you how be able to continue learning and advancing on your own.
- The "teach a man to fish" philosophy is so outdated. You need to learn how to build a fishing boat. Kidding. **You need to learn how to learn.**

### Course evaluation. Good news! It's also about me, not just about you

- There is a Greek saying: "Με όποιο δάσκαλο καθίσεις, τέτοια γράμματα θα μάθεις". A translation would be:
"You will learn as much as the teacher you sit with" or literally:  
"with whomever teacher you sit, such teachings you are going to learn".  
- I would be happy to get a good grade. That can be achieved if you submit excellent final assignments.
- I appreciate your help to make the course and each lecture better after each iteration.
- You are kindly asked to provide feedback on the lectures, the notes, and the teacher all the time.

### How to ask questions between lectures

- Each student is allocated at least 20 minutes per week for questions or personal assistance.
- Please use all this time and more. This is highly recommended.
- Read this Guide from Stackoverflow [How to ask questions](https://stackoverflow.com/help/how-to-ask). What to do before asking:  
  1. Ask an AI assistant and always verify the reply.  
  2. Google it, search for similar questions on Stackoverflow.  
  3. Try various solutions, document your results.
  4. Formulate the question in a clear, concise way, including all the steps you have taken.

### What next

Please visit:
a) A dedicated [teaching repo on MLflow, from beginner to advanced.](https://github.com/argythana/teach-mlflow)  
b) A mini [crash-course on development tools.](https://github.com/argythana/dev_boilerplate_course)  
c) A demo repo to go to [intermediate and then to advanced material](https://github.com/argythana/r4m_public_demo)  
d) A section with "real work" examples, Python in the workplace by UoA - BIS graduates. (Soon).
