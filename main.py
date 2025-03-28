from flask import Flask, jsonify, render_template, request # Added request
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import pytz
import time
import logging # Added logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO) # Log INFO level and above

if __name__ == "__main__":
    # Run with debug=True FOR DEVELOPMENT ONLY.
    app.run(host='0.0.0.0', port=8080, debug=True)

@app.route('/')
def index():
    """Home page - lists API endpoints dynamically as clickable links"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        # Exclude static routes and potentially internal scraping routes if desired
        if rule.endpoint != 'static':
            endpoints.append({
                'url': str(rule),
                'description': app.view_functions[rule.endpoint].__doc__ or 'No description available'
            })
    # Sort endpoints alphabetically by URL for consistency
    endpoints.sort(key=lambda x: x['url'])
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
    """Get live match scores summary"""
    try:
        link = "https://www.cricbuzz.com/cricket-match/live-scores"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(link, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        live_matches_data = []
        # Find all series blocks which contain match items
        series_blocks = soup.find_all("div", class_=lambda x: x and 'cb-plyr-tbody' in x.split() and 'cb-lv-main' in x.split())

        if not series_blocks:
             # Fallback or alternative structure check if needed, or return error
             # Let's try the original simple extraction as a fallback
             live_score_div = soup.find("div", class_="cb-col cb-col-100 cb-bg-white")
             if live_score_div:
                 matches_divs = live_score_div.find_all("div", class_="cb-scr-wll-chvrn cb-lv-scrs-col")
                 for match_div in matches_divs:
                     if match_div.text.strip():
                         live_matches_data.append({"raw_score_text": match_div.text.strip()})
                 if live_matches_data:
                     return jsonify(live_matches_data)
             # If fallback also fails
             return jsonify({"error": "Could not find any live match sections using known structures"}), 404

        for series_block in series_blocks:
            series_name_elem = series_block.find('h2', class_='cb-lv-grn-strip')
            series_name = series_name_elem.a.text.strip() if series_name_elem and series_name_elem.a else "Unknown Series"

            match_items = series_block.find_all('div', class_='cb-mtch-lst cb-col cb-col-100 cb-tms-itm')

            for match_item in match_items:
                match_data = {"series": series_name}

                # --- Header Info ---
                # Try finding the specific title link <a> first
                title_link_elem = match_item.find('a', class_='text-hvr-underline') # Using class from snippet
                if title_link_elem:
                    match_data['title'] = title_link_elem.text.strip().rstrip(',')
                    match_data['match_url'] = "https://www.cricbuzz.com" + title_link_elem['href'] if title_link_elem.has_attr('href') and title_link_elem['href'].startswith('/') else title_link_elem.get('href')

                    # Navigate up to find siblings for description and details
                    title_h3 = title_link_elem.parent # Assuming <a> is direct child of <h3>
                    if title_h3 and title_h3.name == 'h3':
                        header_container = title_h3.parent # Assuming <h3> is direct child of the container div
                        if header_container:
                            match_desc_elem = title_h3.find_next_sibling('span', class_='text-gray')
                            if match_desc_elem:
                                match_data['description'] = match_desc_elem.text.strip()

                            details_div = title_h3.find_next_sibling('div', class_='text-gray')
                            if details_div:
                                 details_text = ' '.join(span.text.strip() for span in details_div.find_all(recursive=False) if span.text.strip())
                                 details_text = re.sub(r'\s+•\s+', ' • ', details_text) # Standardize separators
                                 match_data['details'] = details_text.strip()
                else:
                    # Fallback: Try finding h3 directly again, just in case
                    title_h3_fallback = match_item.find('h3', class_='cb-lv-scr-mtch-hdr')
                    if title_h3_fallback and title_h3_fallback.a:
                         match_data['title'] = title_h3_fallback.a.text.strip().rstrip(',')
                         match_data['match_url'] = "https://www.cricbuzz.com" + title_h3_fallback.a['href'] if title_h3_fallback.a.has_attr('href') and title_h3_fallback.a['href'].startswith('/') else title_h3_fallback.a.get('href')
                         # Try finding siblings again
                         header_container = title_h3_fallback.parent
                         if header_container:
                            match_desc_elem = title_h3_fallback.find_next_sibling('span', class_='text-gray')
                            if match_desc_elem:
                                match_data['description'] = match_desc_elem.text.strip()
                            details_div = title_h3_fallback.find_next_sibling('div', class_='text-gray')
                            if details_div:
                                 details_text = ' '.join(span.text.strip() for span in details_div.find_all(recursive=False) if span.text.strip())
                                 details_text = re.sub(r'\s+•\s+', ' • ', details_text) # Standardize separators
                                 match_data['details'] = details_text.strip()


                # --- Score Info ---
                score_link_elem = match_item.find('a', class_='cb-lv-scrs-well-live')
                if score_link_elem:
                    # Add the main score link itself
                    score_href = score_link_elem.get('href')
                    if score_href:
                         match_data['score_url'] = "https://www.cricbuzz.com" + score_href if score_href.startswith('/') else score_href

                    bat_team_elem = score_link_elem.find('div', class_='cb-hmscg-bat-txt')
                    if bat_team_elem:
                        bat_name = bat_team_elem.find('div', class_='cb-hmscg-tm-nm')
                        bat_score = bat_team_elem.find('div', style=lambda value: value and 'width' in value)
                        match_data['batting_team'] = bat_name.text.strip() if bat_name else None
                        match_data['batting_score'] = bat_score.text.strip() if bat_score else None

                    bowl_team_elem = score_link_elem.find('div', class_='cb-hmscg-bwl-txt')
                    if bowl_team_elem:
                         bowl_name = bowl_team_elem.find('div', class_='cb-hmscg-tm-nm')
                         match_data['bowling_team'] = bowl_name.text.strip() if bowl_name else None
                         # Bowling score div exists but is usually empty in the live summary

                    status_elem = score_link_elem.find('div', class_='cb-text-live')
                    match_data['status'] = status_elem.text.strip() if status_elem else None

                # --- Links ---
                nav_elem = match_item.find('nav', class_='cb-col-100 cb-col padt5')
                if nav_elem:
                    links = {}
                    for link_elem in nav_elem.find_all('a', class_='cb-text-link'):
                        title = link_elem.get('title', link_elem.text.strip())
                        href = link_elem.get('href')
                        if title and href:
                            # Ensure URL is absolute
                            abs_href = href if href.startswith('http') else "https://www.cricbuzz.com" + href
                            links[title.replace(' ', '_').lower()] = abs_href
                    match_data['links'] = links

                if match_data.get('title'): # Only add if we found at least a title
                    live_matches_data.append(match_data)

        return jsonify(live_matches_data)

    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch live scores: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/scrape/scorecard', methods=['GET'])
def scrape_scorecard():
    """Scrape detailed scorecard from a given Cricbuzz URL (?url=...)"""
    url = request.args.get('url')
    app.logger.info(f"--- Scraping Scorecard URL: {url} ---") # DEBUG LOG
    if not url:
        app.logger.error("Scorecard scrape failed: Missing 'url' query parameter")
        return jsonify({"error": "Missing 'url' query parameter"}), 400

    # Basic URL validation (optional)
    if not url.startswith("https://www.cricbuzz.com/"):
        app.logger.error(f"Scorecard scrape failed: Invalid URL format: {url}")
        return jsonify({"error": "Invalid Cricbuzz URL provided"}), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        scorecard_data = {"url": url, "innings": []}

        # --- Attempt to find match status/result ---
        match_status_elem = soup.find('div', class_='cb-text-complete') # Example class, might need adjustment
        if match_status_elem:
            scorecard_data['match_status'] = match_status_elem.text.strip()
            app.logger.info(f"Found Match Status: {scorecard_data['match_status']}") # DEBUG LOG
        else:
            app.logger.warning("Match status element ('cb-text-complete') not found.") # DEBUG LOG


        # --- Attempt to find innings blocks ---
        # Cricbuzz often uses divs with id like 'innings_1', 'innings_2'
        innings_divs = soup.find_all('div', id=lambda x: x and x.startswith('innings_'))
        app.logger.info(f"Found {len(innings_divs)} potential innings divs by ID.") # DEBUG LOG

        if not innings_divs:
             # Fallback: Look for common scorecard container classes
             app.logger.warning("Innings divs by ID not found. Trying fallback selector 'cb-col cb-col-100 cb-scrd-itms'.") # DEBUG LOG
             innings_divs = soup.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms') # Example class
             app.logger.info(f"Found {len(innings_divs)} potential innings divs by fallback class.") # DEBUG LOG


        if not innings_divs:
            app.logger.error("Could not find any innings scorecards on the page.")
            return jsonify({"error": "Could not find innings scorecards on the page", "url": url}), 404

        for i, innings_div in enumerate(innings_divs):
            app.logger.info(f"Processing Innings Div {i+1}...") # DEBUG LOG
            inning_data = {"batting": [], "bowling": [], "extras": None, "total": None, "fall_of_wickets": None}

            # Innings Title (e.g., "RCB Innings")
            title_elem = innings_div.find('div', class_='cb-scrd-hdr-rw') # Example class
            inning_data['title'] = title_elem.text.strip() if title_elem else f"Innings {len(scorecard_data['innings']) + 1}"
            app.logger.info(f"  Innings Title: {inning_data['title']}") # DEBUG LOG

            # --- Batting Scorecard ---
            # Refined selector: Find the container, then look for player rows within it.
            # This assumes player rows are direct children divs with a link inside.
            batting_rows_container = innings_div # Often the innings div itself contains the rows
            if batting_rows_container:
                # Find rows that seem to contain player data (e.g., have a link for the player name)
                player_rows = batting_rows_container.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms', recursive=False) # Look for direct children first
                app.logger.info(f"  Found {len(player_rows)} potential batting rows/items in container.") # DEBUG LOG

                if not player_rows: # If direct children didn't work, search deeper
                     player_rows = batting_rows_container.find_all('div', class_='cb-col cb-col-100 cb-scrd-itms')
                     app.logger.info(f"  Found {len(player_rows)} potential batting rows/items searching deeper.") # DEBUG LOG


                batters_found = 0
                for row_idx, row in enumerate(player_rows):
                     # Check if it looks like a player row (e.g., contains a player link)
                     player_link = row.find('a', href=lambda x: x and '/profiles/' in x)
                     if player_link:
                         cols = row.find_all('div', class_=lambda x: x and x.startswith('cb-col cb-col-'), recursive=False)
                         app.logger.info(f"    Row {row_idx+1}: Found {len(cols)} columns. Player link: {player_link.text.strip()}") # DEBUG LOG
                         if len(cols) >= 7: # Expect player, dismissal, R, B, 4s, 6s, SR
                             player_name = cols[0].text.strip()
                             dismissal = cols[1].text.strip()
                             runs = cols[2].text.strip()
                             balls = cols[3].text.strip()
                             fours = cols[4].text.strip()
                             sixes = cols[5].text.strip()
                             sr = cols[6].text.strip()
                             inning_data['batting'].append({
                                 "player": player_name, "dismissal": dismissal, "R": runs,
                                 "B": balls, "4s": fours, "6s": sixes, "SR": sr
                             })
                             batters_found += 1
                         else:
                             app.logger.warning(f"    Row {row_idx+1}: Expected >= 7 columns for player, found {len(cols)}.") # DEBUG LOG
                     elif "Extras" in row.text:
                         extras_val_elem = row.find('div', class_='cb-col-right')
                         inning_data['extras'] = extras_val_elem.text.strip() if extras_val_elem else 'N/A'
                         app.logger.info(f"    Row {row_idx+1}: Found Extras: {inning_data['extras']}") # DEBUG LOG
                     elif "Total" in row.text:
                         total_val_elem = row.find('div', class_='cb-col-right')
                         inning_data['total'] = total_val_elem.text.strip() if total_val_elem else 'N/A'
                         app.logger.info(f"    Row {row_idx+1}: Found Total: {inning_data['total']}") # DEBUG LOG
                     # Add checks for "Did not bat" or "Fall of wickets" sections if needed

                app.logger.info(f"  Finished processing batting rows. Found {batters_found} batters.") # DEBUG LOG
            else:
                app.logger.warning("  Could not find batting rows container.") # DEBUG LOG


            # --- Bowling Scorecard --- (Placeholder - needs similar detailed logic)
            app.logger.info("  Processing Bowling Scorecard (Placeholder)...") # DEBUG LOG
            # bowling_table = innings_div.find(...) # Find the specific bowling table
            # if bowling_table:
            #    bowler_rows = bowling_table.find_all(...)
            #    for row in bowler_rows:
            #        cols = row.find_all(...)
            #        if len(cols) >= 6: # O, M, R, W, Econ, 0s etc.
            #           ... extract data ...
            #           inning_data['bowling'].append({...})

            # --- Fall of Wickets --- (Placeholder - needs similar detailed logic)
            app.logger.info("  Processing Fall of Wickets (Placeholder)...") # DEBUG LOG
            # fow_div = innings_div.find('div', text=re.compile(r'Fall of Wickets')) # Example
            # if fow_div:
            #    fow_data = fow_div.find_next_sibling('div').text.strip() # Example
            #    inning_data['fall_of_wickets'] = fow_data


            scorecard_data['innings'].append(inning_data)

        app.logger.info(f"--- Finished Scraping Scorecard. Innings found: {len(scorecard_data['innings'])} ---") # DEBUG LOG
        return jsonify(scorecard_data)

    except requests.RequestException as e:
        app.logger.error(f"Failed to fetch scorecard URL {url}: {str(e)}")
        return jsonify({"error": f"Failed to fetch scorecard URL: {str(e)}", "url": url}), 500
    except Exception as e:
        # Log the full error for debugging
        app.logger.error(f"Error scraping scorecard URL {url}: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred while scraping scorecard: {str(e)}", "url": url}), 500


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
        
        for row in soup.select('div.cb-col-100.cb-col.cb-series-matches'):
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
