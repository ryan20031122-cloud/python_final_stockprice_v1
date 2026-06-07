from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def score_sentiment(text: str) -> tuple[str, float]:
    if not text:
        return "neutral", 0.0
    score = _analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        label = "positive"
    elif score <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return label, float(score)
