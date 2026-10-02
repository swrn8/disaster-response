class RescueTeam:

    def __init__(
        self,
        team_id,
        name,
        team_type,
        location,
        capacity=5,
        available=True
    ):
        self.team_id = team_id
        self.name = name
        self.team_type = team_type
        self.location = location
        self.capacity = capacity
        self.available = available
        self.current_assignments = 0

    def is_available(self):
        return (
            self.available
            and self.current_assignments < self.capacity
        )

    def assign_report(self):
        if not self.is_available():
            return False

        self.current_assignments += 1
        return True

    def release_report(self):
        if self.current_assignments > 0:
            self.current_assignments -= 1

        return True

    def get_remaining_capacity(self):
        return max(
            self.capacity - self.current_assignments,
            0
        )

    def to_dict(self):
        return {
            "team_id": self.team_id,
            "name": self.name,
            "team_type": self.team_type,
            "location": self.location,
            "capacity": self.capacity,
            "available": self.available,
            "current_assignments": self.current_assignments,
            "remaining_capacity": self.get_remaining_capacity()
        }


class RescueTeamManager:

    def __init__(self):
        self.teams = []

    def add_team(self, team):
        self.teams.append(team)

    def get_all_teams(self):
        return self.teams

    def get_available_teams(self):
        return [
            team
            for team in self.teams
            if team.is_available()
        ]

    def find_teams_by_type(self, team_type):
        return [
            team
            for team in self.get_available_teams()
            if team.team_type.lower() == team_type.lower()
        ]

    def assign_report_to_team(self, team_id):
        for team in self.teams:
            if team.team_id == team_id:
                return team.assign_report()

        return False

    def release_report_from_team(self, team_id):
        for team in self.teams:
            if team.team_id == team_id:
                return team.release_report()

        return False

    def get_team(self, team_id):
        for team in self.teams:
            if team.team_id == team_id:
                return team

        return None

    def get_summary(self):
        total = len(self.teams)

        available = len(
            self.get_available_teams()
        )

        unavailable = total - available

        return {
            "total": total,
            "available": available,
            "unavailable": unavailable
        }