import requests

class Match():

    def __init__(self, id, started_at, timezone, team1, team2, maps):
        self.id = id
        self.started_at = started_at
        self.timezone = timezone
        self.team1 = team1
        self.team2 = team2

class Map():

    def __init__(self, id, name, team1_side, team1_first_half, team2_first_half, team1_second_half, team2_second_half):
        self.id = id
        self.name = name
        self.team1_side = team1_side
        self.team1_first_half = team1_first_half
        self.team2_first_half = team2_first_half
        self.team1_second_half = team1_second_half
        self.team2_second_half = team2_second_half

class Team():

    def __init__(self, id, name):
        self.id = id
        self.name = name

        
    


