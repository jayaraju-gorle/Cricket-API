<H2>Cricket API</H2>
This is a simple Flask web application that provides an API to retrieve Player Stats, Live Score, Fixtures, Tables and Results data of Cricket Matches ( ODI, T20, Test and IPL ) from Cricbuzz
<h2>API Endpoints</h2>

<p>The application provides the following API endpoints:</p>

<h3>GET /</h3>
<p>This is the home endpoint of the API. It returns a welcome message.</p>
<p>The API returns a simple string message: "Hey there! Welcome to the Cricket API"</p>

<h3>GET  /players/{player_name}</h3>
<p>This endpoint retrieves detailed statistics for a given cricket player. The player's name should be provided as part of the URL path. It fetches player information from Cricbuzz by using Google Search to find the player's Cricbuzz profile.</p>
<p>The API returns a JSON object containing player information, including batting and bowling career summaries across different formats (Test, ODI, T20I). It includes fields like Player Name, Country, Role, and detailed career stats.</p>
<pre><code>[
    {
        "Player Name": "Player Name",
        "Country": "Country",
        "Role": "Role",
        "Batting Career Summary 1": {
            "Mode1": "Test",
            "Matches": "Matches",
            "Runs": "Runs",
            "HS": "HS",
            "Avg": "Avg",
            "SR": "SR",
            "100s": "100s",
            "50s": "50s"
        },
        "Batting Career Summary2": {
            "Mode2": "ODI",
            "Matches": "Matches",
            "Runs": "Runs",
            "HS": "HS",
            "Avg": "Avg",
            "SR": "SR",
            "100s": "100s",
            "50s": "50s"
        },
        "Batting Career Summary3": {
            "Mode2": "T20I",
            "Matches": "Matches",
            "Runs": "Runs",
            "HS": "HS",
            "Avg": "Avg",
            "SR": "SR",
            "100s": "100s",
            "50s": "50s"
        }
    }
]</code></pre>

<h3>GET /schedule</h3>
<p>This endpoint provides a schedule of upcoming international cricket series. It fetches data from Cricbuzz and lists upcoming matches.</p>
<p>The API returns a JSON array where each element is a string describing an upcoming match.</p>
<pre><code>["India vs South Africa, 1st ODI","India vs South Africa, 2nd ODI","India vs South Africa, 3rd ODI",...]</code></pre>

<h3>GET /live</h3>
<p>This endpoint retrieves details of live cricket matches currently in progress. It fetches live score updates from Cricbuzz.</p>
<p>The API returns a JSON array where each element is a string describing a live match with scores and current over information.</p>
<pre><code>["Australia 45/1 (8.4 ov)","Bangladesh 136/4 (17.4 ov)","India 118/2 (13.3 ov)",...]</code></pre>

<h3>GET /ipl-schedule/{year}/{series_id}</h3>
    <p>This endpoint is designed to fetch the schedule for the Indian Premier League (IPL) for a specific year and series ID. It requires the year and series_id as URL parameters to dynamically generate the IPL schedule URL from Cricbuzz.</p>
    <p><b>Parameters:</b></p>
    <ul>
        <li><code>year</code>: The year for which the IPL schedule is requested (integer).</li>
        <li><code>series_id</code>: The series ID for the IPL season on Cricbuzz (integer).</li>
    </ul>
    <p>The API returns a JSON object containing the IPL schedule for the given year and series ID. The object includes the season year, series ID, and a list of matches with details such as date, teams, venue, time, and match status (upcoming, live, or completed).</p>
    <pre><code>
{
    "season": year,
    "series_id": series_id,
    "matches": [
        {
            "date": "Date of match",
            "match_number": "Match number in the series",
            "team1": "Team 1 name",
            "team2": "Team 2 name",
            "venue": "Venue of the match",
            "match_time": "Time of the match",
            "result": "Match result if completed",
            "status": "Match status (Upcoming, Live, Completed)",
            "is_live": false
        },
        ...
    ]
}
    </code></pre>

<h3>GET /all-series</h3>
    <p>This endpoint fetches a comprehensive list of all cricket series schedules available on Cricbuzz, categorized by type (e.g., International, T20 Leagues, Domestic, Women). It provides an overview of ongoing and upcoming series across different categories.</p>
    <p>The API returns a JSON array of series, with each series containing a category, series name, date range, and a list of matches within that series. Match details include match title, date & time, and venue.</p>
    <pre><code>
[
    {
        "category": "Series Category (e.g., International)",
        "series_name": "Name of the series",
        "date_range": "Date range of the series",
        "matches": [
            {
                "match_title": "Title of the match",
                "date_time": "Date and time of the match",
                "venue": "Venue of the match"
            },
            ...
        ]
    },
    ...
]
    </code></pre>
  
<h2>Live Score</h2>
<ul>
  <li>Live Score of all the Matches Going on present</li>
  <br> <img src="Cricket API/live_matches.jpg"> <br>
 </ul>
 <h2>Schedule</h2>
 <ul>
  <li>Schedule of the next Upcoming Matches</li>
  <br> <img src="Cricket API/schedule.jpg"> <br>
 </ul>
 
  <h2>Individual PLayer Stats</h2>
 <ul>
  <li>Example: Stats of Virat Kohli | You can use the common name of the Players as well to retrive the datails</li>
  <br> <img src="Cricket API/player_stats.jpg"> <br>
 </ul>
