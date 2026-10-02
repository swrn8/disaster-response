class SeverityPredictor:

    def predict(self, text):

        text = text.lower()

        high_keywords = [
            "death",
            "dead",
            "trapped",
            "injured",
            "collapsed",
            "destroyed",
            "severe",
            "critical",
            "urgent"
        ]

        medium_keywords = [
            "damage",
            "flooded",
            "fire",
            "blocked",
            "danger",
            "heavy"
        ]

        if any(word in text for word in high_keywords):
            return "High"

        elif any(word in text for word in medium_keywords):
            return "Medium"

        else:
            return "Low"