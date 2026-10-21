def calculate_engagement_score(
    likes=0,
    comments=0,
    views=0,
    shares=0
):
    likes = likes or 0
    comments = comments or 0
    views = views or 0
    shares = shares or 0

    score = (
        comments * 4
        + shares * 5
        + likes * 1
        + views * 0.01
    )

    return round(score, 2)


def classify_engagement(score):
    if score >= 50000:
        return "Trending"

    if score >= 20000:
        return "Ramai"

    if score >= 5000:
        return "Mulai Ramai"

    return "Normal"