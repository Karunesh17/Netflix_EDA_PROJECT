"""
src/analysis.py
Advanced Exploratory Data Analysis & Statistical Modeling Engine
Author: Senior Data Analyst & Analytics Engineer
"""

import os
import pandas as pd
import numpy as np
from scipy import stats

def load_processed_data():
    """Load cleaned movies and genre bridge tables."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    movies_path = os.path.join(base_dir, "data", "processed", "movies_cleaned.csv")
    genres_path = os.path.join(base_dir, "data", "processed", "movie_genres.csv")
    
    df_movies = pd.read_csv(movies_path)
    df_genres = pd.read_csv(genres_path)
    return df_movies, df_genres

def compute_portfolio_summary(df_movies, df_genres):
    """Calculate core portfolio-level metrics."""
    total_titles = len(df_movies)
    unique_titles = df_movies['Title'].nunique()
    total_genre_tags = len(df_genres)
    unique_genres = df_genres['genre'].nunique()
    unique_languages = df_movies['Original_Language'].nunique()
    
    rated_movies = df_movies[df_movies['Rating_Status'] == 'Rated']
    unrated_movies = df_movies[df_movies['Rating_Status'] == 'Unrated']
    
    summary = {
        "total_titles": total_titles,
        "unique_titles": unique_titles,
        "total_genre_tags": total_genre_tags,
        "unique_genres": unique_genres,
        "unique_languages": unique_languages,
        "unrated_titles_count": len(unrated_movies),
        "rated_titles_count": len(rated_movies),
        "mean_rating_all": round(df_movies['Vote_Average'].mean(), 2),
        "mean_rating_rated_only": round(rated_movies['Vote_Average'].mean(), 2),
        "median_rating_rated_only": round(rated_movies['Vote_Average'].median(), 2),
        "std_rating_rated_only": round(rated_movies['Vote_Average'].std(), 2),
        "mean_popularity": round(df_movies['Popularity'].mean(), 2),
        "median_popularity": round(df_movies['Popularity'].median(), 2),
        "iqr_popularity": [round(df_movies['Popularity'].quantile(0.25), 2), round(df_movies['Popularity'].quantile(0.75), 2)],
        "mean_vote_count": round(df_movies['Vote_Count'].mean(), 2),
        "median_vote_count": round(df_movies['Vote_Count'].median(), 2),
        "min_year": int(df_movies['Release_Year'].min()),
        "max_year": int(df_movies['Release_Year'].max())
    }
    return summary

def compute_genre_metrics(df_movies, df_genres, vote_thresholds=[0, 50, 100, 500]):
    """
    Compute genre metrics across multiple vote count thresholds to control for low-sample bias.
    Includes both Occurrence Share and Title Penetration.
    """
    total_titles = len(df_movies)
    total_genre_tags = len(df_genres)
    
    # Merge movies with genres
    df_merged = df_genres.merge(df_movies[['movie_id', 'Title', 'Popularity', 'Vote_Count', 'Vote_Average', 'Rating_Status']], on='movie_id')
    
    results_by_threshold = {}
    for threshold in vote_thresholds:
        filtered = df_merged[df_merged['Vote_Count'] >= threshold]
        filtered_titles_count = df_movies[df_movies['Vote_Count'] >= threshold]['movie_id'].nunique()
        total_filtered_tags = len(filtered)
        
        genre_grp = filtered.groupby('genre').agg(
            tag_count=('movie_id', 'count'),
            avg_rating=('Vote_Average', 'mean'),
            median_rating=('Vote_Average', 'median'),
            avg_popularity=('Popularity', 'mean'),
            median_popularity=('Popularity', 'median'),
            avg_vote_count=('Vote_Count', 'mean')
        ).reset_index()
        
        genre_grp['tag_share_pct'] = (genre_grp['tag_count'] / total_filtered_tags) * 100.0
        genre_grp['title_penetration_pct'] = (genre_grp['tag_count'] / filtered_titles_count) * 100.0
        
        genre_grp = genre_grp.sort_values('tag_count', ascending=False)
        results_by_threshold[threshold] = genre_grp
        
    return results_by_threshold

def compute_genre_cooccurrence_matrix(df_genres):
    """
    Construct a symmetrical genre co-occurrence matrix.
    Indicates how frequently pairs of genres appear together on the same movie.
    """
    # Self-join on movie_id
    pairs = df_genres.merge(df_genres, on='movie_id', suffixes=('_1', '_2'))
    # Filter out same-genre diagonal or count all
    cooccurrence = pd.crosstab(pairs['genre_1'], pairs['genre_2'])
    return cooccurrence

def compute_statistical_correlations(df_movies):
    """
    Calculate Pearson and Spearman correlations between numeric features.
    Spearman is critical due to heavy right skew in Popularity and Vote_Count.
    """
    rated = df_movies[df_movies['Rating_Status'] == 'Rated'].copy()
    
    cols = ['Popularity', 'Vote_Count', 'Vote_Average']
    pearson_corr = rated[cols].corr(method='pearson')
    spearman_corr = rated[cols].corr(method='spearman')
    
    # Specific correlation tests with p-values
    p_pop_votes, p_val_pop_votes = stats.spearmanr(rated['Popularity'], rated['Vote_Count'])
    p_votes_score, p_val_votes_score = stats.spearmanr(rated['Vote_Count'], rated['Vote_Average'])
    p_pop_score, p_val_pop_score = stats.spearmanr(rated['Popularity'], rated['Vote_Average'])
    
    tests = {
        "popularity_vs_vote_count": {"spearman_rho": round(p_pop_votes, 4), "p_value": p_val_pop_votes},
        "vote_count_vs_vote_average": {"spearman_rho": round(p_votes_score, 4), "p_value": p_val_votes_score},
        "popularity_vs_vote_average": {"spearman_rho": round(p_pop_score, 4), "p_value": p_val_pop_score}
    }
    
    return pearson_corr, spearman_corr, tests

def detect_outliers(df_movies):
    """
    Detect statistical outliers in Popularity and Vote_Count using IQR and Z-Score.
    """
    outliers = {}
    for col in ['Popularity', 'Vote_Count']:
        q25 = df_movies[col].quantile(0.25)
        q75 = df_movies[col].quantile(0.75)
        iqr = q75 - q25
        upper_bound = q75 + 1.5 * iqr
        
        iqr_outliers = df_movies[df_movies[col] > upper_bound]
        
        z_scores = np.abs(stats.zscore(df_movies[col]))
        z_outliers = df_movies[z_scores > 3]
        
        outliers[col] = {
            "q25": round(q25, 2),
            "q75": round(q75, 2),
            "iqr": round(iqr, 2),
            "upper_bound_1_5_iqr": round(upper_bound, 2),
            "iqr_outlier_count": len(iqr_outliers),
            "iqr_outlier_pct": round((len(iqr_outliers) / len(df_movies)) * 100.0, 2),
            "zscore_outlier_count": len(z_outliers),
            "zscore_outlier_pct": round((len(z_outliers) / len(df_movies)) * 100.0, 2),
            "max_record": df_movies.loc[df_movies[col].idxmax()][['Title', 'Release_Year', col]].to_dict()
        }
    return outliers

def run_genre_anova_kw_test(df_movies, df_genres, min_votes=50):
    """
    Test whether rating distributions differ significantly across top genres using Kruskal-Wallis non-parametric test.
    (Non-parametric chosen because rating distributions exhibit skew and varying sample sizes).
    """
    df_merged = df_genres.merge(df_movies[['movie_id', 'Vote_Average', 'Vote_Count', 'Rating_Status']], on='movie_id')
    filtered = df_merged[(df_merged['Vote_Count'] >= min_votes) & (df_merged['Rating_Status'] == 'Rated')]
    
    top5_genres = ['Drama', 'Comedy', 'Action', 'Thriller', 'Adventure']
    genre_groups = [filtered[filtered['genre'] == g]['Vote_Average'].dropna().values for g in top5_genres]
    
    kw_stat, kw_pvalue = stats.kruskal(*genre_groups)
    
    medians = {g: round(float(np.median(vals)), 2) for g, vals in zip(top5_genres, genre_groups)}
    
    return {
        "test": "Kruskal-Wallis H-Test",
        "genres_tested": top5_genres,
        "sample_sizes": {g: len(vals) for g, vals in zip(top5_genres, genre_groups)},
        "group_medians": medians,
        "h_statistic": round(kw_stat, 4),
        "p_value": kw_pvalue,
        "significant_at_0_01": kw_pvalue < 0.01
    }

def main():
    print("=" * 60)
    print("RUNNING ADVANCED EDA & STATISTICAL ANALYSIS")
    print("=" * 60)
    df_movies, df_genres = load_processed_data()
    
    summary = compute_portfolio_summary(df_movies, df_genres)
    print(f"[+] Catalog Size: {summary['total_titles']} titles ({summary['unrated_titles_count']} unrated)")
    print(f"[+] Rated Only Average Score: {summary['mean_rating_rated_only']} (Std: {summary['std_rating_rated_only']})")
    
    genre_results = compute_genre_metrics(df_movies, df_genres)
    print("\n[+] Top 5 Genres (Baseline Threshold >= 0 Votes):")
    print(genre_results[0][['genre', 'tag_count', 'tag_share_pct', 'title_penetration_pct', 'avg_rating']].head(5))
    
    print("\n[+] Top 5 Genres (Reliability Filter >= 100 Votes):")
    print(genre_results[100][['genre', 'tag_count', 'title_penetration_pct', 'avg_rating']].head(5))
    
    _, _, corr_tests = compute_statistical_correlations(df_movies)
    print("\n[+] Non-Parametric Correlation Tests (Spearman's Rho):")
    for k, v in corr_tests.items():
        print(f"    * {k}: rho = {v['spearman_rho']}, p = {v['p_value']:.2e}")
        
    outliers = detect_outliers(df_movies)
    print("\n[+] Distribution Outliers:")
    print(f"    * Popularity > {outliers['Popularity']['upper_bound_1_5_iqr']}: {outliers['Popularity']['iqr_outlier_count']} titles ({outliers['Popularity']['iqr_outlier_pct']}%)")
    print(f"    * Max Popularity: {outliers['Popularity']['max_record']['Title']} ({outliers['Popularity']['max_record']['Popularity']})")
    
    kw_result = run_genre_anova_kw_test(df_movies, df_genres)
    print(f"\n[+] Kruskal-Wallis Test on Top 5 Genres (Votes >= 50): H = {kw_result['h_statistic']}, p = {kw_result['p_value']:.2e} (Significant: {kw_result['significant_at_0_01']})")
    print("=" * 60)

if __name__ == "__main__":
    main()
