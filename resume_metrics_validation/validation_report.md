# Data Quality Audit & Validation Report

**Project:** Netflix Content Catalog EDA (`Netflix_EDA_PROJECT`)  
**Auditor:** Senior Data Analyst & Data Quality Auditor  
**Dataset:** `mymoviedb.csv`  
**Execution Script:** `resume_metrics_validation/netflix_metrics.py`  
**Verification Date:** October 2026  

---

## 1. Audit Scorecard & Check Status

| Check ID | Verification Objective | Expected / Target | Actual Calculated | Status | Notes |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **CHK-01** | Total Row Count | ~9,000+ titles | **9,827 rows** | **PASSED** | Exact match |
| **CHK-02** | Unique Film Titles | >9,000 titles | **9,513 unique titles** | **PASSED** | 314 duplicate title instances |
| **CHK-03** | Exact Row Duplicates | 0 duplicates | **0 rows** | **PASSED** | No identical duplicate rows |
| **CHK-04** | Title + Date Duplicates | 0 collisions | **0 rows** | **PASSED** | All duplicate names are remakes/distinct years |
| **CHK-05** | Missing Value Scan | 0 missing | **0 nulls (100% complete)** | **PASSED** | Checked all 9 columns |
| **CHK-06** | Movie / TV Show Count | Sum to total | **9,827 Movies / 0 TV Shows** | **PASSED\*** | \*Schema lacks `type`; 100% movie catalog |
| **CHK-07** | Movie / TV Show % | Total 100% | **100.0% Movies / 0.0% TV** | **PASSED** | Independent count check verified |
| **CHK-08** | Genre Multi-Label Split | Valid normalization | **25,793 occurrences across 19 genres** | **PASSED** | Comma-separated strings normalized |
| **CHK-09** | Genre Sum Verification | Equal total tags | **25,793 tags** | **PASSED** | Sum of 19 individual genres matches |
| **CHK-10** | Release Date Parsing | 0 invalid dates | **9,827 valid dates (1902–2024)** | **PASSED** | All dates successfully parsed |
| **CHK-11** | 2015–2019 Growth Rate | Mathematical verification | **+28.21% (+110 titles)** | **PASSED** | 390 titles (2015) to 500 titles (2019) |
| **CHK-12** | Peak Release Year | Global maximum | **Year 2021 (714 titles, 7.27%)** | **PASSED** | Independent `idxmax()` check |
| **CHK-13** | Language Proxy Totals | Total matches records | **43 languages, 7,570 English (77.03%)** | **PASSED** | Top 5 languages account for 91.75% |
| **CHK-14** | Rating Quartile Audit | No data loss | **100 unrated records flagged** | **PASSED** | Identified bug in notebook `pd.cut` pipeline |
| **CHK-15** | Native `type` Column | Column in schema | **ABSENT** | **FAILED (Schema Limitation)** | No native column for content type |
| **CHK-16** | Native `country` Column | Column in schema | **ABSENT** | **FAILED (Schema Limitation)** | Substituted with `Original_Language` |
| **CHK-17** | Native `date_added` Column | Column in schema | **ABSENT** | **FAILED (Schema Limitation)** | Temporal trends use `Release_Date` |
| **CHK-18** | Native MPAA `rating` Column | Column in schema | **ABSENT** | **FAILED (Schema Limitation)** | Substituted with `Vote_Average` |
| **CHK-19** | Native `duration` Column | Column in schema | **ABSENT** | **FAILED (Schema Limitation)** | Referenced in README but absent |

---

## 2. Dataset Assumptions & Provenance Analysis

### Discrepancy Between Project Title and Dataset Reality
- **Project Context & Documentation:** The GitHub repository is titled `Netflix_EDA_PROJECT`, and the `README.md` states:
  > *"This project involves an exploratory data analysis (EDA) of a Netflix dataset. The goal was to uncover insights about the content available on Netflix, such as trends in movie and TV show releases, genre distributions, and other patterns."*
- **Actual Data Ingestion:**
  - The single data file present is `mymoviedb.csv` (4.2 MB).
  - The dataset originates from **The Movie Database (TMDb)** API, confirmed by the image hosting domain in the `Poster_Url` column (`https://image.tmdb.org/t/p/original/...`).
  - In `src.ipynb` (Cell 27), the notebook author poses the question: *"What is the most frequent genre of movies released on netflix?"*, demonstrating that the analyst intended to treat this file as a Netflix proxy.
- **Auditor Assessment:** In an interview setting, claiming that `mymoviedb.csv` contains official Netflix internal streaming or ingestion data is an immediate red flag. A Senior Data Analyst must explain the distinction:
  > *"The project was structured as an exploratory analysis on an entertainment content catalog of 9,827 titles sourced via TMDb, analyzing macro-level film production, genre distribution, and international language patterns that inform streaming platform acquisition strategies."*

---

## 3. Detailed Diagnosis of Failed or Unestablished Checks

