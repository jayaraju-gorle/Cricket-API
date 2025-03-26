from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

@app.route('/')
def index():
    return "Hey there! Welcome to the Cricket API"

@app.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):

    source = requests.get(f"https://www.google.com/search?q={player_name}%20cricbuzz").text

    page = BeautifulSoup(source, "lxml")
    page = page.find("div",class_="kCrYT")
    link = page.find("a", href=re.compile(r"[/]([a-z]|[A-Z])\w+")).attrs["href"]
    c =  requests.get(link[7:]).text
    cric = BeautifulSoup(c, "lxml")

    profile = cric.find("div",id="playerProfile")
    pc = profile.find("div",class_="cb-col cb-col-100 cb-bg-white")

    #name country and image
    name = pc.find("h1",class_="cb-font-40").text  #1
    country = pc.find("h3",class_="cb-font-18 text-gray").text #2
    images = pc.findAll('img')
    for image in images:
        i = image['src']    #3

    #personal information and rankings
    personal =cric.find_all("div",class_="cb-col cb-col-60 cb-lst-itm-sm")
    role = personal[2].text.strip()  #5
    icc = cric.find_all("div",class_="cb-col cb-col-25 cb-plyr-rank text-right")
    tb = icc[0].text.strip()  #6
    ob = icc[1].text.strip()  #7
    twb = icc[2].text.strip() #8

    tbw=icc[3].text.strip()  #9
    obw=icc[4].text.strip()  #10
    twbw=icc[5].text.strip() #11


    #summary of the stata
    summary  = cric.find_all("div",class_="cb-plyr-tbl")
    batting =summary[0]
    bowling =summary[1]

    cat = cric.find_all("td",class_="cb-col-8")


    batstat = batting.find_all("td",class_="text-right")
    #test
    testmatches = batstat[0].text
    testruns = batstat[3].text
    tesths = batstat[4].text
    testavg = batstat[5].text
    testsr = batstat[7].text              
    test100 = batstat[8].text
    test50 = batstat[10].text

    #odii
    odimatches = batstat[13].text
    odiruns = batstat[16].text
    odihs = batstat[17].text
    odiavg = batstat[18].text
    odisr = batstat[20].text
    odi100 = batstat[21].text      
    odi50 = batstat[23].text

    #t20
    tmatches = batstat[26].text
    truns = batstat[29].text
    ths = batstat[30].text
    tavg = batstat[31].text         
    tsr = batstat[33].text
    t100 = batstat[34].text
    t50 = batstat[36].text


    bowstat = bowling.find_all("td",class_="text-right")

    testballs = bowstat[2].text
    testbruns = bowstat[3].text
    testwickets = bowstat[4].text
    testbbi = bowstat[5].text
    testbbm = bowstat[6].text
    testecon = bowstat[7].text
    test5w = bowstat[10].text

    odiballs = bowstat[14].text
    odibruns = bowstat[15].text
    odiwickets = bowstat[16].text
    odibbi = bowstat[17].text
    odiecon = bowstat[19].text
    odi5w = bowstat[22].text

    tballs = bowstat[26].text
    tbruns = bowstat[27].text
    twickets = bowstat[28].text
    tbbi = bowstat[29].text
    tecon = bowstat[31].text
    t5w = bowstat[34].text

    data1 = [ {"Player Name": name, "Country": country , "Role":  role , "Batting Career Summary 1": { "Mode1": cat[0].text, "Matches": testmatches, "Runs": testruns ,"HS": tesths, "Avg": testavg ,"SR":testsr ,"100s": test100 ,"50s": test50 }}]
    data2 = [ { "Batting Career Summary2": { "Mode2": cat[1].text, "Matches": odimatches, "Runs": odiruns ,"HS": odihs, "Avg": odiavg ,"SR":odisr ,"100s": odi100 ,"50s": odi50}}]
    data3 = [ { "Batting Career Summary3": { "Mode2": cat[1].text, "Matches": tmatches, "Runs": truns ,"HS": ths, "Avg": tavg ,"SR":tsr ,"100s": t100 ,"50s": t50}}]
    data4 = [ { "Bowling Career Summary1": { "Mode3": cat[2].text, "Matches": testballs, "Runs": testbruns ,"Wickets": testwickets, "BBI": testbbi, "BBM": testbbm, "Econ": testecon, "5W": test5w}}]
    data5 = [ { "Bowling Career Summary2": { "Mode3": cat[2].text, "Matches": odiballs, "Runs": odibruns ,"Wickets": odiwickets, "BBI": odibbi, "BBM": odiecon, "Econ": odiecon, "5W": odi5w}}]
    data6 = [ { "Bowling Career Summary3": { "Mode3": cat[2].text, "Matches": tballs, "Runs": tbruns ,"Wickets": twickets, "BBI": tbbi, "BBM": tecon, "Econ": tecon, "5W": t5w}}]
    return jsonify (data1, data2, data3, data4, data5, data6) 
        
@app.route('/schedule')
def schedule():
    link = f"https://www.cricbuzz.com/cricket-schedule/upcoming-series/international"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")
    page = page.find_all("div",class_="cb-col-100 cb-col")
    first = page[0].find_all("div",class_="cb-col-100 cb-col")
    matches = []
    for i in range(len(first)):
        matches.append(first[i].text)
    
    
    return jsonify(matches)

