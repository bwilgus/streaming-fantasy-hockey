from espn_api.hockey import League
import config
import pprint

# Connect
league = League(league_id=config.LEAGUE_ID, year=config.YEAR, espn_s2=config.ESPN_S2, swid=config.SWID)
my_team = league.teams[0] # Adjust index if needed
player = my_team.roster[7]

print(f"--- Inspecting: {player.name} ---")
#for p in my_team.roster:
#    print(p.lineupSlot)
pprint.pprint(player.__dict__)