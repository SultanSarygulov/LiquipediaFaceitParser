import requests
from datetime import datetime, timedelta, timezone
from models import Map, Team
from config import get_faceit_api_key

MAP_NAMES ={
    'de_mirage': 'Mirage',
    'de_train': 'Train',
    'de_overpass': 'Overpass',
    'de_anubis': 'Anubis',
    'de_dust2': 'Dust II',
    'de_ancient': 'Ancient',
    'de_inferno': 'Inferno',
    'de_vertigo': 'Vertigo',
    'de_nuke': 'Nuke'
}
TIMEZONES = {
    'ALMT': 5,
    'AQTT': 5,
    'UZT': 5,
    'TJT': 5,
    'KGT': 6,
    'MSK': 3,
    'CET': 1,
    'CEST': 2,
    'EEST': 3,
    'EET': 2,
}
API_KEY = get_faceit_api_key()
HEADERS = {'Authorization': f'Bearer {API_KEY}'}


def format_match_datetime(timestamp: str, timezone_abbr) -> str:

    '''Convert Unix timestamp into formatted string

    Example:
        format_match_datetime(1764508347, ALMT)
        -> November 30, 2025 - 18:12 {{Abbr/ALMT}}
    '''

    tz = timezone(timedelta(hours=TIMEZONES[timezone_abbr]))
    dt = datetime.fromtimestamp(timestamp=timestamp, tz=tz)
    return f'{dt.strftime('%B')} {dt.day}, {dt.year} - {dt.strftime('%H:%M')} {{{{Abbr/{timezone_abbr}}}}}'

def get_team_stats(map_stats: dict, faction_id: str) -> dict:

    '''Get match stats for a speific team'''
    
    for team in map_stats['teams']:
        if team["team_id"] == faction_id:
            return team
    raise ValueError(f"Team stats not found for faction_id={faction_id}")

def build_map(map_stats: str, voted_map: str, team1_sides: list, team1:str, team2) -> str:

    '''Build map code

    Example:
        |map1={{Map|map=Dust II|finished=true
        |t1firstside=t|t1t=7|t1ct=6|t2t=1|t2ct=5}}

        or (if map skipped)

        |map3={{Map|map=Ancient|finished=skip}}
    '''
    
    if map_stats is None:
        return f"    |map3={{{{Map|map={voted_map}|finished=skip}}}}"

    team1_stats = get_team_stats(map_stats=map_stats, faction_id=team1)['team_stats']
    team2_stats = get_team_stats(map_stats=map_stats, faction_id=team2)['team_stats']

    number=int(map_stats['played'])

    map = Map(
        id=map_stats['played'],
        name=voted_map,
        team1_side=team1_sides[number-1],
        team1_first_half=team1_stats['First Half Score'],
        team1_second_half=team1_stats['Second Half Score'],
        team2_first_half=team2_stats['First Half Score'],
        team2_second_half=team2_stats['Second Half Score']
    )

    if map.team1_side == "t":
        t1_t    = map.team1_first_half
        t1_ct   = map.team1_second_half
        t2_ct   = map.team2_first_half
        t2_t    = map.team2_second_half
    elif map.team1_side == "ct":
        t1_ct   = map.team1_first_half
        t1_t    = map.team1_second_half
        t2_t    = map.team2_first_half
        t2_ct   = map.team2_second_half
    else:
        raise ValueError("team1_side must be either 't' or 'ct'")

    return (
        f"    |map{map.id}={{{{Map|map={map.name}|finished=true\n"
        f"        |t1firstside={map.team1_side}|t1t={t1_t}|t1ct={t1_ct}|t2t={t2_t}|t2ct={t2_ct}}}}}"
    )

def get_match_info(match_id: str):

    if (len(match_id) != 38):
        raise ValueError('Input valid Faceit match id')

    match_url = f'https://open.faceit.com/data/v4/matches/{match_id}'
    match_stats_url = f'https://open.faceit.com/data/v4/matches/{match_id}/stats'

    match_json = requests.get(url=match_url, headers=HEADERS).json()
    match_stats_json = requests.get(url=match_stats_url, headers=HEADERS).json()
    team1 = match_json["teams"]["faction1"]["name"]
    team2 = match_json["teams"]["faction2"]["name"]

    return team1, team2, match_json, match_stats_json

def build_match(match_json, match_stats_json, team1_sides: list[str], tz_abbr: str, switch_teams ) -> str:

    formatted_datetime = format_match_datetime(match_json["started_at"], tz_abbr)

    team1 = Team(
        match_json["teams"]["faction1"]["faction_id"], 
        match_json["teams"]["faction1"]["name"]
    )
    team2 = Team(
        match_json["teams"]["faction2"]["faction_id"], 
        match_json["teams"]["faction2"]["name"]
    )
    
    if switch_teams == 'y':
        team1, team2 = team2, team1

    maps = []

    voted_maps =[MAP_NAMES[voted_map] for voted_map in match_json["voting"]["map"]["pick"]]
    for i, voted_map in enumerate(voted_maps):

        map_stats = match_stats_json["rounds"][i] if i < len(match_stats_json["rounds"]) else None
 
        maps.append(
            build_map(
                map_stats=map_stats, 
                voted_map=voted_map,
                team1_sides=team1_sides,
                team1=team1.id,
                team2=team2.id
            )
        )
        
    lines = [
        "{{Match",
        f"    |opponent1={{{{TeamOpponent|{team1.name.lower()}}}}}|opponent2={{{{TeamOpponent|{team2.name.lower()}}}}}",
        f"    |date={formatted_datetime}|finished=true",
        *maps,
        f"    |faceit={match_json['match_id']}",
        "    }}",
    ]

    return "\n".join(lines)


def main():

    '''First we receive match id, and get match info and stats from API
    To avoid teams switch, we show how it will be presented first, and 
    ask if you need to change it.
    If needed, you switch teams,
    Then we build the match code
    
    '''
    match_id =  input('match_id=')
    team1, team2, match_json, match_stats_json = get_match_info(match_id)
    print('team 1: ', team1, 'team 2: ',team2)
    switch_teams = input('switch_teams(y/n)=')
    team1_sides = input('team1_first_sides=')
    
    print(build_match(match_json, match_stats_json, team1_sides.split(), switch_teams=switch_teams, tz_abbr='UZT'))
    

if __name__ == "__main__":

    main()
    
