import os, json, re
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SECTION_MAP = {
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "machine learning": "Artificial Intelligence",
    "ml": "Artificial Intelligence",
    "technology": "Technology",
    "tech": "Technology",
    "software": "Technology",
    "hardware": "Technology",
    "cybersecurity": "Technology",
    "security": "Technology",
    "business": "Business",
    "finance": "Business",
    "economy": "Business",
    "markets": "Business",
    "startup": "Business",
    "startups": "Business",
}

SIGNIFICANCE_KEYWORDS = [
    "billion", "trillion", "million", "breakthrough", "launch", "acqui",
    "ipo", "regulation", "ban", "law", "court", "partnership", "merger",
    "record", "first", "major", "critical", "emergency", "crisis",
    "revolution", "transform", "disrupt", "announce", "release",
]

BREADTH_KEYWORDS = [
    "global", "worldwide", "industry", "market", "all", "every",
    "widespread", "national", "international", "sector", "everyone",
    "broad", "significant", "sweeping", "massive",
]


def normalise_topic(topic: str) -> str:
    return SECTION_MAP.get(topic.lower().strip(), "Technology")


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate(articles: list) -> list:
    """Cluster articles by title similarity; keep one representative per cluster."""
    kept = []
    used = set()
    for i, art in enumerate(articles):
        if i in used:
            continue
        cluster = [art]
        for j, other in enumerate(articles):
            if j <= i or j in used:
                continue
            if title_similarity(art["title"], other["title"]) >= 0.55:
                cluster.append(other)
                used.add(j)
        # Pick the article with the longest body_excerpt as cluster representative
        best = max(cluster, key=lambda x: len(x.get("body_excerpt", "")))
        kept.append(best)
        used.add(i)
    return kept


def score_article(article: dict) -> float:
    text = (article.get("title", "") + " " + article.get("body_excerpt", "")).lower()

    # Recency proxy: articles mentioning time words score slightly higher
    recency_score = 1.0
    if any(w in text for w in ["today", "yesterday", "this week", "just", "breaking", "latest", "new"]):
        recency_score = 2.0

    # Significance
    sig_score = sum(1 for kw in SIGNIFICANCE_KEYWORDS if kw in text)

    # Breadth of impact
    breadth_score = sum(1 for kw in BREADTH_KEYWORDS if kw in text)

    return recency_score + sig_score * 1.5 + breadth_score * 1.0


def truncate_headline(title: str, max_words: int = 12) -> str:
    words = title.split()
    if len(words) <= max_words:
        return title
    return " ".join(words[:max_words]) + "…"


def build_summary(title: str, excerpt: str) -> str:
    """Return a 2–3 sentence plain-language summary from the excerpt."""
    # Split excerpt into sentences
    sentences = re.split(r'(?<=[.!?])\s+', excerpt.strip())
    # Keep up to 3 meaningful sentences
    good = [s for s in sentences if len(s.split()) >= 5][:3]
    if len(good) >= 2:
        return " ".join(good)
    # Fallback: use up to 280 chars of excerpt
    fallback = excerpt[:280].rsplit(" ", 1)[0]
    if not fallback.endswith((".", "!", "?")):
        fallback += "."
    return fallback


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))

    articles = inp.get("articles")
    if not isinstance(articles, list) or len(articles) == 0:
        raise ValueError("'articles' must be a non-empty list of article objects.")

    # Validate each article has required fields
    required_fields = {"title", "url", "source", "body_excerpt", "topic"}
    for idx, art in enumerate(articles):
        missing = required_fields - set(art.keys())
        if missing:
            raise ValueError(f"Article at index {idx} is missing fields: {missing}")

    # 1. Deduplicate
    unique_articles = deduplicate(articles)

    # 2. Score
    scored = []
    for art in unique_articles:
        s = score_article(art)
        scored.append((s, art))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)

    # 3. Select top 5–7 (prefer diversity across sections; cap at 7)
    selected = []
    section_counts: dict = {}
    MAX_PER_SECTION = 3
    TARGET_MIN = 5
    TARGET_MAX = 7

    for score_val, art in scored:
        if len(selected) >= TARGET_MAX:
            break
        section = normalise_topic(art.get("topic", "Technology"))
        count = section_counts.get(section, 0)
        if count >= MAX_PER_SECTION and len(selected) < TARGET_MIN:
            # Allow overflow if we haven't hit the minimum yet
            pass
        elif count >= MAX_PER_SECTION:
            continue
        selected.append((score_val, art))
        section_counts[section] = count + 1

    # If still under minimum, relax section cap and fill from remaining
    if len(selected) < TARGET_MIN:
        already_urls = {a["url"] for _, a in selected}
        for score_val, art in scored:
            if len(selected) >= TARGET_MAX:
                break
            if art["url"] not in already_urls:
                selected.append((score_val, art))
                already_urls.add(art["url"])

    # 4. Check minimum threshold
    if len(selected) < 5:
        result = {"stories": [], "skip_send": True}
        print(json.dumps(result))
        raise SystemExit(0)

    # 5. Build output story objects
    max_score = selected[0][0] if selected else 0
    stories = []
    for rank, (score_val, art) in enumerate(selected):
        section = normalise_topic(art.get("topic", "Technology"))
        story = {
            "headline": truncate_headline(art["title"], 12),
            "summary": build_summary(art["title"], art.get("body_excerpt", "")),
            "source_name": art.get("source", ""),
            "url": art.get("url", ""),
            "assigned_section": section,
            "top_story": (score_val == max_score and rank == 0),
        }
        stories.append(story)

    # Ensure exactly one top_story=true
    if not any(s["top_story"] for s in stories):
        stories[0]["top_story"] = True

    result = {"stories": stories, "skip_send": False}
    print(json.dumps(result))

except SystemExit:
    pass
except Exception as e:
    print(json.dumps({"error": str(e)}))