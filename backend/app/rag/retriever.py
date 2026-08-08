"""
RAG retriever over the MITRE corpus using TF-IDF + cosine similarity.

Deliberately not using a downloaded embedding model here: the corpus is
tiny (~14 docs) and a downloaded neural embedding model adds first-run
network dependency and startup latency for basically no retrieval-quality
gain at this scale. TF-IDF is a real, explainable retrieval step - it's
still "search the corpus, then generate grounded on what you found" (RAG),
just with a simpler and more reliable retrieval method.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.rag.mitre_corpus import MITRE_TECHNIQUES, get_techniques_for_attack_type

_vectorizer = None
_doc_vectors = None


def _doc_text(t: dict) -> str:
    return f"{t['name']} {' '.join(t['attack_types'])} {t['description']}"


def _ensure_indexed():
    global _vectorizer, _doc_vectors
    if _vectorizer is not None:
        return
    corpus = [_doc_text(t) for t in MITRE_TECHNIQUES]
    _vectorizer = TfidfVectorizer(stop_words="english")
    _doc_vectors = _vectorizer.fit_transform(corpus)


def retrieve_technique(alert: dict, top_k: int = 2) -> list[dict]:
    """
    Given a triaged alert (needs attack_type + signature), retrieve the
    most relevant MITRE technique(s) by TF-IDF cosine similarity.
    """
    _ensure_indexed()
    query = f"{alert.get('attack_type', '')} {alert.get('signature', '')}"
    query_vec = _vectorizer.transform([query])

    similarities = cosine_similarity(query_vec, _doc_vectors)[0]
    ranked_idx = similarities.argsort()[::-1][:top_k]

    techniques = [MITRE_TECHNIQUES[i] for i in ranked_idx if similarities[i] > 0]

    if not techniques:
        techniques = get_techniques_for_attack_type(alert.get("attack_type", ""))[:top_k]

    return techniques
