from espn_api.hockey import League
import config
import pprint

# Connect
league = League(league_id=config.LEAGUE_ID, year=config.YEAR, espn_s2=config.ESPN_S2, swid=config.SWID)

# Get one player
team = league.teams[7]
player = team.roster[0]

print(f"--- Inspecting: {player.name} ---")

# Method 1: Print all available attributes (The "dir" command)
print("\nAll Attributes:")
print(dir(player))

# Method 2: Check the 'stats' dictionary specifically
# The API often hides the good stuff inside a 'stats' bucket
if hasattr(player, 'stats'):
    print("\nStats Dictionary:")
    pprint.pprint(player.stats)
else:
    print("\nNo 'stats' attribute found.")