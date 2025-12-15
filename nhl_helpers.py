import requests
from datetime import datetime, timedelta

def get_weekly_schedule():
    """
    Fetches the next 7 days of NHL games and returns a dictionary
    mapping Team Abbreviations to the days they play.
    
    Returns:
        dict: { "PIT": ["Mon", "Thu", "Sat"], "NYR": ["Tue", "Fri"], ... }
    """
    # 1. Get today's date in YYYY-MM-DD format
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 2. Hit the API (This endpoint returns a full week of data starting from 'today')
    url = f"https://api-web.nhle.com/v1/schedule/{today_str}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # 3. Parse the complicated JSON into a simple map
        team_schedule = {}
        
        # The API returns a list called 'gameWeek' containing 7 days of data
        for day_info in data.get('gameWeek', []):
            date_obj = datetime.strptime(day_info['date'], "%Y-%m-%d")
            day_name = date_obj.strftime("%a") # e.g., "Mon", "Tue"
            
            for game in day_info.get('games', []):
                # Extract team abbreviations (e.g., "PIT", "WSH")
                away_team = game['awayTeam']['abbrev']
                home_team = game['homeTeam']['abbrev']
                
                # Add to our map
                if away_team not in team_schedule: team_schedule[away_team] = []
                if home_team not in team_schedule: team_schedule[home_team] = []
                
                team_schedule[away_team].append(day_name)
                team_schedule[home_team].append(day_name)
                
        return team_schedule

    except Exception as e:
        print(f"Error fetching NHL schedule: {e}")
        return {}