### 1. Movie vs. TV Show Breakdown
- **Requested Calculation:** Movie Count, TV Show Count, Movie %, TV Show %.
- **Finding:** No column named `type` exists in `mymoviedb.csv`.
- **Diagnosis:** The dataset is an export of popular feature films. While 214 titles carry the genre tag `TV Movie` (made-for-television movies like *Descendants* or *Hilda and the Mountain King*), there are zero episodic television series entities (no seasons, episodes, or series IDs).
- **Verified Result:** Catalog is **100.0% movies (9,827 titles)** and **0.0% TV shows (0 titles)**.

### 2. Country Distribution
- **Requested Calculation:** Top 5 countries by content count.
- **Finding:** No column named `country` or `production_country` exists in `mymoviedb.csv`.
- **Diagnosis:** Geographic origin must be inferred through the `Original_Language` column (ISO-639-1 code).
- **Verified Result:** English (`en`) leads at 77.03% (7,570 titles), followed by Japanese (`ja`: 6.56%, 645 titles), Spanish (`es`: 3.45%, 339 titles), French (`fr`: 2.97%, 292 titles), and Korean (`ko`: 1.73%, 170 titles).

### 3. Catalog Ingestion Trends vs. Production Trends
- **Requested Calculation:** Titles added to Netflix each year (`date_added`).
- **Finding:** `date_added` is completely absent from the dataset.
- **Diagnosis:** In classic Netflix datasets (such as Kaggle's `netflix_titles.csv`), `date_added` tracks when Netflix added a title to its platform, whereas `release_year` tracks original film release. Here, only `Release_Date` is available.
- **Verified Result:** Growth trends measure **historical film production release velocity**, not platform ingestion. Production grew by **+28.21% from 2015 (390 titles) to 2019 (500 titles)** and reached an all-time peak of **714 titles in 2021**.

### 4. Duration and MPAA Rating
- **Requested Calculation:** Distribution of content ratings (e.g., PG-13, TV-MA) and duration relationships.
- **Finding:** Columns `rating` and `duration` do not exist in `mymoviedb.csv`.
- **Diagnosis:** The dataset tracks audience evaluation metrics (`Vote_Average` and `Vote_Count`) rather than age maturity ratings.

---

## 4. Pipeline Vulnerability Identified in Existing Notebook (`src.ipynb`)

During the audit of `src.ipynb`, a data-loss bug was uncovered in the preprocessing phase:

```python
# Code snippet from src.ipynb (Cell 14-18):
def categorize_col(df, col, labels):
    edges = [df[col].describe()['min'],
             df[col].describe()['25%'],
             df[col].describe()['50%'],
             df[col].describe()['75%'],
             df[col].describe()['max']]
    df[col] = pd.cut(df[col], edges, labels=labels, duplicates='drop')
    return df

lables = ['not_popular', 'below_avg', 'average', 'popular']
categorize_col(df, 'Vote_Average', lables)
df.dropna(inplace=True)
```

### Impact Analysis:
1. `df['Vote_Average'].describe()['min']` equals `0.0`.
2. By default, `pd.cut()` sets `include_lowest=False`. As a result, the left-most bin interval is $(0.0, 5.9]$, which **strictly excludes 0.0**.
3. All **100 titles with `Vote_Average == 0.0` were assigned `NaN`**.
4. The subsequent call `df.dropna(inplace=True)` silently deleted all 100 rows, reducing the dataset from 9,827 to 9,727 titles.
5. In `resume_metrics_validation/netflix_metrics.py`, this bug is resolved by documenting the exact 100 zero-voted records and verifying distributions across the full, uncorrupted 9,827 rows.

---

## 5. Discrepancies Between `README.md` Claims and Calculated Data

| Item Mentioned in `README.md` | Actual Status in `mymoviedb.csv` | Auditor Recommendation |
| :--- | :--- | :--- |
| *"trends in movie and TV show releases"* | Only movies are present (0 TV series). | Update README to clarify dataset is a movie catalog. |
| *"content types (movies vs. TV shows)"* | No `type` column exists. | Remove claim or explain that catalog is 100% movies. |
| *"relationships between variables such as ... duration"* | `duration` column does not exist. | Remove mention of `duration` from README. |
| *"ratings"* | Only user vote averages (0–10) exist, not MPAA ratings. | Clarify as "audience ratings and vote volume". |
| Generic bullet: *"Explored 9,000+ titles"* | Exact verified count is **9,827 titles**. | Replace with verified number: **9,827 titles**. |

---

## 6. Recommendations for Repository Update (Phase 5)

1. **Add a "Verified Key Findings" section to `README.md`:** Highlight the exact verified catalog metrics (9,827 titles, 25,793 genre occurrences, +28.21% growth from 2015 to 2019, 77.03% English vs 22.97% international content).
2. **Clarify Data Source:** Note that the dataset (`mymoviedb.csv`) contains TMDb movie catalog records with audience ratings and multi-genre tagging.
3. **Fix `requirements.txt` typo:** Line 2 has `umpy` instead of `numpy`.
4. **Preserve Integrity:** Do not overwrite `src.ipynb` or `mymoviedb.csv`; keep all validation deliverables self-contained in `resume_metrics_validation/`.
