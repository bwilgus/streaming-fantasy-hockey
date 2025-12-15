import streamlit as st
import pandas as pd
from espn_api.hockey import League
import config
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---

# Roster Limits
LIMITS = {
    'F': 9, 'D': 5, 'G': 2,
    'Bench': 5, 'IR': 2,
    'Max_Goalies_On_Team': 4
}

# Skater Scoring
SCORING_SKATER = {
    'G': 2, 'A': 1, 'PPP': 0.5, 'SHP': 1,
    'HAT': 3, 'SOG': 0.1, 'HIT': 0.2, 'BLK': 0.5
}

# Goalie Scoring
SCORING_GOALIE = {
    'W': 1, 'GA': -0.3, 'SV': 0.1,
    'SO': 3, 'OTL': 0.5
}

# Schedule Weights (1.0 = Streamer Friendly)
DAY_WEIGHTS = {
    'Mon': 1.0, 'Tue': 0.1, 'Wed': 0.8, 
    'Thu': 0.1, 'Fri': 0.8, 'Sat': 0.0, 'Sun': 0.9
}

# --- 2. HELPER FUNCTIONS ---

def get_player_stats(player):
    """Safely extracts stats, preferring 2026 but falling back to 2025."""
    if 'Total 2026' in player.stats and player.stats['Total 2026']['total']:
        return player.stats['Total 2026']['total']
    elif 'Total 2025' in player.stats and player.stats['Total 2025']['total']:
        return player.stats['Total 2025']['total']
    return {}

def calculate_fantasy_points(player):
    """Calculates points based on position specific scoring."""
    stats = get_player_stats(player)
    total_points = 0.0
    
    rules = SCORING_GOALIE if player.position == 'G' else SCORING_SKATER
        
    for category, weight in rules.items():
        value = stats.get(category, 0)
        total_points += value * weight
        
    return round(total_points, 1)

def get_avg_points(player):
    """Derives Average Points Per Game manually."""
    stats = get_player_stats(player)
    total_pts = calculate_fantasy_points(player)
    games_played = stats.get('GP', 0)
    
    if games_played > 0:
        return round(total_pts / games_played, 2)
    return 0.0

def get_stream_score(player):
    """Calculates Stream Score: Avg Points * Opportunity Factor."""
    avg_pts = get_avg_points(player)
    avg_week_weight = sum(DAY_WEIGHTS.values()) / 7
    return round(avg_pts * avg_week_weight * 3, 2)

# --- 3. MAIN APP ---
st.set_page_config(page_title="Fantasy War Room", layout="wide")

try:
    # Connect to ESPN
    league = League(league_id=config.LEAGUE_ID, year=config.YEAR, espn_s2=config.ESPN_S2, swid=config.SWID)
    my_team = league.teams[7] 

    st.title(f"🏒 {my_team.team_name} War Room")
    
    # Check Goalie Limits
    goalie_count = len([p for p in my_team.roster if p.position == 'G'])
    st.caption(f"Roster: {len(my_team.roster)} Players | Goalies: {goalie_count}/{LIMITS['Max_Goalies_On_Team']}")
    
    if goalie_count >= LIMITS['Max_Goalies_On_Team']:
        st.warning(f"⚠️ Max goalies reached ({goalie_count}).")

    # CREATE TABS HERE (Must happen before 'with tab1:')
    tab1, tab2, tab3 = st.tabs(["📊 Roster Analysis", "🚀 Stream Targets (Skaters)", "🥅 Stream Targets (Goalies)"])

    # --- TAB 1: ROSTER ---
    with tab1:
        st.write("**My Team Performance**")
        roster_data = []
        for p in my_team.roster:
            avg = get_avg_points(p)
            total = calculate_fantasy_points(p)
            
            # FIX: Use getattr to handle missing ownership data
            own_pct = getattr(p, 'percent_owned', 'N/A')
            
            roster_data.append({
                "Player": p.name,
                "Pos": p.position,
                "Avg Pts": avg,
                "Total Pts": total,
                "GP": int(get_player_stats(p).get('GP', 0)),
                "% Own": own_pct
            })
        
        df_roster = pd.DataFrame(roster_data)
        st.dataframe(
            df_roster.sort_values(by="Avg Pts", ascending=True)
            .style.background_gradient(subset=['Avg Pts'], cmap="RdYlGn"),
            use_container_width=True
        )

    # --- TAB 2: SKATER STREAMERS ---
    with tab2:
        st.write("**Top Available Forwards & Defensemen**")
        free_agents = league.free_agents(size=40)
        fa_data = []
        
        for p in free_agents:
            if p.position != 'G':
                avg = get_avg_points(p)
                if avg > 1.5: 
                    score = get_stream_score(p)
                    fa_data.append({
                        "Player": p.name,
                        "Team": p.proTeam,
                        "Pos": p.position,
                        "Avg Pts": avg,
                        "Stream Score": score
                    })
        
        df_fa = pd.DataFrame(fa_data)
        if not df_fa.empty:
            st.dataframe(df_fa.sort_values(by="Stream Score", ascending=False).head(15), use_container_width=True)
        else:
            st.info("No skaters found.")

    # --- TAB 3: GOALIE STREAMERS ---
    with tab3:
        st.write("**Top Available Goalies**")
        if goalie_count >= LIMITS['Max_Goalies_On_Team']:
            st.error("⛔ Max goalies reached. Drop one first.")
        else:
            fa_data_g = []
            for p in free_agents:
                if p.position == 'G':
                    avg = get_avg_points(p)
                    if avg > 0:
                        score = get_stream_score(p)
                        fa_data_g.append({
                            "Player": p.name,
                            "Team": p.proTeam,
                            "Avg Pts": avg,
                            "Stream Score": score
                        })
            
            df_fa_g = pd.DataFrame(fa_data_g)
            if not df_fa_g.empty:
                st.dataframe(df_fa_g.sort_values(by="Stream Score", ascending=False), use_container_width=True)
            else:
                st.info("No goalies found.")

except Exception as e:
    st.error(f"Something went wrong: {e}")
    st.write(e)