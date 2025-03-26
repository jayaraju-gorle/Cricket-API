<H2>Cricket API</H2>
<H2>Cricket API</H2>

**Disclaimer:** This is an unofficial API built by scraping content from Cricbuzz. It is not affiliated with or endorsed by Cricbuzz. The availability and accuracy of data depend on the structure of the Cricbuzz website, which may change over time.

This is a simple Flask web application that provides an API to retrieve Player Stats, Live Scores, Fixtures, and Results data of Cricket Matches (ODI, T20, Test, and IPL) from Cricbuzz.

<h2>API Endpoints</h2>

<p>The application provides the following API endpoints:</p>

<h3>GET /</h3>
<p>This is the home endpoint of the API. It returns a welcome message.</p>
<p>The API returns a simple string message: "Hey there! Welcome to the Cricket API"</p>

<h3>GET  /players/{player_name}</h3>
<p>This endpoint retrieves detailed statistics for a given cricket player. The player's name should be provided as part of the URL path. It fetches player information from Cricbuzz by using Google Search to find the player's Cricbuzz profile.</p>
<p>The API returns a JSON object containing player information, including batting and bowling career summaries across different formats (Test, ODI, T20I). It includes fields like Player Name, Country, Role, and detailed career stats.</p>
<pre><code>
[
    {
        "Player Name": "Virat Kohli",
        "Country": "India",
        "Role": "Top-order Batter",
        "Batting Career Summary 1": {
            "Mode1": "TEST",
            "Matches": "113",
            "Runs": "8848",
            "HS": "254*",
            "Avg": "49.15",
            "SR": "55.66",
            "100s": "29",
            "50s": "30"
        }
    },
    {
        "Batting Career Summary2": {
            "Mode2": "ODI",
            "Matches": "292",
            "Runs": "13794",
            "HS": "183",
            "Avg": "58.69",
            "SR": "93.62",
            "100s": "50",
            "50s": "72"
        }
    },
    {
        "Batting Career Summary3": {
            "Mode2": "T20I",
            "Matches": "117",
            "Runs": "4008",
            "HS": "122*",
            "Avg": "51.38",
            "SR": "137.96",
            "100s": "1",
            "50s": "37"
        }
    },
    {
        "Bowling Career Summary1": {
            "Mode3": "TEST",
            "Matches": "12",
            "Runs": "12",
            "Wickets": "0",
            "BBI": "0/0",
            "BBM": "0.00",
            "Econ": "3.00",
            "5W": "0"
        }
    },
    {
        "Bowling Career Summary2": {
            "Mode3": "ODI",
            "Matches": "10",
            "Runs": "10",
            "Wickets": "4",
            "BBI": "1/15",
            "BBM": "0.00",
            "Econ": "5.00",
            "5W": "0"
        }
    },
    {
        "Bowling Career Summary3": {
            "Mode3": "T20I",
            "Matches": "12",
            "Runs": "12",
            "Wickets": "0",
            "BBI": "0/0",
            "BBM": "0.00",
            "Econ": "12.00",
            "5W": "0"
        }
    }
]
</code></pre>

<h3>GET /schedule</h3>
<p>This endpoint provides a schedule of upcoming international cricket series. It fetches data from Cricbuzz and lists upcoming matches.</p>
<p>The API returns a JSON array where each element is a string describing an upcoming match.</p>
<pre><code>
[
    "India vs South Africa, 1st ODI",
    "India vs South Africa, 2nd ODI",
    "India vs South Africa, 3rd ODI",
    ...
]
</code></pre>

