import re
from collections import Counter

TRANSITIONS = {
    "however", "therefore", "moreover", "furthermore", "firstly", "secondly",
    "finally", "although", "because", "consequently", "similarly", "instead",
    "meanwhile", "in addition", "for example", "for instance"
}

REWRITES = {
    "in order to": "to",
    "due to the fact that": "because",
    "at this point in time": "now",
    "a large number of": "many",
    "in the event that": "if",
    "has the ability to": "can",
    "make use of": "use",
    "a number of": "several",
    "in spite of the fact that": "although",
    "on a daily basis": "daily",
    "for the purpose of": "to",
    "in the near future": "soon",
}


def clean_text(text):
    text = re.sub(r"<.*?>", " ", str(text))
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def basic_stats(text):
    text = str(text)
    words = re.findall(r"\b[\w']+\b", text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    counts = Counter(w.lower() for w in words)
    unique = len(counts)
    wc = len(words)
    transition_count = sum(len(re.findall(rf"\b{re.escape(t)}\b", text, re.I)) for t in TRANSITIONS)
    return {
        "word_count": wc,
        "character_count": len(text),
        "sentence_count": len(sentences),
        "paragraph_count": max(1, len(paragraphs)),
        "unique_word_count": unique,
        "vocabulary_richness": round(unique / wc, 3) if wc else 0,
        "avg_sentence_length": round(wc / len(sentences), 2) if sentences else 0,
        "avg_word_length": round(sum(map(len, words)) / wc, 2) if wc else 0,
        "long_word_ratio": round(sum(len(w) >= 7 for w in words) / wc, 3) if wc else 0,
        "punctuation_density": round(sum(text.count(x) for x in ",.!?;:") / max(1, len(text)), 4),
        "comma_count": text.count(","),
        "period_count": text.count("."),
        "question_count": text.count("?"),
        "exclamation_count": text.count("!"),
        "punctuation_count": sum(text.count(x) for x in ",.!?;:"),
        "transition_count": transition_count,
        "repeated_words": [
            {"word": w, "count": c} for w, c in counts.most_common(10)
            if c >= 3 and len(w) > 3
        ],
    }


def topic_relevance(essay, topic):
    if not topic or not topic.strip():
        return {"available": False, "score": None, "note": "Topic not supplied."}
    topic_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", topic.lower()))
    essay_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", essay.lower()))
    if not topic_words:
        return {"available": False, "score": None, "note": "Topic has no analyzable words."}
    matched = topic_words & essay_words
    overlap = len(matched) / len(topic_words)
    return {
        "available": True,
        "score": round(min(100, overlap * 100), 1),
        "matched_terms": sorted(matched),
    }


def _apply_rewrites(text):
    result = text
    changes = []
    for old, new in REWRITES.items():
        pattern = rf"\b{re.escape(old)}\b"
        if re.search(pattern, result, flags=re.I):
            result = re.sub(pattern, new, result, flags=re.I)
            changes.append({"type": "clarity", "original": old, "suggestion": new})
    return result, changes


def _split_long_sentences(text):
    # Conservative: only split semicolon clauses when both sides are reasonably complete.
    out = []
    changed = False
    for sentence in re.split(r"(?<=[.!?])\s+", text.strip()):
        if sentence.count(";") and len(sentence.split()) > 28:
            parts = [p.strip() for p in sentence.split(";") if p.strip()]
            if len(parts) > 1:
                out.extend([p.rstrip(".!?") + "." for p in parts])
                changed = True
                continue
        out.append(sentence)
    return " ".join(out), changed


def humanize(essay):
    original = str(essay).strip()
    improved, suggestions = _apply_rewrites(original)
    improved, split_changed = _split_long_sentences(improved)
    stats = basic_stats(original)

    if split_changed:
        suggestions.append({
            "type": "sentence variety",
            "original": "Long semicolon-linked sentence",
            "suggestion": "Split the clause into shorter sentences so each idea has room to breathe.",
        })
    elif stats["avg_sentence_length"] > 28:
        suggestions.append({
            "type": "sentence variety",
            "original": "Long average sentence length",
            "suggestion": "Consider splitting long sentences where a new idea begins.",
        })

    if stats["repeated_words"]:
        suggestions.append({
            "type": "vocabulary",
            "original": ", ".join(x["word"] for x in stats["repeated_words"][:4]),
            "suggestion": "Review repeated wording and replace it only when a natural alternative preserves your meaning.",
        })

    if stats["transition_count"] == 0 and stats["paragraph_count"] > 1:
        suggestions.append({
            "type": "coherence",
            "original": "Few explicit transition signals detected",
            "suggestion": "Add a transition such as 'however', 'for example', or 'therefore' only where it accurately connects ideas.",
        })

    if not re.search(r"\b(I think|in my opinion|I believe|we can see)\b", improved, re.I):
        suggestions.append({
            "type": "voice",
            "original": "No first-person framing detected",
            "suggestion": "Use first-person language only when the assignment asks for your personal viewpoint.",
        })

    return {
        "original": original,
        "improved": improved,
        "changes_made": len(suggestions),
        "suggestions": suggestions,
        "note": "This is a rule-based natural-writing rewrite. It focuses on clarity, sentence variety and readability; it is not an AI-detector bypass or authorship-concealment tool.",
    }
