class ResponseQueue:

    PRIORITY_ORDER = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

    STATUS_ORDER = {
        "Pending": 1,
        "In Progress": 2,
        "Resolved": 3
    }

    def __init__(self, reports=None):
        self.reports = reports or []

    def set_reports(self, reports):
        """
        Update the reports used by the response queue.
        """
        self.reports = reports or []

    def calculate_queue_score(self, report):
        """
        Calculate a queue score for a report.

        Higher priority and higher priority_score
        will place the report earlier in the queue.
        """

        priority_score = getattr(
            report,
            "priority_score",
            0
        ) or 0

        priority = getattr(
            report,
            "priority",
            "Low"
        ) or "Low"

        status = getattr(
            report,
            "status",
            "Pending"
        ) or "Pending"

        priority_weight = self.PRIORITY_ORDER.get(
            priority,
            1
        )

        status_weight = self.STATUS_ORDER.get(
            status,
            1
        )

        # Reports that are still pending should
        # receive higher queue importance.
        pending_bonus = 20 if status == "Pending" else 0

        queue_score = (
            priority_weight * 100
            + priority_score
            + pending_bonus
        )

        return queue_score

    def build_queue(self, reports=None):
        """
        Build and return the emergency response queue.

        Critical/High priority reports are placed
        before lower-priority reports.
        """

        if reports is not None:
            self.reports = reports

        queue = []

        for report in self.reports:

            queue_score = self.calculate_queue_score(
                report
            )

            queue.append({
                "report": report,
                "queue_score": queue_score
            })

        queue.sort(
            key=lambda item: (
                item["queue_score"],
                getattr(
                    item["report"],
                    "id",
                    0
                ) or 0
            ),
            reverse=True
        )

        return queue

    def get_pending_queue(self, reports=None):
        """
        Return only reports that still require
        emergency response.
        """

        if reports is not None:
            self.reports = reports

        pending_reports = [
            report
            for report in self.reports
            if getattr(
                report,
                "status",
                "Pending"
            ) != "Resolved"
        ]

        return self.build_queue(
            pending_reports
        )

    def get_critical_reports(self, reports=None):
        """
        Return Critical and High priority reports.
        """

        if reports is not None:
            self.reports = reports

        critical_reports = [
            report
            for report in self.reports
            if getattr(
                report,
                "priority",
                "Low"
            ) in ["Critical", "High"]
            and getattr(
                report,
                "status",
                "Pending"
            ) != "Resolved"
        ]

        return self.build_queue(
            critical_reports
        )

    def get_next_report(self, reports=None):
        """
        Return the next report that should be handled.
        """

        queue = self.get_pending_queue(
            reports
        )

        if not queue:
            return None

        return queue[0]["report"]

    def get_queue_summary(self, reports=None):
        """
        Return summary information about
        the current emergency response queue.
        """

        if reports is not None:
            self.reports = reports

        queue = self.get_pending_queue()

        critical = 0
        high = 0
        medium = 0
        low = 0

        for item in queue:

            report = item["report"]

            priority = getattr(
                report,
                "priority",
                "Low"
            )

            if priority == "Critical":
                critical += 1
            elif priority == "High":
                high += 1
            elif priority == "Medium":
                medium += 1
            else:
                low += 1

        return {
            "total": len(queue),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        }