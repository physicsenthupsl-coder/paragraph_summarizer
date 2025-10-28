import math
import re
from collections import Counter
from typing import List, Tuple

STOPWORDS = {
    "a","an","and","the","or","but","if","while","is","am","are","was","were","be","been","being",
    "to","of","in","for","on","with","as","by","at","from","that","this","these","those","it","its",
    "into","about","over","after","before","than","then","so","such","no","nor","not","too","very",
    "can","could","should","would","may","might","must","do","does","did","doing","done","have",
    "has","had","having","you","your","yours","we","our","ours","they","their","theirs","he","his",
    "she","her","hers","i","me","my","mine","them","us","him","herself","himself","itself","ourselves",
    "yourselves","themselves","there","here","when","where","why","how","what","which","who","whom",
    "because","up","down","out","off","again","further","once","also","just","only","even","ever",
    "more","most","some","any","each","few","both","all","other","another","much","many","such"
}

SENT_SPLIT_REGEX = re.compile(
    r"(?<!\b[A-Z])(?<!\b[A-Z][a-z])(?<!\betc)(?<!\be\.g)(?<!\bi\.e)(?<!\bMr)(?<!\bMrs)(?<!\bDr)"
    r"(?<=[\.\?\!])\s+(?=[A-Z0-9])"
)
WORD_REGEX = re.compile(r"[A-Za-z0-9']+")

def split_sentences(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []
    normalized = re.sub(r"\s+", " ", text)
    if not re.search(r"[.!?]", normalized):
        return [normalized]
    parts = SENT_SPLIT_REGEX.split(normalized)
    return [s.strip() for s in parts if s.strip()]

def tokenize(text: str) -> List[str]:
    return [w.lower().strip("'") for w in WORD_REGEX.findall(text)]

def build_word_frequencies(sentences: List[str]) -> Counter:
    freq = Counter()
    for s in sentences:
        for w in tokenize(s):
            if w and w not in STOPWORDS and not w.isdigit():
                freq[w] += 1
    if not freq:
        return freq
    maxf = max(freq.values())
    for w in list(freq):
        freq[w] = freq[w] / maxf
    return freq

def score_sentences(sentences: List[str], word_freq: Counter) -> List[Tuple[int, float]]:
    scores = []
    for idx, s in enumerate(sentences):
        words = [w for w in tokenize(s) if w and w not in STOPWORDS]
        if not words:
            scores.append((idx, 0.0))
            continue
        score = sum(word_freq.get(w, 0.0) for w in words) / len(words)
        score *= (1.0 + 0.15 * math.log(1 + len(words)))
        scores.append((idx, score))
    return scores

def pick_top_sentences(
    sentences: List[str],
    scores: List[Tuple[int, float]],
    ratio: float | None = None,
    sentence_count: int | None = None,
    max_chars: int | None = None
) -> List[str]:
    if not sentences:
        return []

    n = len(sentences)
    if sentence_count is None:
        ratio = 0.3 if ratio is None else ratio
        sentence_count = max(1, min(n, int(round(n * ratio))))

    top = sorted(scores, key=lambda x: x[1], reverse=True)[:sentence_count]
    top_idxs = sorted(idx for idx, _ in top)
    selected = [sentences[i] for i in top_idxs]

    if max_chars is not None:
        out, total = [], 0
        for s in selected:
            add_len = len(s) + (1 if out else 0)
            if total + add_len <= max_chars:
                out.append(s)
                total += add_len
            else:
                break
        selected = out if out else [selected[0][:max_chars]]
    return selected

def summarize(text: str, ratio: float | None = None, sentences: int | None = None, max_chars: int | None = None) -> str:
    sents = split_sentences(text)
    if not sents:
        return ""
    word_freq = build_word_frequencies(sents)
    scores = score_sentences(sents, word_freq)
    summary_sents = pick_top_sentences(sents, scores, ratio, sentences, max_chars)
    return " ".join(summary_sents)
