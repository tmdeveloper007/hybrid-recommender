"""
NLP Sentiment Engine
Uses NLTK VADER for lightweight sentiment analysis on user review text.
"""
import nltk
import pandas as pd
import numpy as np

# Download VADER lexicon (only on first run)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

from nltk.sentiment.vader import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of a single text string.
    Returns the VADER compound score in range [-1.0, 1.0].
      > 0.05  → positive
      < -0.05 → negative
      else    → neutral
    """
    if not text or not isinstance(text, str) or text.strip() == '':
        return 0.0
    scores = _analyzer.polarity_scores(text)
    return scores['compound']


def sentiment_label(score: float) -> str:
    """
    Convert a compound VADER score to a human-readable label.

    Args:
        score: VADER compound score in range [-1.0, 1.0]

    Returns:
        'positive' if score >= 0.05, 'negative' if score <= -0.05, else 'neutral'
    """
    if score >= 0.05:
        return 'positive'
    elif score <= -0.05:
        return 'negative'
    else:
        return 'neutral'


def batch_analyze(df: pd.DataFrame, text_col: str = 'review_text') -> pd.DataFrame:
    """
    Add sentiment_score and sentiment_label columns to the DataFrame.

    Args:
        df: Input DataFrame
        text_col: Name of the text column to analyze (default: 'review_text')

    Returns:
        DataFrame with added 'sentiment_score' and 'sentiment_label' columns
    """
    df = df.copy()
    if text_col not in df.columns:
        df['sentiment_score'] = 0.0
        df['sentiment_label'] = 'neutral'
        return df

    df['sentiment_score'] = df[text_col].apply(analyze_sentiment)
    df['sentiment_label'] = df['sentiment_score'].apply(sentiment_label)
    return df


def aggregate_sentiment_by_item(df: pd.DataFrame, item_col: str = 'title') -> pd.DataFrame:
    """
    Compute average sentiment score per unique item.

    Args:
        df: DataFrame with 'sentiment_score' column (or will be computed)
        item_col: Column name to group by (default: 'title')

    Returns:
        DataFrame with columns: [item_col, 'avg_sentiment', 'review_count']
    """
    if 'sentiment_score' not in df.columns:
        df = batch_analyze(df)

    agg = df.groupby(item_col).agg(
        avg_sentiment=('sentiment_score', 'mean'),
        review_count=('sentiment_score', 'count')
    ).reset_index()

    return agg
