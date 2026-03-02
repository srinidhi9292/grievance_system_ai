"""
AI Engine for Smart Grievance Management System
- Text Classification (TF-IDF + Logistic Regression)
- Sentiment Analysis (Rule-based)
- Priority Scoring
- Duplicate Detection (Cosine Similarity)
- SLA Prediction
"""

import os
import re
import math
import pickle
import random
from pathlib import Path
from datetime import date, timedelta
from collections import Counter

# ─── Training Data ────────────────────────────────────────────────────────────

TRAINING_DATA = [
    # Road
    ("The road is full of potholes and very dangerous for vehicles", "road"),
    ("Broken road needs immediate repair near the market", "road"),
    ("Speed breaker damaged, causing accidents on highway", "road"),
    ("Street is flooded due to road damage after rain", "road"),
    ("Road construction incomplete blocking traffic for months", "road"),
    ("Large pothole on main street caused my vehicle damage", "road"),
    ("Bridge needs urgent repair, cracks visible in structure", "road"),
    ("Divider broken on national highway causing accidents", "road"),

    # Water
    ("No water supply for the past three days in our area", "water"),
    ("Water pipeline burst flooding the entire street", "water"),
    ("Dirty contaminated water coming from taps", "water"),
    ("Low water pressure in apartment building", "water"),
    ("Water leakage from main pipeline wasting resources", "water"),
    ("Borewell not working, residents facing severe water shortage", "water"),
    ("Water tank not cleaned for months, unhygienic conditions", "water"),

    # Drainage
    ("Drainage system blocked causing sewage overflow on streets", "drainage"),
    ("Open manhole is dangerous, child nearly fell in it", "drainage"),
    ("Sewage water mixing with drinking water supply", "drainage"),
    ("Storm drain clogged causing flooding during rain", "drainage"),
    ("Septic tank overflow affecting nearby houses", "drainage"),
    ("Drainage pipe broken, sewage smell causing health issues", "drainage"),

    # Electricity
    ("Power outage for 12 hours, no response from electricity board", "electricity"),
    ("Electric pole fallen on road, very dangerous situation", "electricity"),
    ("Street lights not working in entire colony", "electricity"),
    ("Transformer blown, entire sector without electricity", "electricity"),
    ("Loose wires hanging from pole, risk of electrocution", "electricity"),
    ("Frequent power cuts affecting businesses and residents", "electricity"),
    ("High voltage fluctuation damaging household appliances", "electricity"),

    # Garbage
    ("Garbage not collected for over a week, health hazard", "garbage"),
    ("Illegal garbage dumping near residential area", "garbage"),
    ("Waste bins overflowing with no collection in sight", "garbage"),
    ("Garbage burning causing severe air pollution in locality", "garbage"),
    ("Dead animals not removed creating unhygienic conditions", "garbage"),
    ("Compost facility not working, waste piling up", "garbage"),

    # Parks
    ("Park benches broken, children getting injured", "parks"),
    ("Public park lights not working, unsafe at night", "parks"),
    ("Garden maintenance not done, weeds overgrown everywhere", "parks"),
    ("Playground equipment damaged in children's park", "parks"),
    ("Park encroached by unauthorized vendors", "parks"),

    # Noise
    ("Construction noise 24 hours violating noise pollution norms", "noise"),
    ("Illegal loudspeakers causing noise pollution at night", "noise"),
    ("Factory noise exceeding permissible limits in residential area", "noise"),
    ("Bar playing loud music past midnight disturbing residents", "noise"),

    # Building
    ("Unauthorized construction blocking access to property", "building"),
    ("Building collapse risk, cracks visible in old structure", "building"),
    ("Encroachment on public land by builder", "building"),
    ("Construction debris blocking public road for months", "building"),

    # Traffic
    ("Traffic signal not working causing major jams", "traffic"),
    ("Illegal parking blocking emergency vehicle access", "traffic"),
    ("No traffic police at busy intersection causing chaos", "traffic"),
    ("Road divider missing causing head-on collision risk", "traffic"),

    # Other
    ("Stray dogs attacking residents in the area", "other"),
    ("Public toilet in poor condition not cleaned regularly", "other"),
    ("Encroachment on footpath by hawkers", "other"),
]