<h3>GET /live</h3>
<p>This endpoint retrieves details of live cricket matches currently in progress. It fetches live score updates from Cricbuzz.</p>
<p>The API returns a JSON array where each element is a string describing a live match with scores and current over information.</p>
<pre><code>
[
    "Australia 45/1 (8.4 ov)",
    "Bangladesh 136/4 (17.4 ov)",
    "India 118/2 (13.3 ov)",
    ...
]
</code></pre>

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
    "season": 2024,
    "series_id": 6762,
    "matches": [
        {
            "date": "Sat, Mar 23, 2024",
            "match_number": "Match 1",
            "team1": "Chennai Super Kings",
            "team2": "Royal Challengers Bangalore",
            "venue": "MA Chidambaram Stadium, Chennai",
            "match_time": "8:00 PM IST",
            "gmt_time": "2:30 PM GMT",
            "formatted_date_time": "2024-03-23T20:00:00+05:30",
            "result": null,
            "status": "Upcoming",
            "is_live": false,
            "match_link": "https://www.cricbuzz.com/cricket-match/6762/1/csk-vs-rcb-1st-match-indian-premier-league-2024"
        },
        {
            "date": "Sun, Mar 24, 2024",
            "match_number": "Match 2",
            "team1": "Punjab Kings",
            "team2": "Delhi Capitals",
            "venue": "Punjab Cricket Association IS Bindra Stadium, Mohali",
            "match_time": "3:30 PM IST",
            "gmt_time": "10:00 AM GMT",
            "formatted_date_time": "2024-03-24T15:30:00+05:30",
            "result": null,
            "status": "Upcoming",
            "is_live": false,
            "match_link": "https://www.cricbuzz.com/cricket-match/6762/2/pbks-vs-dc-2nd-match-indian-premier-league-2024"
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
        "category": "International",
        "series_name": "India tour of South Africa, 2023-24",
        "date_range": "Dec 10, 2023 - Jan 07, 2024",
        "matches": [
            {
                "match_title": "1st T20I: South Africa vs India",
                "date_time": "Dec 10, 2023",
                "venue": "Kingsmead, Durban"
            },
            {
                "match_title": "2nd T20I: South Africa vs India",
                "date_time": "Dec 12, 2023",
                "venue": "St George's Park, Gqeberha"
            },
            ...
        ]
    },
    {
        "category": "T20 Leagues",
        "series_name": "Indian Premier League, 2024",
        "date_range": "Mar 22, 2024 - May 26, 2024",
        "matches": [
            {
                "match_title": "Match 1: Chennai Super Kings vs Royal Challengers Bangalore",
                "date_time": "Mar 22, 2024",
                "venue": "MA Chidambaram Stadium, Chennai"
            },
            ...
        ]
    },
    ...
]
</code></pre>

<h2>Key Features</h2>
<ul>
    <li><b>Player Statistics:</b> Retrieve comprehensive batting and bowling stats for any player across Test, ODI, and T20I formats.</li>
    <li><b>Live Scores:</b> Get real-time updates on all ongoing cricket matches.</li>
    <li><b>Upcoming Schedule:</b> View the schedule for upcoming international cricket series.</li>
    <li><b>IPL Schedule:</b> Fetch the complete schedule for any IPL season by specifying the year and series ID.</li>
    <li><b>All Series Data:</b> Explore a categorized list of all cricket series, including international, T20 leagues, domestic, and women's matches.</li>
</ul>

**Disclaimer:** This is an unofficial API built by scraping content from Cricbuzz. It is not affiliated with or endorsed by Cricbuzz. The availability and accuracy of data depend on the structure of the Cricbuzz website, which may change over time.

This is a simple Flask web application that provides an API to retrieve Player Stats, Live Scores, Fixtures, and Results data of Cricket Matches (ODI, T20, Test, and IPL) from Cricbuzz.

<h2>API Endpoints</h2>

<p>The application provides the following API endpoints:</p>

<h3>GET /</h3>
<p>This is the home endpoint of the API. It returns a welcome message.</p>
<p>The API returns a simple string message: "Hey there! Welcome to the Cricket API"</p>

<h3>GET  /players/{player_name}</h3>
<p>This endpoint retrieves detailed statistics for a given cricket player. The player's name should be provided as part of the URL path. It fetches player information from Cricbuzz by using Google Search to find the player's Cricbuzz profile.</p>
<p>The API returns a JSON object containing player information, including batting and bowling career summaries across different formats (Test, ODI, T20I). It includes fields like Player Name, Country, Role, and detailed career stats.</p>
<pre><code>
[
    {
        "Player Name": "Virat Kohli",
        "Country": "India",
        "Role": "Top-order Batter",
        "Batting Career Summary 1": {
            "Mode1": "TEST",
            "Matches": "113",
            "Runs": "8848",
            "HS": "254*",
            "Avg": "49.15",
            "SR": "55.66",
            "100s": "29",
            "50s": "30"
        }
    },
    {
        "Batting Career Summary2": {
            "Mode2": "ODI",
            "Matches": "292",
            "Runs": "13794",
            "HS": "183",
            "Avg": "58.69",
            "SR": "93.62",
            "100s": "50",
            "50s": "72"
        }
    },
    {
        "Batting Career Summary3": {
            "Mode2": "T20I",
            "Matches": "117",
            "Runs": "4008",
            "HS": "122*",
            "Avg": "51.38",
            "SR": "137.96",
            "100s": "1",
            "50s": "37"
        }
    },
    {
        "Bowling Career Summary1": {
            "Mode3": "TEST",
            "Matches": "12",
            "Runs": "12",
            "Wickets": "0",
            "BBI": "0/0",
            "BBM": "0.00",
            "Econ": "3.00",
            "5W": "0"
        }
    },
    {
        "Bowling Career Summary2": {
            "Mode3": "ODI",
            "Matches": "10",
            "Runs": "10",
            "Wickets": "4",
            "BBI": "1/15",
            "BBM": "0.00",
            "Econ": "5.00",
            "5W": "0"
        }
    },
    {
        "Bowling Career Summary3": {
            "Mode3": "T20I",
            "Matches": "12",
            "Runs": "12",
            "Wickets": "0",
            "BBI": "0/0",
            "BBM": "0.00",
            "Econ": "12.00",
            "5W": "0"
        }
    }
]
</code></pre>

