from flask import Flask, request, send_file, jsonify, render_template
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__)

# FPL API endpoints
league_url_template = 'https://fantasy.premierleague.com/api/leagues-classic/{}/standings/'
entry_url_template = 'https://fantasy.premierleague.com/api/entry/{}/history/'

def fetch_league_data(league_id):
    # Fetch league standings
    response = requests.get(league_url_template.format(league_id))
    response.raise_for_status()
    league_data = response.json()

    # Extract manager details
    managers = [
        {"Team Name": player['entry_name'], "Player Name": player['player_name'], "Entry ID": player['entry']}
        for player in league_data['standings']['results']
    ]

    all_gameweeks_data = []

    for manager in managers:
        entry_id = manager["Entry ID"]
        entry_response = requests.get(entry_url_template.format(entry_id))
        entry_response.raise_for_status()
        entry_data = entry_response.json()

        # Extract gameweek points
        gameweeks = entry_data['current']
        gameweek_points = {f"GW {gw['event']}": gw['points'] for gw in gameweeks}
        gameweek_points.update(manager)
        all_gameweeks_data.append(gameweek_points)

    # Create a DataFrame
    df = pd.DataFrame(all_gameweeks_data)
    df.fillna('', inplace=True)  # Replace NaN values
    return df

@app.route('/')
def home():
    # Serve the HTML form
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_excel():
    try:
        league_id = request.form.get('league_code')
        if not league_id:
            return jsonify({"error": "Please provide a league code"}), 400

        # Fetch league data
        df = fetch_league_data(league_id)

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
    app.run(debug=False)
