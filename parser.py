import requests
from datetime import datetime, timedelta, timezone
from models import Map, Match, Team


map_names ={
    'de_mirage': 'Mirage',
    'de_train': 'Train',
    'de_overpass': 'Overpass',
    'de_anubis': 'Anubis',
    'de_dust2': 'Dust II',
    'de_ancient': 'Ancient',
    'de_inferno': 'Inferno',
    'de_vertigo': 'Vertgio',
    'de_nuke': 'Nuke'
}

API_KEY = your-api-key
HEADERS = {'Authorization': f'Bearer {API_KEY}'}


def format_match_datetime(timestamp, timezone_abbr) -> str:

    tz = timezone(timedelta(hours=5))
    dt = datetime.fromtimestamp(timestamp=timestamp, tz=tz)
    return f'{dt.strftime('%B')} {dt.day}, {dt.year} - {dt.strftime('%H:%M')} {{{{Abbr/{timezone_abbr}}}}}'

def main(match_id):

    match_url = f'https://open.faceit.com/data/v4/matches/{match_id}'
    match_stats_url = f'https://open.faceit.com/data/v4/matches/{match_id}/stats'
    match_json = requests.get(url=match_url, headers=HEADERS).json()
    match_stats = requests.get(url=match_stats_url, headers=HEADERS).json()

    formatted_datetime = format_match_datetime(match_json["started_at"], 'ALMT')

    team1 = Team(
        match_json["teams"]["faction1"]["faction_id"], 
        match_json["teams"]["faction1"]["name"]
    )
    team2 = Team(
        match_json["teams"]["faction2"]["faction_id"], 
        match_json["teams"]["faction2"]["name"]
    )

    maps = []
    for map_number in range(3):

        try:

            map_stats = match_stats['rounds'][map_number]

            team1_stats = get_team_stats(map_stats=map_stats, faction_id=team1.id)['team_stats']
            team2_stats = get_team_stats(map_stats=map_stats, faction_id=team2.id)['team_stats']

            map = Map(
                id=map_stats['played'],
                name=map_names[map_stats['round_stats']['Map']],
                team1_side='t',
                team1_first_half=team1_stats['First Half Score'],
                team1_second_half=team1_stats['Second Half Score'],
                team2_first_half=team2_stats['First Half Score'],
                team2_second_half=team2_stats['Second Half Score']
            )

            maps.append(build_map(map))

        except:
            maps.append(
                f"    |map{map_number+1}={{{{Map|map=Unknown|finished=skip}}}}"
                )

    
    lines = [
        "{{Match",
        f"    |opponent1={{{{TeamOpponent|{team1.name.lower()}}}}}|opponent2={{{{TeamOpponent|{team2.name.lower()}}}}}",
        f"    |date={formatted_datetime}|finished=true",
        *maps,
        f"    |faceit={match_id}",
        "    }}",
    ]

    return "\n".join(lines)


def get_name(faction_id, headers):
        team_json = requests.get(
            f'https://open.faceit.com/data/v4/teams/{faction_id}',
            headers=headers).json()
        
        return team_json["name"]


def build_map(map: Map):

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
    

def get_team_stats(map_stats: dict, faction_id: str) -> dict:

    
    for team in map_stats['teams']:
        if team["team_id"] == faction_id:
            return team
    raise ValueError(f"Team stats not found for faction_id={faction_id}")

    

if __name__ == "__main__":

    match_id = input('match_id=')
    
    print(main(match_id))
    