@app.route('/live')
def live_matches():
    link = f"https://www.cricbuzz.com/cricket-match/live-scores"
    source = requests.get(link).text
    page = BeautifulSoup(source, "lxml")

    page = page.find("div",class_="cb-col cb-col-100 cb-bg-white")
    matches = page.find_all("div",class_="cb-scr-wll-chvrn cb-lv-scrs-col")

    live_matches = []

    for i in range(len(matches)):
        live_matches.append(matches[i].text)
    
    
    return jsonify(live_matches)

@app.route('/ipl-schedule/<int:year>/<int:series_id>', methods=['GET'])
def get_ipl_schedule(year, series_id):
    try:
        # Dynamic URL based on year and series_id
        url = f"https://www.cricbuzz.com/cricket-series/{series_id}/indian-premier-league-{year}/matches"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch data from Cricbuzz for IPL {year}"}), 500
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        matches = []
        
        # Find all match rows - these are in table-like format on Cricbuzz
        match_rows = soup.select('div.cb-series-matches > div')
        
        current_date = None
        
        for row in match_rows:
            # Check if this is a date header
            if 'cb-series-matches-head' in row.get('class', []):
                current_date = row.text.strip()
                continue
            
            # Extract match details - each match has team names, venue and time
            match_details = row.select_one('div[class*="cb-col-60"]')
            venue_details = row.select_one('div[class*="cb-col-40"]')
            
            if not match_details or not venue_details:
                continue
                
            match_title = match_details.text.strip()
            venue_text = venue_details.text.strip()
            
            # Extract match time and status
            match_time_div = row.select_one('div.cb-col-100')
            match_time = match_time_div.text.strip() if match_time_div else "Time not available"
            
            # Parse team names and match number from title
            match_info = match_title.split(',')
            if len(match_info) >= 2:
                teams = match_info[0].split(' vs ')
                team1 = teams[0].strip() if len(teams) > 0 else "Team 1 not available"
                team2 = teams[1].strip() if len(teams) > 1 else "Team 2 not available"
                match_number = match_info[1].strip()
            else:
                team1 = "Team 1 not available"
                team2 = "Team 2 not available"
                match_number = ""
            
            # Check match status
            result_div = row.select_one('div.cb-text-complete')
            result = result_div.text.strip() if result_div else None
            
            # Find if match is live
            live_div = row.select_one('div.cb-text-live')
            is_live = True if live_div else False
            
            # Determine match status
            if result:
                status = "Completed"
            elif is_live:
                status = "Live"
            else:
                status = "Upcoming"
            
            matches.append({
                "date": current_date,
                "match_number": match_number,
                "team1": team1,
                "team2": team2,
                "venue": venue_text,
                "match_time": match_time,
                "result": result,
                "status": status,
                "is_live": is_live
            })
        
        return jsonify({
            "season": year,
            "series_id": series_id,
            "matches": matches
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/all-series', methods=['GET'])
def all_series():
    try:
        # URL for all series schedules on Cricbuzz
        url = "https://www.cricbuzz.com/cricket-schedule/series/all"
        
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find all series containers
        series_sections = soup.find_all('div', class_='cb-sch-lst')
        
        if not series_sections:
            return jsonify({"error": "No series found on the page"}), 404
        
        # List to store all series data
        all_series_data = []
        
        # Iterate through each series section (e.g., International, T20 Leagues, Domestic, Women)
        for section in series_sections:
            # Extract the category (e.g., "T20 Leagues")
            category = section.find_previous('h2', class_='cb-col-100 cb-sch-hdr')
            category = category.text.strip() if category else "Unknown Category"
            
            # Find all series within this category
            series_blocks = section.find_all('div', class_='cb-col-100 cb-col')
            
            for series_block in series_blocks:
                # Extract series name and date range
                series_name = series_block.find('a', class_='text-hvr-underline')
                series_name = series_name.text.strip() if series_name else "Unknown Series"
                
                date_range = series_block.find('div', class_='text-gray')
                date_range = date_range.text.strip() if date_range else "TBD"
                
                # Find all matches within this series
                match_blocks = series_block.find_all('div', class_='cb-col-100 cb-col')
                matches = []
                
                for match_block in match_blocks:
                    # Extract match details
                    match_title = match_block.find('a', class_='text-hvr-underline')
                    match_title = match_title.text.strip() if match_title else "TBD"
                    
                    date_time = match_block.find('div', class_='text-gray')
                    date_time = date_time.text.strip() if date_time else "TBD"
                    
                    venue = match_block.find('div', class_='text-gray', string=lambda x: x and ',' in x)
                    venue = venue.text.strip() if venue else "TBD"
                    
                    # Create a match object
                    match = {
                        "match_title": match_title,
                        "date_time": date_time,
                        "venue": venue
                    }
                    matches.append(match)
                
                # Create a series object
                series = {
                    "category": category,
                    "series_name": series_name,
                    "date_range": date_range,
                    "matches": matches
                }
                all_series_data.append(series)
        
        # Return the list of series as JSON
        return jsonify(all_series_data)
    
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch series schedules: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    # Run with debug=True FOR DEVELOPMENT ONLY.
    app.run(host='0.0.0.0', port=8080, debug=True)