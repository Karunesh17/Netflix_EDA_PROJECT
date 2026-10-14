# TMDb Movie Data Analysis

I built this project to explore movie data and practice working with Python, SQL, and data visualization. I wanted to understand which genres are most common, how movie releases have changed over time, and whether a movie's popularity relates to its audience ratings.

The project analyzes a dataset of **9,827 movies** from The Movie Database (TMDb). I cleaned the data in Python, built a relational database in SQLite to practice analytical SQL queries, created charts to spot patterns, and built an interactive Streamlit dashboard so anyone can explore the dataset themselves.

> **Note on Project Name & Dataset:**  
> This repository was originally named `Netflix_EDA_PROJECT`. When I first explored the data (`mymoviedb.csv`), I realized it isn't an internal Netflix catalog—it's a dataset of movies from The Movie Database (TMDb). It contains only movies (no TV shows) and includes attributes like genre, original language, release date, audience vote average, vote count, and popularity score. I decided to keep the original repository and do an honest, detailed movie analysis with it.

---

## Why I Built This

As a student preparing for entry-level Data Analyst roles, I wanted to build an end-to-end project where I could:
- Practice data cleaning and deal with real data quality issues (like missing values, multi-genre strings, and unrated movies).
- Write practical SQL queries using joins, aggregations, CTEs, and window functions.
- Create clear, easy-to-read charts that answer specific questions rather than just making charts for the sake of it.
- Build an interactive dashboard using Streamlit and Plotly to let users filter the data dynamically.
- Explain my findings clearly and simply, just as I would in an interview or to a teammate.

---

## Dataset

- **Source:** The Movie Database (TMDb) via Kaggle (`mymoviedb.csv`)
- **Total Records:** 9,827 movies
- **Time Period:** 1902 to 2022
- **Main Columns:** `Title`, `Release_Date`, `Genre`, `Original_Language`, `Vote_Average`, `Vote_Count`, `Popularity`, `Overview`

---

## Tools Used

- **Python:** For data cleaning, feature engineering, and exploratory data analysis.
- **Pandas & NumPy:** For tabular data manipulation, parsing release years, and splitting multi-label genre strings.
- **Matplotlib & Seaborn:** For static data visualizations in the Jupyter notebook.
- **SQL & SQLite:** For relational modeling, indexing, and writing analytical queries.
- **Streamlit & Plotly:** For building the interactive web dashboard.
- **Git & GitHub:** For version control.

---

## Project Structure

