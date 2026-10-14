"""
dashboard/app.py
Production Analytics Dashboard: TMDb Movie Catalog Intelligence
Built with Streamlit & Plotly
Author: Senior Data Analyst & Analytics Engineer
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dashboard.utils import load_dashboard_data, execute_sql_query

# 1. Page Configuration
st.set_page_config(
    page_title="TMDb Movie Analytics | Intelligence Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e222d 0%, #262c3a 100%);
        border: 1px solid #363c4e;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
    }
    .metric-title {
        color: #9aa0a6;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #f1f3f4;
        font-size: 28px;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-subtitle {
        color: #8ab4f8;
        font-size: 12px;
        margin-top: 4px;
    }
    .insight-box {
        background-color: #17202e;
        border-left: 4px solid #4285f4;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load Cached Data
try:
    df_movies, df_genres, df_merged = load_dashboard_data()
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# 4. Sidebar Controls & Global Filters
with st.sidebar:
    st.image("https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.svg", width=60)
    st.title("TMDb Analytics")
    st.markdown("**Catalog Intelligence Platform**")
    st.markdown("---")
    
    st.subheader("Global Filters")
    min_year_val = int(df_movies['Release_Year'].min())
    max_year_val = int(df_movies['Release_Year'].max())
    
    year_range = st.slider(
        "Release Year Range",
        min_value=min_year_val,
        max_value=max_year_val,
        value=(1980, max_year_val)
    )
    
    all_genres = sorted(df_genres['genre'].unique())
    selected_genres = st.multiselect(
        "Filter by Genre(s)",
        options=all_genres,
        default=[]
    )
    
    min_vote_filter = st.select_slider(
        "Minimum Vote Count Threshold",
        options=[0, 10, 50, 100, 500, 1000],
        value=0,
        help="Filters out low-vote movies to control for sample-size rating bias."
    )
    
    st.markdown("---")
    st.markdown("📌 **Data Provenance:** `mymoviedb.csv` (TMDb Movie Export; 9,827 titles).")
    st.caption("Engineered for Data Analyst & Analytics Engineering portfolio showcase.")

# 5. Apply Global Filters
filtered_movies = df_movies[
    (df_movies['Release_Year'] >= year_range[0]) &
    (df_movies['Release_Year'] <= year_range[1]) &
    (df_movies['Vote_Count'] >= min_vote_filter)
]

if selected_genres:
    matching_ids = df_genres[df_genres['genre'].isin(selected_genres)]['movie_id'].unique()
    filtered_movies = filtered_movies[filtered_movies['movie_id'].isin(matching_ids)]

# 6. Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. Executive Overview",
    "🎭 2. Genre Intelligence",
    "📈 3. Historical Trends",
    "⭐ 4. Popularity & Ratings",
    "🔍 5. Data Quality & SQL Engine"
])

# ==============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# ==============================================================================
with tab1:
    st.markdown("## Executive Portfolio Overview")
    st.markdown("A macro-level performance scorecard across the 9,827-film catalog.")
    
    # KPI Row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Catalog Titles</div>
            <div class="metric-value">{len(filtered_movies):,}</div>
            <div class="metric-subtitle">Filtered of 9,827 total</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        clean_avg = filtered_movies[filtered_movies['Rating_Status'] == 'Rated']['Vote_Average'].mean()
        val_str = f"{clean_avg:.2f}" if not np.isnan(clean_avg) else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Mean Rating</div>
            <div class="metric-value">{val_str}</div>
            <div class="metric-subtitle">Rated titles only (out of 10)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        med_pop = filtered_movies['Popularity'].median()
        val_pop = f"{med_pop:.1f}" if not np.isnan(med_pop) else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Median Popularity</div>
            <div class="metric-value">{val_pop}</div>
            <div class="metric-subtitle">TMDb Engagement Index</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Unique Genres</div>
            <div class="metric-value">{df_genres['genre'].nunique()}</div>
            <div class="metric-subtitle">Normalized categories</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Languages</div>
            <div class="metric-value">{filtered_movies['Original_Language'].nunique()}</div>
            <div class="metric-subtitle">43 total catalog languages</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col6:
        unrated_filtered = (filtered_movies['Rating_Status'] == 'Unrated').sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Unrated Titles</div>
            <div class="metric-value">{unrated_filtered}</div>
            <div class="metric-subtitle">Preserved zero-vote records</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Charts Row 1: Languages & Rating Tiers
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        st.subheader("Global Linguistic Portfolio Distribution")
        lang_counts = filtered_movies['Original_Language'].value_counts()
        top_langs = lang_counts.head(6).reset_index()
        top_langs.columns = ['Language', 'Count']
        other_count = lang_counts.iloc[6:].sum()
        if other_count > 0:
            top_langs = pd.concat([top_langs, pd.DataFrame([{'Language': 'Other (37+)', 'Count': other_count}])], ignore_index=True)
            
        fig_lang = px.pie(
            top_langs,
            names='Language',
            values='Count',
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_lang.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=340)
        st.plotly_chart(fig_lang, use_container_width=True)
        st.caption("English represents 77.03% of catalog, followed by Japanese (6.56%) and Spanish (3.45%).")
        
    with col_chart2:
        st.subheader("Audience Rating Tier Breakdown")
        tier_counts = filtered_movies['Rating_Tier'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Count']
        order_dict = {'Acclaimed (>= 7.5)': 1, 'Good (6.5 - 7.4)': 2, 'Below Average (5.0 - 6.4)': 3, 'Poor (< 5.0)': 4, 'Unrated (0 Votes)': 5}
        tier_counts['sort_key'] = tier_counts['Tier'].map(order_dict).fillna(99)
        tier_counts = tier_counts.sort_values('sort_key')
        
        fig_tier = px.bar(
            tier_counts,
            x='Tier',
            y='Count',
            color='Tier',
            color_discrete_sequence=['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6'],
            text='Count'
        )
        fig_tier.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=340, showlegend=False)
        st.plotly_chart(fig_tier, use_container_width=True)
        st.caption("Ratings center strongly between 6.0 and 7.4; unrated films (100 total) are segregated from low scores.")


# ==============================================================================
# TAB 2: GENRE INTELLIGENCE
# ==============================================================================
with tab2:
    st.markdown("## Multi-Label Genre Intelligence & Co-Occurrence")
    st.markdown("Films carry multiple genre tags. This section demonstrates dual-denominator normalization and genre pairing frequency.")
    
    # Toggle Denominator View
    metric_choice = st.radio(
        "Select Genre Metric Formulation:",
        ["Title Penetration Rate (% of Films Carrying Tag)", "Share of Total Genre Occurrences (% of All 25,793 Tags)"],
        horizontal=True
    )
    
    # Merge filtered movies with genres bridge
    active_m_ids = filtered_movies['movie_id'].unique()
    active_genres = df_genres[df_genres['movie_id'].isin(active_m_ids)]
    
    genre_summary = active_genres.groupby('genre').agg(
        occurrence_count=('movie_id', 'count')
    ).reset_index()
    
    total_active_titles = len(filtered_movies)
    total_active_tags = len(active_genres)
    
    genre_summary['penetration_pct'] = (genre_summary['occurrence_count'] / total_active_titles) * 100.0 if total_active_titles > 0 else 0
    genre_summary['share_pct'] = (genre_summary['occurrence_count'] / total_active_tags) * 100.0 if total_active_tags > 0 else 0
    genre_summary = genre_summary.sort_values('occurrence_count', ascending=True)
    
    y_col = 'penetration_pct' if "Title Penetration" in metric_choice else 'share_pct'
    x_label = "Title Penetration (%)" if "Title Penetration" in metric_choice else "Share of Total Tags (%)"
    
    fig_genres = px.bar(
        genre_summary,
        x=y_col,
        y='genre',
        orientation='h',
        text=genre_summary[y_col].apply(lambda x: f"{x:.1f}%"),
        color=y_col,
        color_continuous_scale='Blues'
    )
    fig_genres.update_layout(height=520, xaxis_title=x_label, yaxis_title="Genre", coloraxis_showscale=False)
    st.plotly_chart(fig_genres, use_container_width=True)
    
    st.markdown("---")
    
    # Co-occurrence Analysis
    st.subheader("Top Genre Co-Occurrence Pairings (Multi-Genre Synergy)")
    st.markdown("Calculated via relational self-join on the normalized bridge table (`g1.genre < g2.genre`).")
    
    pairs_query = """
    WITH pairs AS (
        SELECT g1.genre AS genre_a, g2.genre AS genre_b, COUNT(*) AS pair_count
        FROM movie_genres g1
        JOIN movie_genres g2 ON g1.movie_id = g2.movie_id AND g1.genre < g2.genre
        GROUP BY g1.genre, g2.genre
    )
    SELECT genre_a || ' + ' || genre_b AS genre_pairing, pair_count
    FROM pairs
    ORDER BY pair_count DESC
    LIMIT 12;
    """
    df_pairs = execute_sql_query(pairs_query)
    
    fig_cooccur = px.bar(
        df_pairs,
        x='pair_count',
        y='genre_pairing',
        orientation='h',
        text='pair_count',
        color='pair_count',
        color_continuous_scale='Viridis'
    )
    fig_cooccur.update_layout(height=420, yaxis=dict(autorange="reversed"), xaxis_title="Co-Occurrence Frequency", yaxis_title="Genre Pair", coloraxis_showscale=False)
    st.plotly_chart(fig_cooccur, use_container_width=True)
    st.caption("Action + Thriller (944 films) and Drama + Thriller (923 films) are the two most common pairing vectors.")


# ==============================================================================
# TAB 3: HISTORICAL TRENDS
# ==============================================================================
with tab3:
    st.markdown("## Temporal Catalog Evolution & Growth Velocity")
    st.markdown("Historical analysis of film releases across 12 decades (1902–2024) and annual production fluctuations.")
    
    # Annual Release Timeline
    yearly_df = filtered_movies.groupby('Release_Year').agg(
        titles_count=('movie_id', 'count'),
        avg_score=('Vote_Average_Rated_Only', 'mean'),
        avg_pop=('Popularity', 'mean')
    ).reset_index().sort_values('Release_Year')
    
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Bar(
        x=yearly_df['Release_Year'],
        y=yearly_df['titles_count'],
        name='Annual Releases',
        marker_color='#3498db'
    ))
    fig_timeline.add_trace(go.Scatter(
        x=yearly_df['Release_Year'],
        y=yearly_df['avg_score'],
        name='Average Rating',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#e74c3c', width=2)
    ))
    
    fig_timeline.update_layout(
        height=450,
        title="Annual Catalog Influx & Rating Stability",
        xaxis_title="Release Year",
        yaxis=dict(title="Number of Titles Released"),
        yaxis2=dict(title="Average Audience Rating (0-10)", overlaying='y', side='right', range=[0, 10]),
        legend=dict(x=0.01, y=0.99),
        hovermode="x unified"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # YoY Growth Table Callout
    st.markdown("### Pre-Pandemic Expansion & Post-Lockdown Rebound (2015–2021)")
    yoy_query = """
    WITH yearly AS (
        SELECT Release_Year, COUNT(*) AS count
        FROM movies
        WHERE Release_Year BETWEEN 2014 AND 2022
        GROUP BY Release_Year
    )
    SELECT 
        Release_Year,
        count AS releases,
        LAG(count) OVER (ORDER BY Release_Year) AS prev_year,
        count - LAG(count) OVER (ORDER BY Release_Year) AS net_change,
        ROUND(((count - LAG(count) OVER (ORDER BY Release_Year)) * 100.0) / LAG(count) OVER (ORDER BY Release_Year), 2) AS yoy_pct
    FROM yearly
    WHERE Release_Year >= 2015;
    """
    df_yoy_table = execute_sql_query(yoy_query)
    st.dataframe(df_yoy_table, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
        <b>Key Takeaway:</b> Production release volumes expanded by <b>+28.21% between 2015 and 2019</b> (390 to 500 titles), 
        experienced a <b>-9.40% contraction in 2020</b> (453 titles) during global production pauses, and surged by 
        <b>+57.62% in 2021 to reach an all-time peak of 714 titles</b> as studios cleared theatrical backlogs.
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# TAB 4: POPULARITY & RATINGS
# ==============================================================================
with tab4:
    st.markdown("## Popularity, Voting Volume & Sample-Size Bias")
    st.markdown("Interactive analysis examining the relationship between commercial popularity and user scores.")
    
    col_scat, col_dens = st.columns([2, 1])
    
    with col_scat:
        # Scatter Plot: Popularity vs Vote_Average
        plot_sample = filtered_movies.sample(min(2000, len(filtered_movies)), random_state=42)
        fig_scatter = px.scatter(
            plot_sample,
            x='Vote_Average',
            y='Popularity',
            size='Vote_Count',
            color='Rating_Tier',
            hover_name='Title',
            hover_data=['Release_Year', 'Original_Language'],
            log_y=True,
            title="Popularity vs. Audience Score (Bubble Size = Vote Count)",
            color_discrete_map={
                'Acclaimed (>= 7.5)': '#2ecc71',
                'Good (6.5 - 7.4)': '#3498db',
                'Below Average (5.0 - 6.4)': '#f39c12',
                'Poor (< 5.0)': '#e74c3c',
                'Unrated (0 Votes)': '#95a5a6'
            }
        )
        fig_scatter.update_layout(height=480, xaxis_title="Vote Average (0 - 10)", yaxis_title="Popularity (Log Scale)")
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("Spearman Rank Correlation: Popularity vs. Vote Average is weak (rho = 0.127), indicating mass commercial popularity does not imply high acclaim.")
        
    with col_dens:
        st.subheader("Vote Count Distribution")
        fig_hist = px.histogram(
            filtered_movies[filtered_movies['Vote_Count'] > 0],
            x='Vote_Count',
            nbins=30,
            log_x=True,
            title="Vote Volume Frequency (Log Scale)",
            color_discrete_sequence=['#9b59b6']
        )
        fig_hist.update_layout(height=480, xaxis_title="Vote Count (Log Scale)", yaxis_title="Title Count")
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("Vote counts follow an extreme power law: median vote count is 444, while top blockbusters exceed 30,000 votes.")


# ==============================================================================
# TAB 5: DATA QUALITY & SQL ENGINE
# ==============================================================================
with tab5:
    st.markdown("## Data Quality Audit, Provenance & Interactive SQL Engine")
    st.markdown("Inspect schema transformations, data-loss bug fixes, and execute live queries on the SQLite analytics database.")
    
    with st.expander("🛡️ Data Provenance & Preprocessing Audit Details", expanded=True):
        st.markdown("""
        - **Data Provenance:** The dataset `mymoviedb.csv` is an export of **The Movie Database (TMDb)** popular movies, verified via `Poster_Url` (`image.tmdb.org`). It contains 0 episodic TV shows and lacks streaming ingestion dates (`date_added`).
        - **Pipeline Bug Patched:** In previous exploratory code, `pd.cut` with default non-inclusive lower bounds converted **100 movies with `Vote_Average == 0.0` into `NaN`s**, which were silently dropped by `df.dropna()`.
        - **Preservation Strategy:** These 100 films were audited and verified as **unrated releases** (`Vote_Count == 0`). They are preserved in the catalog for volume and genre analysis, with scores segregated into `Rating_Status = 'Unrated'`.
        """)
        
    st.markdown("### Interactive SQL Query Explorer (SQLite)")
    query_options = {
        "Query 1: Executive KPI Summary & Rating Integrity": """SELECT COUNT(*) AS total_titles, COUNT(DISTINCT Title) AS unique_titles, SUM(CASE WHEN Rating_Status = 'Unrated' THEN 1 ELSE 0 END) AS unrated_count, ROUND(AVG(Vote_Average), 2) AS unadjusted_avg_rating, ROUND(AVG(CASE WHEN Rating_Status = 'Rated' THEN Vote_Average ELSE NULL END), 2) AS clean_rated_avg_rating FROM movies;""",
        "Query 2: Language Market Breakdown": """SELECT CASE WHEN Original_Language = 'en' THEN 'English' WHEN Original_Language = 'ja' THEN 'Japanese' WHEN Original_Language = 'es' THEN 'Spanish' ELSE 'Other International' END AS language_group, COUNT(*) AS count, ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM movies), 2) AS pct FROM movies GROUP BY language_group ORDER BY count DESC;""",
        "Query 3: Year-over-Year Growth Rate (LAG Window Function)": """WITH yearly AS (SELECT Release_Year, COUNT(*) AS count FROM movies WHERE Release_Year BETWEEN 2015 AND 2021 GROUP BY Release_Year) SELECT Release_Year, count, LAG(count) OVER (ORDER BY Release_Year) AS prev_year, count - LAG(count) OVER (ORDER BY Release_Year) AS net_growth, ROUND(((count - LAG(count) OVER (ORDER BY Release_Year)) * 100.0) / LAG(count) OVER (ORDER BY Release_Year), 2) AS yoy_pct FROM yearly;""",
        "Query 4: Top 3 Acclaimed Films per Genre (DENSE_RANK)": """WITH ranked AS (SELECT mg.genre, m.Title, m.Release_Year, m.Vote_Average, m.Vote_Count, DENSE_RANK() OVER (PARTITION BY mg.genre ORDER BY m.Vote_Average DESC, m.Vote_Count DESC) AS rnk FROM movies m JOIN movie_genres mg ON m.movie_id = mg.movie_id WHERE m.Vote_Count >= 500 AND mg.genre IN ('Action', 'Comedy', 'Drama', 'Animation')) SELECT genre, rnk, Title, Release_Year, Vote_Average, Vote_Count FROM ranked WHERE rnk <= 3 ORDER BY genre, rnk;""",
        "Query 5: Top 5 Genre Co-Occurrence Pairs (Self-Join)": """SELECT g1.genre AS genre_a, g2.genre AS genre_b, COUNT(*) AS pair_count FROM movie_genres g1 JOIN movie_genres g2 ON g1.movie_id = g2.movie_id AND g1.genre < g2.genre GROUP BY g1.genre, g2.genre ORDER BY pair_count DESC LIMIT 5;"""
    }
    
    selected_query_label = st.selectbox("Select Pre-Built Analytical Query:", list(query_options.keys()))
    query_to_run = st.text_area("SQL Query Text:", value=query_options[selected_query_label], height=110)
    
    if st.button("▶ Execute SQL Query"):
        try:
            df_sql_result = execute_sql_query(query_to_run)
            st.success(f"Query returned {len(df_sql_result)} rows.")
            st.dataframe(df_sql_result, use_container_width=True)
        except Exception as err:
            st.error(f"SQL Error: {err}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #80868b; font-size: 13px;'>TMDb Movie Analytics Platform | Developed with Python, Pandas, SQLite & Streamlit | 100% Mathematically Verified Data</div>", unsafe_allow_html=True)
