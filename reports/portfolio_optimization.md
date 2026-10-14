# Portfolio & Resume Optimization Guide — TMDb Movie Analytics

**Target Roles:** Junior Data Analyst, Analytics Engineer, Business Intelligence Analyst  
**Technologies:** Python, Pandas, SQL (SQLite), Streamlit, Plotly, Pytest, SciPy  
**Repository:** [Netflix_EDA_PROJECT](https://github.com/Karunesh17/Netflix_EDA_PROJECT)  

---

## 1. Five ATS-Friendly Resume Bullets

### Option 1: Core Data Analyst (Recommended Overall)
> **Engineered a Python and Pandas EDA pipeline to analyze 9,827 movie titles and 25,793 normalized genre occurrences, uncovering a 28.2% catalog growth rate (2015–2019) and identifying portfolio concentration in Drama (38.1%) and Comedy (30.8%).**
* *Keywords:* Python, Pandas, EDA pipeline, normalized, catalog growth rate, portfolio concentration.

### Option 2: Analytics Engineer & Data Quality
> **Audited catalog data integrity across 9,827 titles using Python, resolving boundary flaws in quantile binning to prevent 100 unrated records from data loss and implementing 14 automated pytest assertions to guarantee zero regression.**
* *Keywords:* Data integrity, Python, quantile binning, automated assertions, pytest, regression testing.

### Option 3: SQL Analytics & Relational Modeling
> **Architected a normalized SQLite database modeling 9,827 films and 25,793 genre bridge records, writing 8 advanced SQL queries utilizing CTEs, window functions (LAG, DENSE_RANK), and self-joins to evaluate genre co-occurrence and YoY growth.**
* *Keywords:* SQLite, normalized schema, bridge records, SQL, CTEs, window functions, DENSE_RANK, self-joins.

### Option 4: Business Intelligence & Dashboard Development
> **Developed an interactive 5-tab Streamlit and Plotly intelligence dashboard with dynamic vote-count threshold filters, modeling release velocity across 12 decades and analyzing market share across 43 languages.**
* *Keywords:* Streamlit, Plotly, dashboard development, interactive filters, release velocity, market share.

### Option 5: Statistical Analysis & Behavioral Modeling
> **Evaluated commercial popularity versus audience ratings across 9,827 films using SciPy, demonstrating weak correlation (Spearman rho = 0.127) and applying Kruskal-Wallis tests (p < 0.001) to validate rating variance across major genres.**
* *Keywords:* Statistical analysis, SciPy, Spearman rank correlation, Kruskal-Wallis test, hypothesis testing.

---

## 2. Three-Line LinkedIn Project Summary

```
🎬 Engineered an end-to-end Movie Analytics Platform analyzing 9,827 films and 25,793 normalized genre tags using Python, SQLite, and Streamlit.
🔍 Identified critical data quality risks by resolving lower-bound binning errors to safeguard 100 unrated catalog assets, verified with 14 automated pytest checks.
📈 Built an interactive Plotly dashboard and modeled YoY production trends, uncovering a 28.2% pre-pandemic expansion and a 57.6% backlog surge in 2021.
```

---

## 3. Professional GitHub Project Description & Topics

**GitHub About Summary (Max 350 chars):**
> Production-grade Movie Analytics Platform analyzing 9,827 films across 12 decades. Features reproducible Python ETL, normalized SQLite relational modeling, 8 production SQL queries (CTEs, LAG, DENSE_RANK), interactive Streamlit dashboard, and automated pytest suite.

**GitHub Suggested Repository Topics / Tags:**
`data-analytics` `python` `sql` `sqlite` `pandas` `streamlit` `plotly` `pytest` `data-quality` `exploratory-data-analysis` `analytics-engineering` `business-intelligence`

---

## 4. Top Five Technical Interview Questions & Defensible Answers

### Q1: "How did you approach data cleaning and handling untidy data in this project?"
> **Answer:** *"The most critical challenge was multi-label genre tags stored as comma-separated strings. Instead of naively exploding the main DataFrame—which inflates row counts and distorts release year histograms—I designed a normalized relational model. I kept a cleaned `movies` table of 9,827 rows and created a separate `movie_genres` bridge table containing 25,793 rows. This allowed me to compute dual denominators: Drama makes up 14.5% of total genre tags, but penetrates 38.1% of all unique movie titles. I also added automated assertions in Python to confirm referential integrity between tables."*

### Q2: "What was the most significant data quality bug you discovered, and how did you resolve it?"
> **Answer:** *"In the original notebook, the analyst used `pd.cut()` to bin audience ratings into quantiles, starting at the minimum score of 0.0. Because `include_lowest` defaults to `False`, the 100 movies with `Vote_Average == 0.0` became `NaN` and were subsequently deleted by `df.dropna()`. Upon inspecting the raw data, I discovered that 100% of these 100 records had `Vote_Count == 0`—they were unrated/upcoming films, not films that received scores of zero. I resolved this by segregating them into a dedicated `Rating_Status = 'Unrated'` tier, preserving the full 9,827 catalog volume while preventing zero-score distortion in clean rating averages."*

### Q3: "Why did you use SQLite instead of keeping everything in Pandas, and what advanced SQL did you write?"
> **Answer:** *"While Pandas is effective for in-memory exploration, demonstrating relational data modeling and SQL fluency is critical for Analytics Engineering roles. I loaded the cleaned data into SQLite with primary keys, foreign keys, and indexes. I wrote 8 analytical queries featuring Common Table Expressions, `CASE WHEN` conditional groupings, window functions like `LAG()` for Year-over-Year release growth, `DENSE_RANK()` for finding top films per genre, and a relational self-join to compute a genre co-occurrence matrix (finding that Action + Thriller is the most common pairing with 944 films)."*

### Q4: "How did you address sample size bias in audience ratings?"
> **Answer:** *"Titles with only 1 to 5 user votes often have extreme scores (like 10.0 or 1.0) due to low sample variance. In both my SQL queries and Streamlit dashboard, I implemented configurable vote-count threshold filters ($N \ge 50$, $N \ge 100$, $N \ge 500$). For example, when applying an $N \ge 100$ filter, the average rating for Drama stabilizes from 6.71 to 6.86, and ranking queries surface genuine audience consensus rather than obscure single-vote titles."*

### Q5: "What did your statistical analysis uncover regarding popularity versus ratings?"
> **Answer:** *"Because Popularity and Vote Count exhibit severe positive skew with long right tails (over 1,000 titles exceeded the $1.5 \times IQR$ upper bound), I used non-parametric tests. I calculated Spearman's rank correlation and discovered that Popularity and Vote Average have a very weak correlation ($\rho = 0.127$, $p < 10^{-35}$). This proves that commercial marketing buzz does not correlate with audience acclaim. I also ran a Kruskal-Wallis H-test ($H = 636.96, p < 10^{-100}$) showing statistically significant differences in rating distributions across major genres."*

---

## 5. Concise Business Value Statement
> *"This project demonstrates how rigorous data quality engineering and multi-dimensional analytics can turn raw entertainment metadata into actionable content acquisition intelligence. By establishing automated pipeline assertions, modeling genre co-occurrence synergies, and quantifying production volatility across economic cycles, the project provides content strategy teams with mathematically verified benchmarks to optimize catalog licensing and reduce portfolio risk."*