```text
Netflix_EDA_PROJECT/
├── data/
│   ├── mymoviedb.csv              # Raw movie dataset (9,827 rows)
│   ├── movies_cleaned.csv         # Cleaned movies dataset with movie_id
│   ├── movie_genres.csv          # Normalized 1-to-many genre table (25,793 rows)
│   └── movies_analytics.db        # SQLite database
├── notebooks/
│   └── movie_analysis.ipynb       # Jupyter notebook with step-by-step analysis
├── sql/
│   └── movie_analysis.sql         # 7 SQL queries with comments
├── dashboard/
│   └── app.py                     # Streamlit interactive dashboard
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

---

## Data Cleaning

Before jumping into charts, I spent time inspecting the data and found a few things that needed fixing:

### 1. Handling the "Zero-Vote" Movies
- I noticed that exactly **100 movies** had a `Vote_Average` of `0.0`. Looking closer at `Vote_Count`, all 100 had `0` votes. These were mostly unreleased, upcoming, or very obscure films with no user reviews.
- If I had left these as 0.0 or dropped them with `dropna()`, it would either drag down the average rating or lose 100 valid movie records.
- Instead, I created a `Rating_Status` column:
  - `'Rated'` (9,727 movies) — used when calculating average ratings and analyzing review scores.
  - `'Unrated'` (100 movies) — kept for total volume, release year counts, and genre counts.
- With this adjustment, the clean average rating for rated movies is **6.51 / 10.0** (instead of 6.44 if zeroes were included).

### 2. Splitting Multi-Label Genres
- The raw `Genre` column stored multiple genres as comma-separated text (e.g., `"Action, Adventure, Science Fiction"`).
- To analyze genres accurately without double-counting movies, I created a normalized table (`movie_genres.csv`) where each row represents one movie-genre pair. This expanded the data into **25,793 genre entries across 19 unique genres**, linked back to the movies table by `movie_id`.

### 3. Date Parsing & Year Extraction
- I converted `Release_Date` to datetime format and extracted `Release_Year` (1902–2022) to study trends over time.

### 4. Checking for Duplicates
- There were 0 full duplicate rows.
- There were 314 duplicate movie titles, but checking the release dates showed these were legitimate remakes or adaptations released in different years (e.g., *Pinocchio*, *Halloween*, *Beauty and the Beast*).

---

## Key Findings

### 1. Movie Releases and the 2020 Drop
- Movie releases grew steadily by **+28.2% between 2015 and 2019** (from 390 titles to 500 titles).
- In **2020**, releases dropped by **-9.4% YoY** (down to 453 titles), reflecting worldwide film production delays during the COVID-19 pandemic.
- In **2021**, releases rebounded sharply by **+57.6% YoY** to an all-time high of **714 titles**, as delayed films were finally released.

### 2. Most Common Genres
- **Drama** is the most common genre, appearing in **38.1% of all movies** (3,744 titles).
- **Comedy** is second at **30.8%** (3,030 titles), followed by **Action** at **27.3%** (2,686 titles) and **Thriller** at **25.3%** (2,488 titles).
- Looking at genre pairs, the most frequent combination is **Action + Adventure** (956 movies), followed by **Action + Thriller** (827 movies) and **Comedy + Romance** (742 movies).

### 3. Languages in the Catalog
- **English** dominates the catalog, accounting for **77.0%** of movies (7,570 titles).
- The remaining **23.0%** (2,257 titles) span 42 different non-English languages.
- The top non-English languages are **Japanese** (6.6%, 645 titles — driven largely by anime and Japanese cinema), **Spanish** (3.5%, 339 titles), and **French** (3.0%, 291 titles).

### 4. Ratings Distribution
- Most rated movies fall between **5.5 and 7.5 out of 10**, with the overall average at **6.51**.
- Highly rated classics with at least 1,000 votes include *The Shawshank Redemption* (8.7), *The Godfather* (8.7), and *Spirited Away* (8.5).

### 5. Popularity vs. Audience Ratings
- A movie's popularity score has only a very weak positive correlation ($r \approx 0.13$) with its audience rating.
- High popularity scores are mostly concentrated in recent blockbuster franchises (like *Spider-Man: No Way Home*), showing that heavy marketing and buzz drive popularity numbers much more than critical rating consensus.

---

## SQL Queries

I stored the cleaned tables in SQLite (`data/movies_analytics.db`) and wrote 7 queries in `sql/movie_analysis.sql` to answer specific questions:

1. **Overall Summary:** Total movies, unique titles, and clean average rating using conditional aggregation (`CASE WHEN`).
2. **Top 10 Genres:** Relational `JOIN` on the `movie_genres` bridge table calculating total count and percentage share.
3. **Language Breakdown:** Grouping languages into English, top international languages, and others.
4. **Releases by Year:** Counting annual movie releases between 2010 and 2022.
5. **Year-over-Year Growth:** Using a Common Table Expression (CTE) and the `LAG()` window function to calculate annual release percentage changes from 2015 to 2021.
6. **Top Rated Movies:** Finding the highest rated movies with at least 1,000 votes to avoid 1-vote anomalies.
7. **Genre Pairings:** Using a self-join (`g1.genre < g2.genre`) to find which genres appear together most often.

---

## Dashboard

I built an interactive dashboard using Streamlit and Plotly (`dashboard/app.py`). It includes:
- **Summary Cards:** Quick stats showing total movies, number of genres, average rating, and distinct languages based on your current filters.
- **Sidebar Filters:** Filter by release year range (slider), select multiple genres, or filter by original language.
- **Interactive Visualizations:**
  - Bar chart of the top 10 genres.
  - Line chart showing movies released per year.
  - Donut chart showing the top original languages.
  - Histogram of audience ratings with an average reference line.
  - Scatter plot comparing popularity against ratings (log scale).
- **Data Table:** A searchable preview of the filtered data.

---

## What I Learned

- **Data cleaning matters more than complex models:** Finding the 100 zero-vote unrated movies reminded me how easily default functions like `dropna()` or simple binning can distort real data if you don't inspect edge cases first.
- **How to handle multi-label categories:** Separating comma-separated genres into a relational bridge table made SQL joins and Pandas grouping much cleaner and mathematically accurate.
- **Practical SQL window functions:** Writing `LAG()` inside a CTE made calculating year-over-year percentage changes much clearer than doing it manually in spreadsheets.
- **Communicating insights simply:** Learning to write clear, direct explanations without overcomplicating things makes findings much more useful to anyone reading the project.

---

## How to Run the Project

### 1. Clone the repository
```bash
git clone https://github.com/Karunesh17/Netflix_EDA_PROJECT.git
cd Netflix_EDA_PROJECT
```

### 2. Set up a virtual environment and install dependencies
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Streamlit dashboard
```bash
streamlit run dashboard/app.py
```
Open `http://localhost:8501` in your browser.

### 4. Run the Jupyter notebook
```bash
jupyter notebook notebooks/movie_analysis.ipynb
```