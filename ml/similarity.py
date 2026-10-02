from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityChecker:

    # ========================================================
    # CHECK SIMILARITY BETWEEN NEW AND EXISTING REPORTS
    # ========================================================

    def check_similarity(
        self,
        new_description,
        existing_reports
    ):

        # ----------------------------------------------------
        # NO EXISTING REPORTS
        # ----------------------------------------------------

        if not existing_reports:

            return None, 0, "No Match"


        # ----------------------------------------------------
        # COLLECT EXISTING DESCRIPTIONS
        # ----------------------------------------------------

        descriptions = [

            report.description

            for report in existing_reports

        ]


        # Add the new report

        descriptions.append(
            new_description
        )


        # ----------------------------------------------------
        # TF-IDF VECTORIZATION
        # ----------------------------------------------------

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )


        vectors = vectorizer.fit_transform(
            descriptions
        )


        # ----------------------------------------------------
        # COSINE SIMILARITY
        # ----------------------------------------------------

        similarity_scores = cosine_similarity(

            vectors[-1],

            vectors[:-1]

        )[0]


        # ----------------------------------------------------
        # FIND HIGHEST SIMILARITY
        # ----------------------------------------------------

        highest_score = similarity_scores.max()


        highest_index = (
            similarity_scores.argmax()
        )


        similar_report = (
            existing_reports[highest_index]
        )


        # ----------------------------------------------------
        # CLASSIFY SIMILARITY
        # ----------------------------------------------------

        if highest_score >= 0.75:

            similarity_type = "Duplicate"

        elif highest_score >= 0.40:

            similarity_type = "Related"

        else:

            similarity_type = "No Match"


        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        return (
            similar_report,
            highest_score,
            similarity_type
        )