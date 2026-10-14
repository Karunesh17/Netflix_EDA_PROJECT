# TMDb Movie Data Analysis | Python, SQL & Streamlit

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.15%2B-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end exploratory data analysis and business intelligence project evaluating **9,827 movie records** from The Movie Database (TMDb). This project demonstrates practical data analyst competencies: data cleaning and quality auditing, relational SQL modeling, exploratory visualization, interactive dashboard engineering, and business communication.

> **Project Origin & Dataset Note:**  
> While the repository retains its original legacy name (`Netflix_EDA_PROJECT`), a comprehensive data audit revealed the underlying dataset (`mymoviedb.csv`) is sourced from **The Movie Database (TMDb)**. It consists entirely of feature films (0 TV series, no streaming availability dates). The project was repurposed to provide an accurate, mathematically verified analysis of global cinema production trends.

---

## 📌 Executive Summary & Key Metrics

| Metric | Verified Value | Analytical Context |
| :--- | :--- | :--- |
| **Catalog Volume** | **9,827 movies** | Spans 1902 to 2022 (9,513 unique titles, 314 multi-year remakes) |
| **Average Rating** | **6.51 / 10.0** | Clean mean among rated titles (excludes 100 zero-vote unrated films) |
| **Pre-Pandemic Growth** | **+28.21%** | Catalog expanded steadily from 390 titles (2015) to 500 titles (2019) |
| **2020 Pandemic Shock** | **-9.40%** | Annual output contracted to 453 titles due to global production shutdowns |
| **2021 Backlog Rebound** | **+57.62% YoY** | All-time production peak at 714 releases as delayed pipelines cleared |
| **Top 3 Genres** | **Drama, Comedy, Action** | Drama leads (38.10%), Comedy (30.84%), Action (27.33%) |
| **Language Distribution** | **77.03% English** | 7,570 English titles; 42 international languages led by Japanese (6.56%) |
| **Data Quality Fix** | **100 Zero-Vote Records** | Preserved volume integrity by flagging unrated titles instead of dropping |

---

## 🎯 Core Business Questions Investigated

1. **Production Velocity:** How did global movie release volume trend from 1980 to 2022, and what was the quantifiable impact of the COVID-19 pandemic on film output?
2. **Genre Portfolio:** Which genres capture the largest catalog share, and which genre pairings (synergies) occur most frequently?
3. **Linguistic Diversity:** How concentrated is the catalog in English-language content versus international non-English markets?
4. **Data Quality & Rating Distribution:** What is the true distribution of audience ratings, and what anomalies exist in raw crowd-sourced scores?
5. **Popularity vs. Quality:** Does high viral popularity correlate with superior critical ratings, or is popularity driven primarily by franchise marketing?

---

## 🛠️ Tech Stack & Tooling

- **Data Processing & Analysis:** Python, Pandas, NumPy
- **Relational Data Modeling & Querying:** SQLite3, SQL (CTEs, Window Functions, Self-Joins)
- **Data Visualization:** Matplotlib, Seaborn, Plotly Express
- **Interactive Web App:** Streamlit (Multi-filter analytics dashboard)
- **Environment & Version Control:** Git, GitHub

---

## 📂 Project Structure

```text
Netflix_EDA_PROJECT/
│
├── data/
│   ├── mymoviedb.csv              # Raw TMDb dataset (9,827 rows)
│   ├── movies_cleaned.csv         # Cleaned primary dataset with surrogate key (movie_id)
│   ├── movie_genres.csv          # Normalized 1-to-many genre bridge table (25,793 rows)
│   └── movies_analytics.db        # Relational SQLite database with indexed tables
│
├── notebooks/
│   └── movie_analysis.ipynb       # 7-section end-to-end Jupyter analysis notebook
│
├── sql/
│   └── movie_analysis.sql         # 7 production-grade analytical SQL queries
│
├── dashboard/
│   └── app.py                     # Interactive Streamlit analytics dashboard
│
├── requirements.txt               # Streamlined Python dependencies
├── .gitignore                     # Git ignore rules (excludes virtual environments)
└── README.md                      # Executive project documentation
```

---

## 🔍 Data Quality Audit & The "Zero-Vote" Anomaly

During initial data inspection, a critical data quality issue was identified:

- **The Discovery:** Exactly **100 movies** had a `Vote_Average` of `0.0` with `Vote_Count == 0`. These were unreleased, upcoming, or obscure films without audience reviews.
- **The Risk:** Common introductory EDA notebooks use `pd.cut()` without a lower inclusive bound or run `df.dropna()`, silently corrupting or discarding 100 records and biasing summary metrics.
- **The Engineering Solution:** Rather than discarding valid catalog items or artificially imputing a fake rating (such as mean 6.5), an explicit engineered feature `Rating_Status` was created:
  - `Rating_Status = 'Rated'` (9,727 movies, evaluated for rating metrics)
  - `Rating_Status = 'Unrated'` (100 movies, preserved for catalog volume counts)
