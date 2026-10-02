from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


class DisasterClassifier:

    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()

        # Small starter dataset
        texts = [
            "heavy rain flooded the road",
            "water entered houses after rain",
            "river overflow caused flooding",

            "earthquake damaged buildings",
            "strong earthquake destroyed houses",
            "ground shaking damaged roads",

            "fire broke out in a building",
            "house caught fire",
            "large fire spreading",

            "cyclone damaged houses",
            "strong winds destroyed trees",
            "cyclone warning in the area"
        ]

        labels = [
            "Flood",
            "Flood",
            "Flood",

            "Earthquake",
            "Earthquake",
            "Earthquake",

            "Fire",
            "Fire",
            "Fire",

            "Cyclone",
            "Cyclone",
            "Cyclone"
        ]

        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)

    def predict(self, text):

        X = self.vectorizer.transform([text])

        return self.model.predict(X)[0]