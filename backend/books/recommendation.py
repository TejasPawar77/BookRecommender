import os
import pandas as pd
from django.conf import settings

PROJECT_ROOT = os.path.abspath(
    os.path.join(settings.BASE_DIR, '..')
)

CSV_PATH = os.path.join(
    PROJECT_ROOT,
    'books_with_emotions.csv'
)

_df_cache = None


def load_data():
    global _df_cache

    if _df_cache is None:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(
                f"Dataset not found at expected path: {CSV_PATH}"
            )

        _df_cache = pd.read_csv(CSV_PATH)
        _df_cache.fillna('', inplace=True)

        # Clean column names
        _df_cache.columns = _df_cache.columns.str.strip()

        # Remove empty titles and duplicate books
        if 'title' in _df_cache.columns:
            _df_cache['title'] = (
                _df_cache['title'].astype(str).str.strip()
            )

            _df_cache = _df_cache[
                _df_cache['title'] != ''
            ].copy()

            _df_cache.drop_duplicates(
                subset=['title'],
                keep='first',
                inplace=True
            )

        # print("CSV PATH:", CSV_PATH)
        # print("TOTAL UNIQUE BOOKS:", len(_df_cache))

    return _df_cache


def get_recommendations(
    query=None,
    emotion=None,
    category=None,
    top_n=10
):
    df = load_data()

    if df.empty:
        return []

    filtered_df = df.copy()

    if emotion and 'emotion' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['emotion'].astype(str).str.contains(
                str(emotion).strip(),
                case=False,
                na=False,
                regex=False
            )
        ]

    if category and 'category' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['category'].astype(str).str.contains(
                str(category).strip(),
                case=False,
                na=False,
                regex=False
            )
        ]

    if query is not None and str(query).strip():
        query = str(query).strip()

        if 'title' in filtered_df.columns:
            exact_matches = filtered_df[
                filtered_df['title'].astype(str).str.strip().str.casefold()
                == query.casefold()
            ]

            title_matches = filtered_df[
                filtered_df['title'].astype(str).str.contains(
                    query,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

            if not exact_matches.empty:
                filtered_df = exact_matches

            elif not title_matches.empty:
                filtered_df = title_matches

            elif 'description' in filtered_df.columns:
                filtered_df = filtered_df[
                    filtered_df['description'].astype(str).str.contains(
                        query,
                        case=False,
                        na=False,
                        regex=False
                    )
                ]

            else:
                filtered_df = filtered_df.iloc[0:0]

        elif 'description' in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df['description'].astype(str).str.contains(
                    query,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        else:
            filtered_df = filtered_df.iloc[0:0]

    if 'title' in filtered_df.columns:
        filtered_df = filtered_df.drop_duplicates(
            subset=['title'],
            keep='first'
        )

    results = filtered_df.head(max(0, int(top_n)))

    # Debug output
    # print("MATCHING BOOKS:", len(filtered_df))

    # if 'title' in results.columns:
        # print("MATCHED TITLES:", results['title'].tolist())

    return results.to_dict(orient='records')