- **Outcome:** Clean catalog average rating of **6.51 / 10.0** calculated without skew or data loss.

---

## 📊 Key Analytical Insights

### 1. Release Trends & Macro Shocks
- Between **2015 and 2019**, movie releases grew by **+28.21%** (from 390 to 500 titles).
- In **2020**, global pandemic shutdowns resulted in a **-9.40% YoY drop** (falling to 453 titles).
- In **2021**, release volume surged **+57.62% YoY** (reaching 714 titles), capturing the release of accumulated production backlogs.

### 2. Genre Dominance & Synergies
- **Drama** is the primary genre, present in **3,744 films (38.10%)**, followed by **Comedy (3,030 films, 30.84%)** and **Action (2,686 films, 27.33%)**.
- Relational self-join queries revealed that the most common multi-genre combination is **Action + Adventure (956 titles)**, followed by **Action + Thriller (827 titles)** and **Comedy + Romance (742 titles)**.

### 3. Global Linguistic Footprint
- **English (`en`)** commands **77.03%** of the catalog (7,570 titles).
- International non-English titles account for **22.97%** (2,257 titles) spanning 42 languages.
- Top international cinema industries represented:
  - **Japanese (`ja`):** 645 titles (6.56%) — driven by anime and domestic cinema.
  - **Spanish (`es`):** 339 titles (3.45%) — strong cross-regional Latin American and European presence.
  - **French (`fr`):** 291 titles (2.96%) and **Korean (`ko`):** 262 titles (2.67%).

### 4. Popularity vs. Audience Acclaim
- The correlation between `Popularity` and `Vote_Average` is weakly positive ($r \approx 0.16$).
- Highly rated films with substantial consensus (e.g., *The Godfather*, *The Shawshank Redemption*, *Spirited Away*) maintain stable ratings above 8.5, while extreme viral popularity peaks are concentrated in contemporary franchise blockbusters (e.g., *Spider-Man: No Way Home*).

---

## 💻 SQL Query Portfolio (`sql/movie_analysis.sql`)

The repository includes a dedicated SQLite database and an analytical script demonstrating practical SQL capabilities:

1. **Query 1 — Catalog KPIs:** High-level volume, clean average rating, and date boundaries using conditional aggregation.
2. **Query 2 — Genre Penetration:** Relational `JOIN` against normalized bridge table `movie_genres` calculating title share percentages.
3. **Query 3 — Language Segmentation:** `CASE WHEN` categorization profiling catalog linguistic concentration.
4. **Query 4 — Annual Velocity:** Decade-by-decade release cadence, filtering 2010–2022 trends.
5. **Query 5 — YoY Growth via Window Functions:** Uses a Common Table Expression (CTE) and `LAG()` to calculate annual percentage fluctuations.
6. **Query 6 — Consensus Blockbusters:** Multi-criteria filter identifying top-rated films with minimum 1,000 audience reviews.
7. **Query 7 — Genre Synergy Matrix:** Self-join (`g1.genre < g2.genre`) discovering the most frequent co-occurring genre pairings.

---

## 🖥️ Interactive Dashboard (`dashboard/app.py`)

The Streamlit dashboard allows recruiters and stakeholders to interactively slice and explore the dataset:

- **4 High-Level KPI Cards:** Real-time updates for Total Movies, Filtered Titles, Clean Average Rating, and Median Popularity.
- **Interactive Slicers:** Dynamic Year Range slider (1902–2022), Multi-Genre selector, and Primary Language filter.
- **5 Synchronized Visualizations:**
  - *Top Genres by Title Volume* (Horizontal Bar Chart)
  - *Annual Release Velocity & Pandemic Trends* (Interactive Area Trend)
  - *Linguistic Market Distribution* (Donut Chart)
  - *Audience Rating Distribution* (Clean Histogram with 6.51 Mean Marker)
  - *Popularity vs. Rating Dynamics* (Scatter Plot with Consensus Color Scale)

---

## 🚀 How to Run the Project Locally

### 1. Clone the Repository
```bash
git clone https://github.com/Karunesh17/Netflix_EDA_PROJECT.git
cd Netflix_EDA_PROJECT
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Launch the Interactive Dashboard
```bash
streamlit run dashboard/app.py
```
*The app will automatically open in your default browser at `http://localhost:8501`.*

### 4. Run the Jupyter Notebook
```bash
jupyter notebook notebooks/movie_analysis.ipynb
```

### 5. Execute SQL Queries
You can query the SQLite database (`data/movies_analytics.db`) using any standard SQL client (DBeaver, DB Browser for SQLite, or Python sqlite3):
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/movies_analytics.db')
query = open('sql/movie_analysis.sql').read().split(';')[0]
df = pd.read_sql_query(query, conn)
print(df)
```

---

## 📄 License & Acknowledgments
- **Dataset:** TMDb 10k Movies Dataset sourced via [Kaggle](https://www.kaggle.com/).
- **License:** MIT License. Free for academic and portfolio evaluation purposes.