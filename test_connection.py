from espn_api.hockey import League
import config  # This imports your variables from the other file

print("Attempting to connect to ESPN...")


try:
    # Initialize the League Object
    league = League(
        league_id=config.LEAGUE_ID,
        year=config.YEAR,
        espn_s2=config.ESPN_S2,
        swid=config.SWID
    )

    # If we get here, it worked!
    print("------------------------------------------------")
    print("✅ SUCCESS! Connected to League:") 
    print(f"Name: {league.settings.name}")
    print(f"Members: {len(league.members)}")
    print("------------------------------------------------")

    # Show my team
    # Note: This grabs the first team in the list. 
    # Later we will find *your* specific team.
    team = league.teams[0]
    print(f"Sample Team: {team.team_name}")
    print(f"Record: {team.wins}-{team.losses}-{team.ties}")

except Exception as e:
    print("------------------------------------------------")
    print("❌ FAILED TO CONNECT")
    print(f"Error: {e}")
    print("------------------------------------------------")
    print("Double check your SWID and ESPN_S2 in config.py")

    print(f"League ID Type: {type(config.LEAGUE_ID)}") # Should say <class 'int'>
    print(f"SWID Length: {len(config.SWID)}")          # Should be around 38 characters
    print(f"S2 Length: {len(config.ESPN_S2)}")         # Should be very long (approx 200-400 chars)