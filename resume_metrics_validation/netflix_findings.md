# Netflix Content Catalog EDA — Verified Quantitative Findings & Analytical Report

**Role:** Senior Data Analyst & Data Quality Auditor  
**Project:** Netflix EDA Project (`Netflix_EDA_PROJECT`)  
**Dataset Analyzed:** `mymoviedb.csv`  
**Execution Pipeline:** `resume_metrics_validation/netflix_metrics.py`  
**Date of Audit:** October 2026  

---

## Executive Summary

This report establishes **mathematically verified, reproducible metrics** for the Netflix EDA project repository. As part of a thorough data quality audit, the dataset was inspected at the schema and record level. 

A central finding of this audit is an essential **data provenance and schema distinction**: while the repository and original documentation frame the project as an analysis of the Netflix catalog, the underlying dataset file (`mymoviedb.csv`) consists of **9,827 movie records sourced from The Movie Database (TMDb)**. The dataset contains 0 TV series entities and lacks Netflix-specific ingestion metadata (such as `date_added`, `type`, and content MPAA rating). 

All metrics in this report are computed **directly from the active dataset** using verifiable mathematical formulas and independent count checks, ensuring 100% reproducibility and interview defensibility.

---

## 1. Dataset Overview & Data Quality Audit

| Metric | Verified Value | Verification Method / Raw Count | Verification Status |
| :--- | :--- | :--- | :--- |
| **Total Catalog Records** | **9,827** | `len(df)` | **PASSED** (Exact match) |
| **Unique Film Titles** | **9,513** | `df['Title'].nunique()` | **PASSED** |
| **Exact Full-Row Duplicates** | **0** | `df.duplicated().sum()` | **PASSED** (0 duplicate rows) |
| **Duplicate Title Occurrences** | **314** | `df.duplicated(subset=['Title']).sum()` | **PASSED** (602 rows across 288 distinct titles) |
| **Duplicate Title & Date Collisions** | **0** | `df.duplicated(subset=['Title', 'Release_Date']).sum()` | **PASSED** (All duplicate titles are distinct remakes/releases) |
| **Missing / Null Values** | **0** | `df.isnull().sum().sum()` across all 9 columns | **PASSED** (Complete dataset) |
| **Movie Count & Percentage** | **9,827 (100.0%)** | 9,827 / 9,827 * 100 | **PASSED** (TMDb Film Catalog) |
| **TV Show Count & Percentage** | **0 (0.0%)** | 0 / 9,827 * 100 | **PASSED** (No episodic TV series present) |

### Key Data Integrity Findings:
1. **Title Duplication Context:** The 314 duplicate title instances (e.g., *A Nightmare on Elm Street* in 1984 vs. 2010; *Adventures in Babysitting* in 1987 vs. 2016; *365 Days* in 2015 vs. 2020) represent different productions, remakes, or adaptations across different years. Zero titles share both the same name and release date.
2. **Notebook Data Pipeline Flaw:** In the original `src.ipynb` notebook (Cell 15), `pd.cut` was applied to `Vote_Average` using quartile bins with default parameters (`include_lowest=False`). This converted the **100 records with `Vote_Average == 0.0` into `NaN` values**, which were then permanently deleted by `df.dropna(inplace=True)` (Cell 18), artificially reducing the working dataset from 9,827 to 9,727 rows.

---

## 2. Content Distribution Analysis

### A. Genre Distribution & Dual Denominator Analysis
Titles in the catalog are multi-genre (comma-separated strings). Across 9,827 titles, there are **2,337 unique raw genre string combinations**, which normalize into **19 distinct genre classifications** totaling **25,793 genre occurrences** (an average of 2.62 genres per title).

To avoid ambiguity, genre metrics must be presented using both standard analytical denominators:
- **Occurrence Denominator ($N_{occ} = 25,793$):** Share of total genre tags across all films. Sums to 100.0%.
- **Title Penetration Denominator ($N_{titles} = 9,827$):** Percentage of unique catalog films that include that genre tag. Sums to $>100.0\%$ due to multi-genre tagging.

