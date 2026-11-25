import json

def build():
    from sklearn.pipeline import Pipeline, FeatureUnion
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    feats = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, sublinear_tf=True, max_features=60000)),
    ])
    return Pipeline([("tfidf", feats), ("lr", LogisticRegression(C=4.0, class_weight="balanced", max_iter=2000))])

def save(model, path, meta):
    import joblib
    joblib.dump(model, path); json.dump(meta, open(path + ".json", "w"), indent=2)

def load(path):
    """.json -> pure-Python LiteModel (no sklearn needed, for phones); otherwise sklearn joblib."""
    if path.endswith(".json"):
        from .lite import LiteModel
        return LiteModel.load(path)
    import joblib
    return joblib.load(path)

def prob(model, text):
    if hasattr(model, "prob"):
        return model.prob(text)
    return float(model.predict_proba([text])[0, 1])