<h3>GET /schedule</h3>
<p>This endpoint provides a schedule of upcoming international cricket series. It fetches data from Cricbuzz and lists upcoming matches.</p>
<p>The API returns a JSON array where each element is a string describing an upcoming match.</p>
<pre><code>
[
    "India vs South Africa, 1st ODI",
    "India vs South Africa, 2nd ODI",
    "India vs South Africa, 3rd ODI",
    ...
]
</code></pre>

<h3>GET /live</h3>
<p>This endpoint retrieves details of live cricket matches currently in progress. It fetches live score updates from Cricbuzz.</p>
<p>The API returns a JSON array where each element is a string describing a live match with scores and current over information.</p>
<pre><code>
[
    "Australia 45/1 (8.4 ov)",
    "Bangladesh 136/4 (17.4 ov)",
    "India 118/2 (13.3 ov)",
    ...
]
</code></pre>

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
    "season": 2024,
    "series_id": 6762,
    "matches": [
        {
            "date": "Sat, Mar 23, 2024",
            "match_number": "Match 1",
            "team1": "Chennai Super Kings",
            "team2": "Royal Challengers Bangalore",
            "venue": "MA Chidambaram Stadium, Chennai",
            "match_time": "8:00 PM IST",
            "gmt_time": "2:30 PM GMT",
            "formatted_date_time": "2024-03-23T20:00:00+05:30",
            "result": null,
            "status": "Upcoming",
            "is_live": false,
            "match_link": "https://www.cricbuzz.com/cricket-match/6762/1/csk-vs-rcb-1st-match-indian-premier-league-2024"
        },
        {
            "date": "Sun, Mar 24, 2024",
            "match_number": "Match 2",
            "team1": "Punjab Kings",
            "team2": "Delhi Capitals",
            "venue": "Punjab Cricket Association IS Bindra Stadium, Mohali",
            "match_time": "3:30 PM IST",
            "gmt_time": "10:00 AM GMT",
            "formatted_date_time": "2024-03-24T15:30:00+05:30",
            "result": null,
            "status": "Upcoming",
            "is_live": false,
            "match_link": "https://www.cricbuzz.com/cricket-match/6762/2/pbks-vs-dc-2nd-match-indian-premier-league-2024"
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
        "category": "International",
        "series_name": "India tour of South Africa, 2023-24",
        "date_range": "Dec 10, 2023 - Jan 07, 2024",
        "matches": [
            {
                "match_title": "1st T20I: South Africa vs India",
                "date_time": "Dec 10, 2023",
                "venue": "Kingsmead, Durban"
            },
            {
                "match_title": "2nd T20I: South Africa vs India",
                "date_time": "Dec 12, 2023",
                "venue": "St George's Park, Gqeberha"
            },
            ...
        ]
    },
    {
        "category": "T20 Leagues",
        "series_name": "Indian Premier League, 2024",
        "date_range": "Mar 22, 2024 - May 26, 2024",
        "matches": [
            {
                "match_title": "Match 1: Chennai Super Kings vs Royal Challengers Bangalore",
                "date_time": "Mar 22, 2024",
                "venue": "MA Chidambaram Stadium, Chennai"
            },
            ...
        ]
    },
    ...
]
</code></pre>

<h2>Key Features</h2>
<ul>
    <li><b>Player Statistics:</b> Retrieve comprehensive batting and bowling stats for any player across Test, ODI, and T20I formats.</li>
    <li><b>Live Scores:</b> Get real-time updates on all ongoing cricket matches.</li>
    <li><b>Upcoming Schedule:</b> View the schedule for upcoming international cricket series.</li>
    <li><b>IPL Schedule:</b> Fetch the complete schedule for any IPL season by specifying the year and series ID.</li>
    <li><b>All Series Data:</b> Explore a categorized list of all cricket series, including international, T20 leagues, domestic, and women's matches.</li>
</ul>