CATEGORIES = ['road', 'water', 'drainage', 'electricity', 'garbage', 'parks', 'noise', 'building', 'traffic', 'other']

# ─── Minimal TF-IDF Implementation ────────────────────────────────────────────

class SimpleTFIDF:
    def __init__(self):
        self.vocab = {}
        self.idf = {}
        self.fitted = False

    def _tokenize(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        tokens = text.split()
        stop_words = {'the', 'a', 'an', 'is', 'in', 'on', 'at', 'for', 'of', 'and',
                      'or', 'to', 'with', 'from', 'by', 'not', 'are', 'was', 'were',
                      'be', 'been', 'have', 'has', 'had', 'this', 'that', 'it', 'its',
                      'no', 'my', 'our', 'very', 'i', 'we', 'they', 'he', 'she'}
        return [t for t in tokens if t not in stop_words and len(t) > 2]

    def fit_transform(self, texts):
        # Build vocab
        all_tokens = []
        tokenized = [self._tokenize(t) for t in texts]
        for tokens in tokenized:
            all_tokens.extend(tokens)

        freq = Counter(all_tokens)
        self.vocab = {word: i for i, (word, _) in enumerate(freq.most_common(500))}

        # Compute IDF
        n_docs = len(texts)
        doc_freq = Counter()
        for tokens in tokenized:
            for word in set(tokens):
                if word in self.vocab:
                    doc_freq[word] += 1

        self.idf = {word: math.log((n_docs + 1) / (doc_freq.get(word, 0) + 1)) + 1
                    for word in self.vocab}
        self.fitted = True

        return self._texts_to_matrix(tokenized)

    def transform(self, texts):
        tokenized = [self._tokenize(t) for t in texts]
        return self._texts_to_matrix(tokenized)

    def _texts_to_matrix(self, tokenized):
        matrix = []
        for tokens in tokenized:
            vec = [0.0] * len(self.vocab)
            token_count = Counter(tokens)
            n_tokens = max(len(tokens), 1)
            for word, count in token_count.items():
                if word in self.vocab:
                    tf = count / n_tokens
                    idf = self.idf.get(word, 1.0)
                    vec[self.vocab[word]] = tf * idf
            # L2 normalize
            norm = math.sqrt(sum(v ** 2 for v in vec)) or 1.0
            vec = [v / norm for v in vec]
            matrix.append(vec)
        return matrix


class SimpleLogisticRegression:
    def __init__(self, n_iter=200, lr=0.1):
        self.n_iter = n_iter
        self.lr = lr
        self.weights = {}
        self.classes = []
        self.fitted = False

    def _softmax(self, scores):
        exp_scores = [math.exp(min(s, 500)) for s in scores]
        total = sum(exp_scores) or 1e-10
        return [e / total for e in exp_scores]

    def fit(self, X, y):
        self.classes = list(set(y))
        n_features = len(X[0])
        self.weights = {c: [0.0] * n_features for c in self.classes}
        self.bias = {c: 0.0 for c in self.classes}

        for _ in range(self.n_iter):
            for xi, yi in zip(X, y):
                scores = [sum(xi[j] * self.weights[c][j] for j in range(n_features)) + self.bias[c]
                          for c in self.classes]
                probs = self._softmax(scores)

                for k, c in enumerate(self.classes):
                    grad = probs[k] - (1.0 if c == yi else 0.0)
                    self.bias[c] -= self.lr * grad
                    for j in range(n_features):
                        self.weights[c][j] -= self.lr * grad * xi[j]

        self.fitted = True

    def predict(self, X):
        predictions = []
        for xi in X:
            scores = [sum(xi[j] * self.weights[c][j] for j in range(len(xi))) + self.bias[c]
                      for c in self.classes]
            predictions.append(self.classes[scores.index(max(scores))])
        return predictions

    def predict_proba(self, X):
        results = []
        for xi in X:
            scores = [sum(xi[j] * self.weights[c][j] for j in range(len(xi))) + self.bias[c]
                      for c in self.classes]
            probs = self._softmax(scores)
            results.append({c: p for c, p in zip(self.classes, probs)})
        return results


# ─── Sentiment Analyzer ───────────────────────────────────────────────────────

POSITIVE_WORDS = {'good', 'great', 'excellent', 'amazing', 'fixed', 'resolved', 'clean',
                  'working', 'appreciate', 'thank', 'better', 'improved', 'nice'}

NEGATIVE_WORDS = {'bad', 'dangerous', 'urgent', 'broken', 'damaged', 'blocked', 'flooded',
                  'contaminated', 'illegal', 'hazardous', 'worst', 'terrible', 'horrible',
                  'awful', 'pathetic', 'disgusting', 'overflow', 'collapsed', 'deadly',
                  'accident', 'injury', 'killed', 'dying', 'severe', 'critical', 'emergency',
                  'immediate', 'months', 'years', 'never', 'nobody', 'ignored', 'neglected',
                  'poor', 'dirty', 'unhygienic', 'suffering', 'problem', 'issue', 'complaint'}

INTENSIFIERS = {'very', 'extremely', 'highly', 'severely', 'absolutely', 'completely',
                'totally', 'utterly', 'quite', 'really', 'so', 'too'}


def analyze_sentiment(text):
    tokens = text.lower().split()
    score = 0.0
    intensifier = 1.0

    for i, token in enumerate(tokens):
        clean = re.sub(r'[^a-z]', '', token)
        if clean in INTENSIFIERS:
            intensifier = 1.5
            continue
        if clean in NEGATIVE_WORDS:
            score -= 1.0 * intensifier
        elif clean in POSITIVE_WORDS:
            score += 1.0 * intensifier
        intensifier = 1.0

    # Normalize to -1 to 1
    word_count = max(len(tokens), 1)
    normalized = max(-1.0, min(1.0, score / (word_count ** 0.5)))

    if normalized >= 0.1:
        label = 'positive'
    elif normalized <= -0.1:
        label = 'negative'
    else:
        label = 'neutral'

    return round(normalized, 3), label


# ─── Priority Scoring ─────────────────────────────────────────────────────────

URGENT_KEYWORDS = {'urgent', 'immediate', 'emergency', 'critical', 'dangerous', 'accident',
                   'injury', 'collapse', 'death', 'hospital', 'fire', 'electrocution',
                   'explosion', 'flood', 'drowning', 'attack'}

HIGH_RISK_KEYWORDS = {'weeks', 'months', 'years', 'no response', 'ignored', 'neglected',
                      'contaminated', 'sewage', 'overflow', 'broken', 'damaged'}

CATEGORY_BASE_PRIORITY = {
    'electricity': 70,
    'water': 65,
    'drainage': 60,
    'road': 55,
    'garbage': 50,
    'traffic': 50,
    'building': 45,
    'noise': 35,
    'parks': 30,
    'other': 40,
}


def calculate_priority(text, category, sentiment_score):
    text_lower = text.lower()
    tokens = set(text_lower.split())

    base = CATEGORY_BASE_PRIORITY.get(category, 40)

    # Keyword boosts
    urgent_boost = sum(10 for kw in URGENT_KEYWORDS if kw in text_lower)
    risk_boost = sum(5 for kw in HIGH_RISK_KEYWORDS if kw in text_lower)

    # Sentiment boost (negative = higher priority)
    sentiment_boost = max(0, int(-sentiment_score * 20))

    # Text length (longer = more detailed = slightly higher priority)
    length_boost = min(5, len(text) // 100)

    score = base + min(30, urgent_boost) + min(15, risk_boost) + sentiment_boost + length_boost
    score = max(5, min(100, score))

    if score >= 80:
        level = 'critical'
    elif score >= 60:
        level = 'high'
    elif score >= 40:
        level = 'medium'
    else:
        level = 'low'

    return score, level


# ─── SLA Prediction ───────────────────────────────────────────────────────────

SLA_DAYS = {
    'critical': {'electricity': 1, 'water': 1, 'drainage': 2, 'road': 3, 'garbage': 2,
                 'traffic': 1, 'building': 3, 'noise': 2, 'parks': 5, 'other': 3},
    'high':     {'electricity': 3, 'water': 3, 'drainage': 4, 'road': 7, 'garbage': 3,
                 'traffic': 3, 'building': 7, 'noise': 4, 'parks': 7, 'other': 5},
    'medium':   {'electricity': 7, 'water': 7, 'drainage': 10, 'road': 14, 'garbage': 7,
                 'traffic': 7, 'building': 14, 'noise': 7, 'parks': 14, 'other': 10},
    'low':      {'electricity': 14, 'water': 10, 'drainage': 14, 'road': 21, 'garbage': 14,
                 'traffic': 14, 'building': 21, 'noise': 14, 'parks': 21, 'other': 21},
}


def predict_resolution_time(category, priority_level):
    days = SLA_DAYS.get(priority_level, SLA_DAYS['medium']).get(category, 10)
    expected_date = date.today() + timedelta(days=days)
    return days, expected_date


# ─── Duplicate Detection ──────────────────────────────────────────────────────

def cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a ** 2 for a in vec1))
    norm2 = math.sqrt(sum(b ** 2 for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def check_duplicates(new_complaint_text, existing_complaints, tfidf_model, threshold=0.75):
    if not existing_complaints:
        return None, 0.0

    all_texts = [c.title + ' ' + c.description for c in existing_complaints]
    all_texts.append(new_complaint_text)

    try:
        vectors = tfidf_model.transform(all_texts)
        new_vec = vectors[-1]
        existing_vectors = vectors[:-1]

        max_sim = 0.0
        master = None

        for i, (vec, complaint) in enumerate(zip(existing_vectors, existing_complaints)):
            sim = cosine_similarity(new_vec, vec)
            if sim > max_sim:
                max_sim = sim
                master = complaint

        if max_sim >= threshold:
            return master, max_sim

    except Exception:
        pass

    return None, 0.0


# ─── AI Engine Class ──────────────────────────────────────────────────────────

class GrievanceAIEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.tfidf = SimpleTFIDF()
        self.classifier = SimpleLogisticRegression(n_iter=300, lr=0.05)
        self._train()
        self._initialized = True

    def _train(self):
        texts = [d[0] for d in TRAINING_DATA]
        labels = [d[1] for d in TRAINING_DATA]
        X = self.tfidf.fit_transform(texts)
        self.classifier.fit(X, labels)

    def process_complaint(self, title, description, existing_complaints=None):
        full_text = f"{title} {description}"

        # 1. Classify
        X = self.tfidf.transform([full_text])
        category = self.classifier.predict(X)[0]
        proba = self.classifier.predict_proba(X)[0]
        confidence = max(proba.values())

        # 2. Sentiment
        sentiment_score, sentiment_label = analyze_sentiment(full_text)

        # 3. Priority
        priority_score, priority_level = calculate_priority(full_text, category, sentiment_score)

        # 4. SLA
        est_days, expected_date = predict_resolution_time(category, priority_level)

        # 5. Duplicate detection
        is_duplicate = False
        master_complaint = None
        similarity_score = 0.0

        if existing_complaints:
            master_complaint, similarity_score = check_duplicates(
                full_text, existing_complaints, self.tfidf
            )
            if master_complaint:
                is_duplicate = True

        return {
            'category': category,
            'confidence': round(confidence, 3),
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'priority_score': priority_score,
            'priority_level': priority_level,
            'estimated_resolution_days': est_days,
            'expected_resolution_date': expected_date,
            'is_duplicate': is_duplicate,
            'master_complaint': master_complaint,
            'similarity_score': round(similarity_score, 3),
        }


# Singleton instance
ai_engine = GrievanceAIEngine()
