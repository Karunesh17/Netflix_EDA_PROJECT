# TMDb Movie Analytics | Python, SQL & Streamlit

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.15%2B-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests: Pytest](https://img.shields.io/badge/Tests-14%2F14%20Passing-success?logo=pytest&logoColor=white)](https://pytest.org/)

An end-to-end analytics engineering and exploratory data analysis project examining **9,827 feature films across 12 decades (1902–2024)**. Features a reproducible Python preprocessing pipeline, multi-label genre normalization, relational SQLite database modeling, 8 production-grade SQL analytical queries, and an interactive Streamlit intelligence dashboard.

---

## 📌 Executive Summary & Data Provenance

* **Repository Context:** While historically titled `Netflix_EDA_PROJECT`, a rigorous data quality audit revealed that the underlying dataset (`mymoviedb.csv`) is an export of **The Movie Database (TMDb)** popular movies API, verified via image asset URLs (`image.tmdb.org`).
* **Catalog Scope:** 9,827 movie records spanning 43 original languages, 19 normalized genre classifications, user review averages, and commercial popularity metrics.
* **Integrity Audit:** Zero missing values across all 9 raw columns; zero identical duplicate rows across title and release date; 314 duplicate title names audited and verified as historical remakes (e.g., *A Nightmare on Elm Street* in 1984 vs. 2010).
* **Data-Loss Bug Patched:** Audited and resolved a critical pipeline flaw where unhandled lower quantile bounds in `pd.cut` inadvertently converted **100 unrated films (`Vote_Count == 0`) into NaNs**, which were then deleted by `df.dropna()`. All 100 films are now preserved and segregated into verified `Rating_Status = 'Unrated'`.

---

## 🏗️ Architecture & Project Structure

```
Netflix_EDA_PROJECT/
├── data/
│   ├── raw/
│   │   └── mymoviedb.csv              # Pristine raw source dataset (9,827 rows)
│   └── processed/
│       ├── movies_cleaned.csv         # Cleaned, un-exploded movie table (9,827 rows)
│       ├── movie_genres.csv           # Normalized bridge table: movie_id <-> genre (25,793 rows)
│       └── movies_analytics.db        # Relational SQLite database with indexed tables
├── src/
│   ├── preprocessing.py               # Reproducible ETL pipeline & data validation assertions
│   ├── analysis.py                    # Advanced statistics, Spearman correlations & KW tests
│   ├── db_manager.py                  # DDL schema setup, indexing, and SQLite loading
│   └── run_sql_queries.py             # SQL query execution runner with Pandas parity checks
├── sql/
│   ├── 01_schema_setup.sql            # Table definitions, constraints, and indexes
│   ├── 02_aggregations.sql            # Executive summaries, language breakdowns, CASE WHEN
│   ├── 03_window_functions.sql        # LAG() YoY growth, DENSE_RANK() top films, cumulative sums
│   └── 04_genre_analytics.sql         # Multi-label joins, self-join co-occurrence, divergence
├── dashboard/
│   ├── app.py                         # 5-tab Streamlit & Plotly interactive dashboard
│   └── utils.py                       # High-performance cached data loaders & query executor
├── tests/
│   ├── test_data_quality.py           # Pytest: row counts, null bounds, zero-rate preservation
│   ├── test_metrics_consistency.py    # Pytest: SQL vs. Pandas mathematical parity assertions
│   └── test_dashboard_loading.py      # Pytest: data loading speed & cache integrity
├── reports/
│   ├── business_insights.md           # 6 defensible, evidence-backed strategy insights
│   └── portfolio_optimization.md      # Resume bullets, LinkedIn summary & interview Q&As
├── resume_metrics_validation/          # Standalone verification deliverables & audit scorecard
├── requirements.txt                   # Production environment dependencies
└── README.md                          # Project documentation
```

---

## 📊 Mathematically Verified Key Findings

| Domain | Verified Metric | Denominator / Formulation | Key Insight |
| :--- | :--- | :--- | :--- |
| **Catalog Scope** | **9,827 Titles** | $N = 9,827$ films | 100% movies (0 TV series); 0 missing values; 0 date collisions. |
| **Unrated Inventory** | **100 Titles (1.02%)** | $100 / 9,827 \times 100$ | Titles with 0 votes preserved; prevents artificial rating distortion. |
| **Clean Rating Average** | **6.51 / 10.0** | $N = 9,727$ rated films | Median: 6.50; IQR: $[5.90 - 7.10]$; Std: 0.93. |
| **Top Genre: Drama** | **38.10% Penetration** | 3,744 / 9,827 titles | 14.52% of all 25,793 genre tags. Core portfolio driver. |
| **2nd Genre: Comedy** | **30.84% Penetration** | 3,031 / 9,827 titles | 11.75% of all genre tags. Broad-appeal format. |
| **3rd Genre: Action** | **27.33% Penetration** | 2,686 / 9,827 titles | 10.41% of all genre tags. High commercial blockbuster volume. |
| **Pre-Pandemic Growth** | **+28.21% Expansion** | $(500 - 390) / 390 \times 100$ | Steady growth from 390 titles (2015) to 500 titles (2019). |
| **Pandemic Shock** | **-9.40% Contraction** | $(453 - 500) / 500 \times 100$ | Production halted during 2020 global industry shutdowns. |
| **Backlog Rebound** | **+57.62% YoY Surge** | $(714 - 453) / 453 \times 100$ | **All-time peak of 714 titles in 2021** as studios cleared backlogs. |
| **Language Distribution** | **77.03% English** | 7,570 / 9,827 titles | Non-English spans 42 languages led by Japanese (6.56%) & Spanish (3.45%). |

---

## 🗄️ Relational SQL Analytics (SQLite)

The project includes **8 production-grade SQL queries** executing against a normalized relational schema (`movies` and `movie_genres`). Every query has been validated with unit tests to confirm parity against Pandas:

1. **Executive KPI Summary:** Segregates unrated titles from rated averages using conditional `CASE WHEN`.
2. **Language Market Penetration:** Groups 43 language codes into strategic global tiers.
3. **Year-over-Year Growth Rate:** Employs `LAG()` window function to model annual release velocity and volatility.
4. **Cumulative Production Velocity:** Uses `SUM() OVER (ORDER BY Decade)` to compute catalog modernity (54.8% released $\ge 2010$).
5. **Top 3 Acclaimed Films per Genre:** Uses `DENSE_RANK() OVER (PARTITION BY genre ORDER BY Vote_Average DESC)` with sample-size filters ($N \ge 500$ votes).
6. **Normalized Genre Portfolio Volume:** Joins the bridge table to report dual denominators (Tag Share vs. Title Penetration).
7. **Genre Co-Occurrence Matrix:** Executes a relational self-join (`g1.genre < g2.genre`) to identify top multi-genre vectors (Action + Thriller: 944 films; Drama + Thriller: 923 films).
8. **Commercial vs. Acclaimed Divergence:** Categorizes films into performance quadrants (Universal Hits, Commercial Drivers, Hidden Gems).

---

## 💻 Interactive Streamlit Intelligence Dashboard

The application (`dashboard/app.py`) provides an interactive interface built with Streamlit and Plotly:

* **Tab 1: Executive Overview:** High-level KPI metric cards, global linguistic distribution donut chart, and rating tier distributions.
* **Tab 2: Genre Intelligence:** Multi-label bar charts with dynamic denominator toggles and top co-occurrence pairings.
* **Tab 3: Historical Trends:** Dual-axis release timeline, year-range sliders, and pre/post-lockdown YoY tables.
* **Tab 4: Popularity & Ratings:** Interactive bubble charts with log-scale popularity and dynamic vote-count threshold sliders ($0, 10, 50, 100, 500, 1000$) to demonstrate sample-size bias.
* **Tab 5: Data Quality & SQL Engine:** Live SQL query explorer enabling recruiters to execute SQLite queries directly within the dashboard.

---

## 🧪 Automated Testing & Verification Suite

All core pipeline components, schema constraints, and statistical metrics are validated using `pytest`:

```bash
# Run complete test suite (14 tests)
pytest tests/ -v
```

```
============================= test session starts =============================
tests/test_dashboard_loading.py::test_dashboard_data_loading PASSED      [  7%]
tests/test_dashboard_loading.py::test_dashboard_query_executor PASSED    [ 14%]
tests/test_data_quality.py::test_row_counts PASSED                       [ 21%]
tests/test_data_quality.py::test_unique_movie_ids PASSED                 [ 28%]
tests/test_data_quality.py::test_no_unexpected_nulls PASSED              [ 35%]
tests/test_data_quality.py::test_unrated_zero_vote_preservation PASSED   [ 42%]
tests/test_data_quality.py::test_genre_normalization_integrity PASSED    [ 50%]
tests/test_data_quality.py::test_date_parsing_range PASSED               [ 57%]
tests/test_data_quality.py::test_duplicate_handling_logic PASSED         [ 64%]
tests/test_metrics_consistency.py::test_sql_pandas_total_count_parity PASSED [ 71%]
tests/test_metrics_consistency.py::test_sql_pandas_clean_mean_rating_parity PASSED [ 78%]
tests/test_metrics_consistency.py::test_sql_pandas_top_5_genres_parity PASSED [ 85%]
tests/test_metrics_consistency.py::test_sql_pandas_growth_rates_parity PASSED [ 92%]
tests/test_metrics_consistency.py::test_percentage_sums PASSED           [100%]
============================= 14 passed in 3.93s ==============================
```

---

## 🚀 Local Installation & Quickstart

### Prerequisites
* Python 3.10 or higher
* Recommended: Virtual environment (`venv` or `conda`)

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/Karunesh17/Netflix_EDA_PROJECT.git
cd Netflix_EDA_PROJECT

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Data Preprocessing Pipeline
```bash
python src/preprocessing.py
```

### 3. Initialize SQLite Database & Execute SQL Queries
```bash
python src/db_manager.py
python src/run_sql_queries.py
```

### 4. Run Automated Test Suite
```bash
pytest tests/ -v
```

### 5. Launch Interactive Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

---

## 🔍 Analytical Limitations & Methodological Rules

1. **Platform Scope:** The dataset reflects TMDb theatrical and streaming movie releases, not internal streaming platform viewing logs (e.g., Netflix watch-hours or subscriber retention).
2. **Temporal Distinction:** Trends reflect film `Release_Date`. Streaming catalog ingestion dates (`date_added`) are not tracked in TMDb.
3. **Rating Bias Control:** Movies with under 100 votes exhibit substantial rating variance. We employ vote-count thresholds ($N \ge 100$) for reliable ranking.
4. **Causality Guardrails:** Genre popularity and language distributions represent catalog supply and reviewer activity, not proven consumer demand causality.

---

## 📄 License & Attribution
* Dataset Source: [The Movie Database (TMDb)](https://www.themoviedb.org/) API export.
* Project Architecture & Analytics: Developed for professional Data Analyst & Analytics Engineering portfolio showcase.