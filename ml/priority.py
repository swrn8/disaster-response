class PriorityCalculator:

    # ========================================================
    # CALCULATE EMERGENCY PRIORITY
    # ========================================================

    def calculate(
        self,
        severity,
        disaster_type,
        description="",
        evidence_available=False,
        location_available=False
    ):

        score = 0

        description = description.lower().strip()


        # ====================================================
        # 1. SEVERITY SCORE
        # ====================================================

        if severity == "High":

            score += 60

        elif severity == "Medium":

            score += 40

        else:

            score += 20


        # ====================================================
        # 2. DISASTER TYPE SCORE
        # ====================================================

        disaster_scores = {

            "Earthquake": 20,

            "Flood": 20,

            "Fire": 20,

            "Cyclone": 20

        }


        score += disaster_scores.get(
            disaster_type,
            10
        )


        # ====================================================
        # 3. EMERGENCY KEYWORD SCORE
        # ====================================================

        critical_keywords = [

            "death",
            "dead",
            "trapped",
            "injured",
            "collapsed",
            "collapse",
            "destroyed",
            "critical",
            "urgent",
            "rescue",
            "people trapped",
            "people injured",
            "life threatening"

        ]


        keyword_matches = 0


        for keyword in critical_keywords:

            if keyword in description:

                keyword_matches += 1


        # Maximum keyword contribution = 15

        keyword_score = min(
            keyword_matches * 5,
            15
        )


        score += keyword_score


        # ====================================================
        # 4. EVIDENCE SCORE
        # ====================================================

        if evidence_available:

            score += 5


        # ====================================================
        # 5. LOCATION SCORE
        # ====================================================

        if location_available:

            score += 5


        # ====================================================
        # 6. LIMIT SCORE TO 100
        # ====================================================

        score = min(
            score,
            100
        )


        # ====================================================
        # 7. CONVERT SCORE TO PRIORITY
        # ====================================================

        if score >= 80:

            priority = "Critical"

        elif score >= 60:

            priority = "High"

        elif score >= 40:

            priority = "Medium"

        else:

            priority = "Low"


        return priority, score