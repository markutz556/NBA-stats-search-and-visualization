# Final project: NBA stats search and visualization

For SI 507, Winter 2018

## Data source
 * NBA teams on espn website ([NBA team on ESPN](http://www.espn.com/nba/teams)) 
 * A specified NBA team (e.g. [Boston Celtics](http://www.espn.com/nba/team/stats/_/name/bos/boston-celtics)) 
 * A specified player (e.g. [Kyrie Irving](http://www.espn.com/nba/player/stats/_/id/6442/kyrie-irving))
 * Google Place API (searching the locations of NBA team arenas)
   <br>API key needed (e.g. in secrets.py with format: google_place_key="xxxxxxxxxxxxxxxxx")</br>
   [Getting your Google Place API key](https://developers.google.com/places/web-service/get-api-key)

## Plotly
 * This program integrated plotly with Python. ([Getting started with plotly for Python](https://plot.ly/python/getting-started/))
   <br>Plotly API key needed ([Getting your plotly API key](https://plot.ly/api/))
   
## Code structure
1. Team info
   * get_all_team(): get the names, arena locations, webpage url for all the NBA teams
   * plot_all_team(): plot the locations of all NBA team arenas in US map
2. Route info
   * get_team_route(team): get previous 5 games results for a specified team
   * plot_game_route(team): plot the game route for a specified team in US map 
3. Player info
   * get_players(team): get players for a specified team.
   * get_points(player): get points of a specified player in previous 5 games
   * get_preteam(player): get teams a specified player've ever played for
   * plot_point(point): generate a dot plot for points of a player in past 5 games
   * plot_team_played(team): plot the locations of teams a player've ever played for
4. Class definitions
   * nbaTeam: class for NBA teams (parameters: team_name, arena_lat, arena_lng)
   * nbaPlayer: class for NBA players (parameters: player_name, webpage_url)
5. Dictionary & list
   * team_name: a dict for the conversion from NBA team name abbreviation to full name
   * playoff: a list of NBA teams (full name) that enter playoff

## Program usage
   1. run: python final_project.py
   2. prompt 
