# Lecture 08: EDA & Plots

## Refactoring Status (2025–2026)

Completed refactoring:

- [x] Fixed internal lecture numbering (was "07", now "08") in all notebook titles.
- [x] Added beginner-friendly comments to all existing notebooks (08a–08d).
- [x] Created comprehensive EDA notebook on the heart disease dataset (08e).
- [x] Split old 08e draft into separate auto-EDA (08f) and web frameworks (08g) notebooks.
- [x] Auto-EDA notebook uses heart disease dataset with Sweetviz, PyGWalker, and Vizro.
- [x] Added Taipy to the web frameworks notebook alongside Streamlit, Dash, and Gradio.
- [x] Gradio local demo in lecture 08; Hugging Face deployment deferred to a later ML lecture.

Remaining / future ideas:

- [x] Old draft `lec_08e_auto_EDA_DRAFT_2025.ipynb` archived to `archive/` folder.
- [x] Added "choosing the right plot" decision flowchart to 08b.
- [ ] Gradio + Hugging Face deployment notebook in lecture 12 or 13 (with a trained classifier).

## Learning Goals

- Create interactive plots using Plotly Express (strip, scatter, bar, polar, parallel coordinates).
- Create static plots using seaborn and matplotlib; understand Anscombe's quartet limitations.
- Apply principles of informative visualization: data-ink ratio, proportional ink, aspect ratio, color choice.
- Perform Exploratory Data Analysis (EDA) on a dataset with descriptive statistics and plots.
- Perform comprehensive EDA on a real-world medical dataset (heart disease): data quality, distributions, correlations, outliers, advanced plots.
- Use auto-EDA tools (Sweetviz, PyGWalker, Vizro) to generate reports automatically.
- Awareness of web app frameworks (Streamlit, Gradio, Dash, Taipy) for sharing data science results.

## Files

- `lec_08a_interactive_plots.ipynb` — Plotly Express demo: strip, scatter, bar, histogram, box, sunburst, treemap, choropleth, animated plots.
- `lec_08b_static_plots.ipynb` — Static visualization: seaborn/matplotlib, Anscombe's quartet, data-ink ratio.
- `lec_08c_more_interactive_plots.ipynb` — Advanced Plotly: polar plots, parallel coordinates, treemaps, sunbursts.
- `lec_08d_EDA_iris.ipynb` — EDA walkthrough on the iris dataset (seaborn/matplotlib).
- `lec_08e_EDA_heart_disease.ipynb` — Comprehensive EDA on the heart disease dataset (plotly + seaborn + matplotlib).
- `lec_08f_auto_EDA.ipynb` — Auto-EDA tools: Sweetviz, PyGWalker, Vizro.
- `lec_08g_web_app_frameworks.ipynb` — Web app frameworks: Streamlit, Gradio (local), Dash, Taipy.
- `archive/lec_08e_auto_EDA_DRAFT_2025.ipynb` — (Legacy draft, archived. Superseded by 08f + 08g.)
