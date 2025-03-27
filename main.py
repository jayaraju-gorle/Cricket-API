from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import pytz
import time

app = Flask(__name__)
CORS(app)

if __name__ == "__main__":
    # Run with debug=True FOR DEVELOPMENT ONLY.
    app.run(host='0.0.0.0', port=8080, debug=True)

@app.route('/')
def index():
    """Home page - lists API endpoints dynamically as clickable links"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':  # Exclude static routes
            endpoints.append({
                'url': str(rule),
                'description': app.view_functions[rule.endpoint].__doc__ or 'No description available'
            })
    return render_template('index.html', endpoints=endpoints)

@app.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):
    """Get player information"""
    try:
        source = requests.get(f"https://www.google.com/search?q={player_name}%20cricbuzz").text
        page = BeautifulSoup(source, "lxml")
        page_link_element = page.find("div", class_="kCrYT")
        if not page_link_element or not page_link_element.find("a"):
            return jsonify({"error": "Could not find player link from Google search"}), 404
        link_suffix = page_link_element.find("a")["href"]
        player_url = f"https://www.cricbuzz.com{link_suffix[6:]}"

        cricbuzz_page = requests.get(player_url).text
        cricbuzz_soup = BeautifulSoup(cricbuzz_page, "lxml")

        profile = cricbuzz_soup.find("div", id="playerProfile")
        if not profile:
            return jsonify({"error": "Could not find player profile section on Cricbuzz"}), 404
        pc = profile.find("div", class_="cb-col-100 cb-bg-white")
        if not pc:
            return jsonify({"error": "Could not find player info container"}), 404

        name_element = pc.find("h1", class_="cb-font-40")
        name = name_element.text.strip() if name_element else "N/A"
        country_element = pc.find("h3", class_="cb-font-18 text-gray")
        country = country_element.text.strip() if country_element else "N/A"
        image_element = pc.find('img')
        image_src = image_element['src'] if image_element and 'src' in image_element.attrs else "N/A"

        personal_info = cricbuzz_soup.find_all("div", class_="cb-col cb-col-60 cb-lst-itm-sm")
        role = personal_info[2].text.strip() if len(personal_info) > 2 else "N/A"
        icc_rankings = cricbuzz_soup.find_all("div", class_="cb-col cb-col-25 cb-plyr-rank text-right")

        rankings = {}
        rank_categories = ["Test Batting", "ODI Batting", "T20 Batting", "Test Bowling", "ODI Bowling", "T20 Bowling"]
        for i, category in enumerate(rank_categories):
            rankings[category] = icc_rankings[i].text.strip() if len(icc_rankings) > i else "N/A"

        summary_tables = cricbuzz_soup.find_all("div", class_="cb-plyr-tbl")
        career_summary = []
        if len(summary_tables) >= 2:
            batting_table = summary_tables[0]
            bowling_table = summary_tables[1]
            categories = [td.text for td in batting_table.find_all("td", class_="cb-col-8")[:3]]

            batting_stats = batting_table.find_all("td", class_="text-right")
            batting_formats = ["Test", "ODI", "T20"]
            batting_career = []
            for i, format_name in enumerate(batting_formats):
                start_index = i * 13
                if len(batting_stats) > start_index + 12:
                    batting_career.append({
                        "Format": categories[i] if len(categories) > i else format_name,
                        "Matches": batting_stats[start_index + 0].text, "Runs": batting_stats[start_index + 3].text,
                        "HS": batting_stats[start_index + 4].text, "Avg": batting_stats[start_index + 5].text,
                        "SR": batting_stats[start_index + 7].text, "100s": batting_stats[start_index + 8].text, "50s": batting_stats[start_index + 10].text
                    })
                else:
                    batting_career.append({"Format": categories[i] if len(categories) > i else format_name, "Matches": "N/A", "Runs": "N/A", "HS": "N/A", "Avg": "N/A", "SR": "N/A", "100s": "N/A", "50s": "N/A"})

            bowling_stats = bowling_table.find_all("td", class_="text-right")
            bowling_formats = ["Test", "ODI", "T20"]
            bowling_career = []
            for i, format_name in enumerate(bowling_formats):
                start_index = i * 13
                if len(bowling_stats) > start_index + 12:
                    bowling_career.append({
                        "Format": categories[i] if len(categories) > i else format_name,
                        "Balls": bowling_stats[start_index + 2].text, "Runs Conceded": bowling_stats[start_index + 3].text,
                        "Wickets": bowling_stats[start_index + 4].text, "BBI": bowling_stats[start_index + 5].text, "BBM": bowling_stats[start_index + 6].text,
                        "Economy": bowling_stats[start_index + 7].text, "5W": bowling_stats[start_index + 10].text
                    })
                else:
                    bowling_career.append({"Format": categories[i] if len(categories) > i else format_name, "Balls": "N/A", "Runs Conceded": "N/A", "Wickets": "N/A", "BBI": "N/A", "BBM": "N/A", "Economy": "N/A", "5W": "N/A"})


            career_summary = {
                "Batting Career Summary": batting_career,
                "Bowling Career Summary": bowling_career
            }

        player_data = {
            "Player Name": name,
            "Country": country,
            "Role": role,
            "Image Source": image_src,
            "Rankings": rankings,
            **career_summary
        }
        return jsonify(player_data)

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch player data: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@app.route('/schedule')
def schedule():
    """Get upcoming match schedules"""
    try:
        schedule_url = "https://www.cricbuzz.com/cricket-schedule/upcoming-series/international"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(schedule_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        schedule_div = soup.find('div', class_='cb-sched-tabs')
        if not schedule_div:
            return jsonify({"error": "Could not find schedule section"}), 404

        match_sections = schedule_div.find_all('div', class_='cb-col-100 cb-col cb-sch-lst')
        if not match_sections:
            return jsonify({"error": "No match sections found"}), 404

        matches = []
        for section in match_sections:
            date_header = section.find_previous('h2', class_='cb-sch-day-header')
            date = date_header.text.strip() if date_header else "Unknown Date"

            match_items = section.find_all('div', class_='cb-col-100 cb-col')
            for match_item in match_items:
                if not match_item.text.strip():
                    continue
                match_text = match_item.text.strip()
                if date != "Unknown Date":
                    matches.append({
                        "date": date,
                        "match_details": match_text
                    })
                else:
                    matches.append(match_text)

        return jsonify(matches)

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch schedule: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/live')
def live_matches():
    """Get live match scores"""
    try:
        link = "https://www.cricbuzz.com/cricket-match/live-scores"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(link, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        live_score_div = soup.find("div", class_="cb-col cb-col-100 cb-bg-white")
        if not live_score_div:
            return jsonify({"error": "Could not find live matches section on the page"}), 404

        matches_divs = live_score_div.find_all("div", class_="cb-scr-wll-chvrn cb-lv-scrs-col")
        live_matches_data = []
        for match_div in matches_divs:
            if match_div.text.strip():
                live_matches_data.append(match_div.text.strip())
        return jsonify(live_matches_data)

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch live scores: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/all-series', methods=['GET'])
def all_series():
    """Get all cricket series"""
    try:
        url = "https://www.cricbuzz.com/cricket-schedule/series/all"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        series_sections = soup.find_all('div', class_='cb-sch-lst')
        if not series_sections:
            return jsonify({"error": "No series found on the page"}), 404

        all_series_data = []
        for section in series_sections:
            category_header = section.find_previous('h2', class_='cb-col-100 cb-sch-hdr')
            category = category_header.text.strip() if category_header else "Unknown"
            series_items = section.find_all('div', class_='cb-col-100 cb-col')
            series_list = []
            for series_item in series_items:
                if not series_item.text.strip():
                    continue
                series_info = series_item.find('a')
                if series_info and '/series/' in series_info['href']:
                    series_name = series_info.text.strip()
                    series_id_match = re.search(r'/series/(\d+)/', series_info['href'])
                    series_id = series_id_match.group(1) if series_id_match else "N/A"
                    series_list.append({
                        "series_name": series_name,
                        "series_id": series_id
                    })
            all_series_data.append({
                "category": category,
                "series": series_list
            })
        return jsonify(all_series_data)

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch series list: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/ipl-schedule/<int:year>/<int:series_id>', methods=['GET'])
def get_ipl_schedule(year, series_id):
    """Get IPL schedule for a given year and series"""
    try:
        url = f"https://www.cricbuzz.com/cricket-series/{series_id}/indian-premier-league-{year}/matches"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch data from Cricbuzz for IPL {year}"}), 500
        
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = []
        
        # Create IST timezone (UTC+5:30)
        ist_timezone = timezone(timedelta(hours=5, minutes=30))
        
        for row in soup.select('div.cb-col-100.cb-col.cb-series-brdr'):
            try:
                date_div = row.select_one('div.cb-col-25 span')
                match_div = row.select_one('div.cb-col-60')
                time_div = row.select_one('div.cb-col-40')
                
                if not all([date_div, match_div, time_div]):
                    continue
                
                date = date_div.text.strip()  # e.g., "Mar 26, Wed"
                
                # Extract match details
                match_link_elem = match_div.select_one('a')
                if not match_link_elem:
                    continue
                    
                match_link = match_link_elem['href']
                match_title = match_link_elem.select_one('span').text.strip()
                
                # Parse teams and match number
                if ' vs ' in match_title and ', ' in match_title:
                    teams_part, match_number = match_title.rsplit(', ', 1)
                    team1, team2 = teams_part.split(' vs ', 1)
                else:
                    team1, team2, match_number = "Unknown", "Unknown", match_title
                
                venue = match_div.select_one('div.text-gray').text.strip()
                
                # Determine match status
                status_elem = match_div.select_one('a.cb-text-complete, a.cb-text-live, a.cb-text-preview, a.cb-text-drink')
                status_text = status_elem.text.strip() if status_elem else "Upcoming"
                
                if "won by" in status_text:
                    status = "Completed"
                    result = status_text
                elif status_text == "Strategic Timeout" or "live" in status_text.lower():
                    status = "Live"
                    result = None
                else:
                    status = "Upcoming"
                    result = None
                
                # Extract match time
                match_time = time_div.select_one('span.schedule-date').text.strip()  # e.g., "7:30 PM"
                
                # Parse date and time
                try:
                    # Extract timestamp if available
                    timestamp_elem = time_div.select_one('span.schedule-date')
                    if timestamp_elem and 'timestamp' in timestamp_elem.attrs:
                        timestamp_ms = int(timestamp_elem['timestamp'])
                        match_datetime = datetime.fromtimestamp(timestamp_ms/1000, tz=ist_timezone)
                    else:
                        # Manual parsing as fallback
                        date_parts = date.split(", ")[0]  # Get "Mar 26" from "Mar 26, Wed"
                        date_str = f"{date_parts} {year}"  # Create "Mar 26 2025"
                        
                        # Parse date
                        match_date = datetime.strptime(date_str, "%b %d %Y")
                        
                        # Parse time
                        time_obj = datetime.strptime(match_time, "%I:%M %p")
                        
                        # Combine date and time
                        match_datetime = datetime(
                            year=match_date.year,
                            month=match_date.month,
                            day=match_date.day,
                            hour=time_obj.hour,
                            minute=time_obj.minute,
                            tzinfo=ist_timezone
                        )
                    
                    formatted_date_time = match_datetime.isoformat()
                except Exception as e:
                    formatted_date_time = f"{date} {match_time}"
                
                # Extract GMT time
                time_details = time_div.select_one('div.cb-font-12')
                gmt_time = time_details.text.strip().split('/')[0].strip() if time_details else "GMT time not available"
                
                matches.append({
                    "date": date,
                    "match_number": match_number,
                    "team1": team1,
                    "team2": team2,
                    "venue": venue,
                    "match_time": match_time,
                    "gmt_time": gmt_time,
                    "formatted_date_time": formatted_date_time,
                    "status": status,
                    "is_live": status == "Live",
                    "result": result,
                    "match_link": f"https://www.cricbuzz.com{match_link}"
                })
            except Exception as e:
                # Log the error but continue processing other matches
                print(f"Error processing match: {str(e)}")
                continue
        
        return jsonify({
            "season": year,
            "series_id": series_id,
            "matches": matches
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Cache to store points table data
points_table_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 3600  # Cache for 1 hour

def scrape_points_table():
    """
    Scrapes the IPL 2025 points table from Cricbuzz and returns a list of team data.
    
    Returns:
        list: List of dictionaries containing team position, name, matches, wins, losses,
              ties, no results, points, and net run rate. Returns an error dict if scraping fails.
    """
    # Define the URL and headers to mimic a browser request
    url = "https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/points-table"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # Fetch the page
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch page, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    # Parse the HTML
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the points table (assuming class 'cb-srs-pnts')
    table = soup.find("table", class_="cb-srs-pnts")
    # print(table.prettify())
    if not table:
        return {"error": "Points table not found on the page"}

    # Initialize the result list and position counter
    points_data = []
    position = 1

    # Process each row in the table
    for row in table.find_all("tr"):
        tds = row.find_all("td")
        # Check if this is a team data row (9 <td> elements)
        if len(tds) == 9:
            try:
                # Extract team name from the first <td>
                team_div = tds[0].find("div", class_="cb-col cb-col-84")
                if not team_div:
                    continue  # Skip if team name div is missing
                team_name = team_div.text.strip()

                # Extract stats with safe conversion
                def safe_int(text):
                    try:
                        return int(text.strip())
                    except (ValueError, AttributeError):
                        return 0

                def safe_str(text):
                    return text.strip() if text else "N/A"

                matches = safe_int(tds[1].text)
                wins = safe_int(tds[2].text)
                losses = safe_int(tds[3].text)
                ties = safe_int(tds[4].text)
                no_results = safe_int(tds[5].text)
                points = safe_int(tds[6].text)
                nrr = safe_str(tds[7].text)

                # Compile team data
                team_data = {
                    "position": position,
                    "team": team_name,
                    "matches": matches,
                    "wins": wins,
                    "losses": losses,
                    "ties": ties,
                    "no_results": no_results,
                    "points": points,
                    "nrr": nrr
                }
                points_data.append(team_data)
                position += 1
            except Exception as e:
                # Log error and continue to next row
                print(f"Error processing row for position {position}: {str(e)}")
                continue

    return points_data if points_data else {"error": "No team data extracted"}

@app.route('/ipl/2025/points-table', methods=['GET'])
def get_points_table():
    """
    API endpoint to get the IPL 2025 points table.
    """
    current_time = time.time()
    
    # Check cache
    if (points_table_cache["data"] and 
        (current_time - points_table_cache["timestamp"]) < CACHE_DURATION):
        return jsonify(points_table_cache["data"])
    
    # Scrape fresh data
    data = scrape_points_table()
    if "error" in data:
        return jsonify(data), 500
    
    # Update cache
    points_table_cache["data"] = data
    points_table_cache["timestamp"] = current_time
    
    return jsonify(data)

def scrape_detailed_points_table():
    """
    Scrapes the IPL 2025 detailed points table from Cricbuzz, including match details for each team.
    
    Returns:
        list: List of dictionaries containing team position, name, matches, wins, losses,
              ties, no results, points, net run rate, and match details.
        dict: Error message if scraping fails.
    """
    url = "https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/points-table"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # Fetch the webpage
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch page, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    # Parse the HTML
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="cb-srs-pnts")
    if not table:
        return {"error": "Points table not found on the page"}

    points_data = []
    position = 1
    rows = table.find_all("tr")

    # Process rows to extract team data and match details
    i = 0
    while i < len(rows):
        row = rows[i]
        tds = row.find_all("td")

        # Identify team rows (should have 9 <td> elements)
        if len(tds) == 9:
            try:
                # Extract team name
                team_div = tds[0].find("div", class_="cb-col cb-col-84")
                team_name = team_div.text.strip() if team_div else "Unknown"

                # Helper functions for safe data extraction
                def safe_int(text):
                    try:
                        return int(text.strip())
                    except (ValueError, AttributeError):
                        return 0

                def safe_str(text):
                    return text.strip() if text else "N/A"

                # Extract team standings
                matches = safe_int(tds[1].text)
                wins = safe_int(tds[2].text)
                losses = safe_int(tds[3].text)
                ties = safe_int(tds[4].text)
                no_results = safe_int(tds[5].text)
                points = safe_int(tds[6].text)
                nrr = safe_str(tds[7].text)

                # Look for the dropdown row with match details
                match_details = []
                i += 1  # Move to the next row
                if i < len(rows):
                    dropdown_row = rows[i]
                    match_table = dropdown_row.find("table", class_="cb-srs-pnts-dwn-tbl")
                    if match_table:
                        for match_row in match_table.find_all("tr")[1:]:  # Skip header
                            match_tds = match_row.find_all("td")
                            if len(match_tds) == 4:
                                opponent = safe_str(match_tds[0].text)
                                description = safe_str(match_tds[1].text)
                                date = safe_str(match_tds[2].text)
                                result = safe_str(match_tds[3].text)
                                match_details.append({
                                    "opponent": opponent,
                                    "description": description,
                                    "date": date,
                                    "result": result
                                })

                # Compile team data
                team_data = {
                    "position": position,
                    "team": team_name,
                    "matches": matches,
                    "wins": wins,
                    "losses": losses,
                    "ties": ties,
                    "no_results": no_results,
                    "points": points,
                    "nrr": nrr,
                    "match_details": match_details
                }
                points_data.append(team_data)
                position += 1
            except Exception as e:
                print(f"Error processing team row: {str(e)}")
        i += 1  # Move to the next row

    return points_data if points_data else {"error": "No team data extracted"}

@app.route('/ipl/2025/detailed-points-table', methods=['GET'])
def get_detailed_points_table():
    """
    API endpoint to get the detailed points table for IPL 2025, including match details.
    """
    data = scrape_detailed_points_table()
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data)