| Rank | Genre | Raw Count | Share of Genre Tags ($N=25,793$) | Title Penetration ($N=9,827$) | Formula (Title Penetration) |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **Drama** | 3,744 | **14.52%** | **38.10%** | $(3,744 / 9,827) \times 100$ |
| **2** | **Comedy** | 3,031 | **11.75%** | **30.84%** | $(3,031 / 9,827) \times 100$ |
| **3** | **Action** | 2,686 | **10.41%** | **27.33%** | $(2,686 / 9,827) \times 100$ |
| **4** | **Thriller** | 2,488 | **9.65%** | **25.32%** | $(2,488 / 9,827) \times 100$ |
| **5** | **Adventure** | 1,853 | **7.18%** | **18.86%** | $(1,853 / 9,827) \times 100$ |
| *Top 5 Combined* | *13,802* | *53.51%* | — | — |

*Remaining 14 Genres:* Romance (1,476; 15.02%), Horror (1,470; 14.96%), Animation (1,439; 14.64%), Family (1,414; 14.39%), Fantasy (1,308; 13.31%), Science Fiction (1,273; 12.95%), Crime (1,242; 12.64%), Mystery (773; 7.87%), History (427; 4.35%), War (308; 3.13%), Music (295; 3.00%), Documentary (215; 2.19%), TV Movie (214; 2.18%), Western (137; 1.39%).

### B. Geographic / Language Distribution
*Schema Clarification:* A dedicated `country` column does not exist in `mymoviedb.csv`. Production language (`Original_Language`, ISO-639-1) serves as the verified proxy for cultural and regional origin across 43 unique languages.

| Rank | Language Code | Language Name | Title Count | Percentage of Catalog ($N=9,827$) | Formula |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **1** | `en` | English | 7,570 | **77.03%** | $(7,570 / 9,827) \times 100$ |
| **2** | `ja` | Japanese | 645 | **6.56%** | $(645 / 9,827) \times 100$ |
| **3** | `es` | Spanish | 339 | **3.45%** | $(339 / 9,827) \times 100$ |
| **4** | `fr` | French | 292 | **2.97%** | $(292 / 9,827) \times 100$ |
| **5** | `ko` | Korean | 170 | **1.73%** | $(170 / 9,827) \times 100$ |
| *Top 5 Combined* | — | *Top 5 Languages* | *9,016* | **91.75%** | $(9,016 / 9,827) \times 100$ |

*Key finding:* Non-English productions constitute **22.97% (2,257 titles)** of the catalog, led by East Asian markets (Japanese and Korean combining for 8.29% of titles).

### C. Content Quality & Rating Metrics
*Schema Clarification:* MPAA ratings (G, PG, PG-13, R, NC-17) are not present in this dataset. Content reception is evaluated via audience ratings (`Vote_Average`, range $0.0 - 10.0$) and vote volumes (`Vote_Count`).

- **Mean Rating:** $6.44 \pm 1.13$
- **Median Rating:** $6.50$
- **Interquartile Range (IQR):** $5.90$ (25th percentile) to $7.10$ (75th percentile)
- **Zero-Vote Segment:** 100 titles (1.02%) have a rating of $0.0$ and $0$ votes (unreleased or low-visibility entries).
- **Corrected Quartile Distribution (including zero-votes):**
  - Not Popular ($[0.0, 5.9]$): 2,567 titles (26.12%)
  - Below Average ($(5.9, 6.5]$): 2,398 titles (24.40%)
  - Average ($(6.5, 7.1]$): 2,412 titles (24.55%)
  - Popular ($(7.1, 10.0]$): 2,450 titles (24.93%)

---

## 3. Content Growth & Historical Production Trends

### Metric Distinction: `date_added` vs. `Release_Date`
- **`date_added`:** Indicates when Netflix ingested a title onto its streaming platform. **Absent in `mymoviedb.csv`**.
- **`Release_Date` / `Release_Year`:** Indicates when the title was officially released by its studio. **Present and verified for all 9,827 titles**, spanning release years from **1902 to 2024**.

### Production Volume & Growth Trajectory:

| Year | Titles Released | Annual Share ($N=9,827$) | Cumulative Share | YoY Growth Rate |
| :---: | :---: | :---: | :---: | :---: |
| **2015** | 390 | 3.97% | 61.64% | +5.12% |
| **2016** | 470 | 4.78% | 66.42% | +20.51% |
| **2017** | 510 | 5.19% | 71.61% | +8.51% |
| **2018** | 530 | 5.39% | 77.00% | +3.92% |
| **2019** | 500 | 5.09% | 82.09% | -5.66% |
| **2020** | 453 | 4.61% | 86.70% | **-9.40%** (Pandemic impact) |
| **2021** | **714** | **7.27%** | 93.97% | **+57.62%** (All-time peak) |
| **2022** | 208* | 2.12% | 96.08% | *(Partial year snapshot)* |

### Verified Numerical Findings:
1. **2015 to 2019 Production Growth:**
   $$\text{Growth}_{2015 \to 2019} = \frac{500 - 390}{390} \times 100 = \mathbf{+28.21\%} \quad (+110 \text{ titles})$$
2. **Peak Production Year:** **2021** represents the highest single-year volume in catalog history with **714 titles (7.27% of all catalog titles)**.
3. **Pandemic Shock & Rebound:** Production dropped by **-9.40% in 2020** (453 titles vs. 500 in 2019) due to global industry shutdowns, followed by a dramatic post-lockdown release surge of **+57.62% in 2021** (+261 titles).

---

## 4. Actionable Business Insights

### Insight 1: Heavy Genre Concentration in Core Entertainment Verticals
- **Observed Pattern:** Top 4 genres (Drama: 38.1%, Comedy: 30.8%, Action: 27.3%, Thriller: 25.3%) account for 46.33% of all genre tag instances. 
- **Strategic Implication:** While Drama and Comedy serve as essential high-volume baseline engagement drivers, content acquisition is heavily saturated in these categories. High-retention, passion-driven verticals such as **Animation (14.64% of titles)** and **Sci-Fi (12.95% of titles)** represent high-leverage expansion opportunities that typically deliver higher international merchandising and fandom loyalty.

### Insight 2: Asymmetric Global Content Pipeline
- **Observed Pattern:** 77.03% (7,570 titles) of the catalog is English-language. Japanese content is the second largest individual language segment at 6.56% (645 titles), outperforming Spanish (3.45%, 339 titles) and French (2.97%, 292 titles).
- **Strategic Implication:** The strong presence of Japanese content reflects high global appetite for anime. However, Spanish-language content (3.45%) is disproportionately low relative to the 500M+ global Spanish-speaking population, pointing to a critical licensing and co-production growth corridor in Latin America and Spain.

### Insight 3: Production Pipeline Volatility Requires Licensing Balance
- **Observed Pattern:** Annual releases fluctuated sharply from steady growth (+28.21% between 2015–2019) to a -9.40% contraction in 2020 and a +57.62% backlog release surge in 2021.
- **Strategic Implication:** Over-reliance on newly produced releases leaves platform engagement vulnerable to external production disruptions (e.g., pandemic halts or labor strikes). Content strategists must balance original production pipelines with evergreen catalog acquisitions (pre-2015 titles represent 57.67% of the catalog) to maintain consistent subscriber retention.

### Insight 4: Data Pipeline Vulnerability in Automated Discretization
- **Observed Pattern:** Unchecked quartile binning in the exploratory notebook inadvertently dropped 100 unrated films ($1.02\%$ of the dataset) due to missing boundary handling (`include_lowest=False`).
- **Strategic Implication:** Automated EDA workflows must include assertion tests and boundary audits. In a production recommendation or content discovery system, dropping zero-vote or newly released unrated titles creates an algorithmic blindspot that prevents new acquisitions from being surfaced to users.

---

## 5. Analytical Limitations & Verification Summary

1. **Dataset Origin:** The file analyzed is `mymoviedb.csv` (TMDb popular movies), not the proprietary Netflix subscriber or stream log dataset.
2. **Absence of Ingestion Dates:** Streaming ingestion dates (`date_added`) cannot be measured; all temporal trends reflect theatrical/studio release dates.
3. **Absence of Content Types:** The dataset contains exclusively movies ($100.0\%$), precluding TV show vs. Movie comparative evolution over time.
4. **Denominator Disambiguation:** Genre statistics must explicitly report both Occurrence ($N=25,793$) and Title ($N=9,827$) denominators to avoid misrepresenting genre penetration.
