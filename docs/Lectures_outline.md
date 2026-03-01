
# Course Material - Under extensive refactoring, given the feedback from last year's class and your feedback in each lecture

The following kind of material is provided:

1. Reading related to `Python` topics
2. Python files to practice
3. "Guides" and "instructions" to install, set up, and/or use various tools that are necessary. Some tools are about Python, some about using the PC efficiently.
4. Reading on AI assistants

All kinds of materials that are presented during the lectures should be studied

## AI Assistants and Agents: A Thread Running Through the Course

Starting from 2025–2026, each lecture includes a dedicated AI/agents component alongside the Python content.
Using an AI coding assistant (GitHub Copilot or equivalent) is **mandatory** from Lecture 1.

The goal is to learn to use AI tools effectively and critically — not as a shortcut, but as a learning amplifier.
Each lecture's `goals_NN.md` file lists the specific agent learning goals for that lecture.
Each lecture has a corresponding `read_agents_*.md` reading file.

| Lecture | AI / Agents Topic | File |
| --- | --- | --- |
| 01 | Copilot setup, Ask/Edit/Agent modes, hallucinations, human–AI interaction | `read_agents_intro.md` |
| 02 | Tokens, context windows, model selection, task examples per mode | `read_agents_tokens_model_selection.md` |
| 03 | Agent mode: paths, working directories, CLI tasks via agents | `read_agents_cli_paths.md` *(planned)* |
| 04 | Using AI to explore and understand data containers | `read_agents_containers.md` *(planned)* |
| 05 | Using AI to debug logic errors, loops, and conditions | `read_agents_debugging.md` *(planned)* |
| 06 | Using AI to design and refactor functions | `read_agents_functions.md` *(planned)* |
| 07–09 | Using AI for data exploration, plotting, clustering | *(planned)* |
| 10 | AI-assisted study of KNN and ML concepts | `lec_10b_study_knn_use_AI.ipynb` |
| 11–13 | Using AI for regression, classification, pipelines | *(planned)* |
| 14–16 | Using AI in neural network debugging and experimentation | *(planned)* |

## Section 1: Basic python for Data Science

See lectures 1 to 6.  
The goal of this section is to learn some of the very basics of python.
Focus on how the basic concepts are used in data science, machine learning, and AI.

## Section 2: Working with Data and Dataframes

See lecture 7.  
Add in lecture 7, feedback from students:  
Discuss more about "changes" in dataframes, drop columns, add columns, mutable, not mutable, best practices, etc.

Feedback from last year: Add extra lecture 7 here for data preprocessing (nan, encoding, scaling, convert incorrect types).
Until now, such topics are covered:
a) as complementary material, scattered and fragmented in small parts in each ML algo lecture.
b) after teaching the algos within the material about "pipelines" and "Grid search", parameter tuning.

**Reminder**: utilise the numpy 2.0 release changes to emphasize version control.

### Topic 3: EDA, Static and Interactive Visualisations

See lecture 7. Todo: Refactor to lecture 8.
Add network graphs plotting as part of lecture for plots.

### Topic 4: Machine Learning Algos

See lectures 8-12. To be refactored as 9 to 13.
9: Regession: Linear, Logistic
10: Clustering: K-means.
11: Classification: All Algos in one lecture (Logistic, Kmeans, Naive Bayes, SVM)
12 (Todo: add for 2025): Ensemble methods, Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost.

### Section 5: Deep Learning and AI (NNs, Computer Vision, LLMs)

Lectures 13-16. Requires a lot of refactoring and thought.
Suggestions from last year's class:
13: Neural Networks, Keras, TensorFlow, LSTMs
14: Computer Vision, OpenCV, Image Processing
15: Pytorch Locally
16: Pytorch on the cloud, Google Colab, Kaggle, etc.

### Extra: Python in the workplace by UoA - BIS graduates

Add this as a distinct section "next to the lectures" and also in the README.
"Experimental". Extra, optional presentations, started in 2024, not part of the repo.  
Example A: Data management and reporting worklow in a betting company.  (Pending)
Example B: Auditing Cybersecurity Documents with a fine-tuned LLM.  (DONE)
Example C: Administrative work tasks at a University. (Generate mass word documents, pdfs, and emails).  (DONE)
Example D: Automating excel files' data merge, reporting in a bank.
(DONE)
