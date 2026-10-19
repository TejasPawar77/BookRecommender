import os
import pandas as pd
from django.conf import settings

PROJECT_ROOT = os.path.abspath(os.path.join(settings.BASE_DIR, '..'))
CSV_PATH = os.path.join(PROJECT_ROOT, 'books_with_emotions.csv')

_df_cache = None

def load_data():
    global _df_cache
    if _df_cache is None:
        if os.path.exists(CSV_PATH):
            _df_cache = pd.read_csv(CSV_PATH)
            _df_cache.fillna('', inplace=True)
        else:
            raise FileNotFoundError(f"Dataset not found at expected path: {CSV_PATH}")
    return _df_cache

def get_recommendations(query=None, emotion=None, category=None, top_n=10):
    df = load_data()
    if df.empty:
        return []

    filtered_df = df.copy()

    if emotion and 'emotion' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['emotion'].str.contains(emotion, case=False, na=False)]

    if category and 'category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['category'].str.contains(category, case=False, na=False)]

    if query:
        search_condition = pd.Series(False, index=filtered_df.index)
        if 'title' in filtered_df.columns:
            search_condition |= filtered_df['title'].str.contains(query, case=False, na=False)
        if 'description' in filtered_df.columns:
            search_condition |= filtered_df['description'].str.contains(query, case=False, na=False)
        filtered_df = filtered_df[search_condition]

    return filtered_df.head(top_n).to_dict(orient='records')