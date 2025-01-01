from flask import Flask, request, send_file, jsonify, render_template
import pandas as pd
import requests
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

# FPL API endpoints
league_url_template = 'https://fantasy.premierleague.com/api/leagues-classic/{}/standings/'
entry_url_template = 'https://fantasy.premierleague.com/api/entry/{}/history/'


def fetch_manager_data(manager, specific_gameweek=None):
    """
    Fetch gameweek data for a single manager with optional filtering for a specific gameweek.
    """
    try:
        entry_id = manager["Entry ID"]
        entry_response = requests.get(entry_url_template.format(entry_id))
        entry_response.raise_for_status()
        entry_data = entry_response.json()

        # Extract gameweek points
        gameweeks = entry_data['current']
        if specific_gameweek:
            gameweeks = [gw for gw in gameweeks if gw['event'] == specific_gameweek]

        gameweek_points = {f"GW {gw['event']}": gw['points'] for gw in gameweeks}
        gameweek_points.update(manager)
        return gameweek_points
    except Exception as e:
        print(f"Error fetching data for manager {manager['Player Name']}: {e}")
        return None


def fetch_league_data(league_id, specific_gameweek=None):
    """
    Fetch league data from the FPL API with optional filtering for a specific gameweek.
    """
    all_managers = []
    page = 1

    while True:
        # Fetch league standings for the current page
        response = requests.get(league_url_template.format(league_id), params={'page': page})
        response.raise_for_status()
        league_data = response.json()

        # Extract manager details from the current page
        managers = [
            {"Team Name": player['entry_name'], "Player Name": player['player_name'], "Entry ID": player['entry']}
            for player in league_data['standings']['results']
        ]
        all_managers.extend(managers)

        # Check if there are more pages
        if league_data['standings']['has_next']:
            page += 1
        else:
            break

    # Fetch data for all managers concurrently
    all_gameweeks_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_manager = {
            executor.submit(fetch_manager_data, manager, specific_gameweek): manager
            for manager in all_managers
        }
        for future in as_completed(future_to_manager):
            result = future.result()
            if result:
                all_gameweeks_data.append(result)

    # Create a DataFrame
    df = pd.DataFrame(all_gameweeks_data)
    df.fillna('', inplace=True)  # Replace NaN values
    return df


@app.route('/')
def home():
    """
    Serve the HTML form for users to enter their league code and filters.
    """
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_excel():
    """
    Fetch league data and return it as a downloadable Excel file.
    """
    try:
        league_id = request.form.get('league_code')
        specific_gameweek = request.form.get('gameweek')

        if not league_id:
            return jsonify({"error": "Please provide a league code"}), 400

        # Convert gameweek input to integer if provided
        specific_gameweek = int(specific_gameweek) if specific_gameweek else None

        # Fetch league data
        df = fetch_league_data(league_id, specific_gameweek)

        # Save the DataFrame to an Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='League Data')
        output.seek(0)

        # Send the Excel file as a downloadable response
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'league_{league_id}.xlsx'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Ensure the app runs on the correct host and port for App Engine
    app.run(host='0.0.0.0', port=8080, debug=False)
