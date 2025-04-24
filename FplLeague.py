from flask import Flask, request, send_file, jsonify, render_template
import pandas as pd
import requests
from io import BytesIO

app = Flask(__name__)

# FPL API endpoints
league_url_template = 'https://fantasy.premierleague.com/api/leagues-classic/{}/standings/'
entry_url_template = 'https://fantasy.premierleague.com/api/entry/{}/history/'

def fetch_league_data(league_id, start_gw=None, end_gw=None):
    """
    Fetch league data from the FPL API and handle pagination to get all entries.
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

    all_gameweeks_data = []

    for manager in all_managers:
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
    df.fillna(0, inplace=True)  # Replace NaN values with 0

    # Filter columns by gameweek range if specified
    if start_gw and end_gw:
        try:
            start_gw = int(start_gw)
            end_gw = int(end_gw)
            gw_cols = [f"GW {i}" for i in range(start_gw, end_gw + 1)]
            # Always keep manager columns
            manager_cols = ["Team Name", "Player Name", "Entry ID"]
            cols_to_keep = manager_cols + [col for col in gw_cols if col in df.columns]
            df = df[cols_to_keep]
        except Exception:
            pass  # fallback to all columns if error
    return df

def get_gameweek_champions(df):
    """
    Find the highest-scoring participants for each gameweek and handle ties by listing all tied champions.
    """
    # Ensure all gameweek columns are numeric
    gameweeks = [col for col in df.columns if col.startswith("GW")]
    for gw in gameweeks:
        df[gw] = pd.to_numeric(df[gw], errors='coerce').fillna(0)

    champions_data = []

    for gw in gameweeks:
        max_points = df[gw].max()
        champions = df[df[gw] == max_points]

        # Concatenate the names of all tied champions
        champion_names = ", ".join(champions["Player Name"].tolist())

        champions_data.append({
            "Gameweek": gw.split(" ")[1],
            "Champion(s)": champion_names,
            "Points": int(max_points)
        })

    # Create a DataFrame for champions
    champions_df = pd.DataFrame(champions_data)
    return champions_df

@app.route('/')
def home():
    """
    Serve the HTML form for users to enter their league code.
    """
    return render_template('Index.html')

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        league_id = request.form.get('league_code')
        start_gw = request.form.get('start_gameweek')
        end_gw = request.form.get('end_gameweek')
        if not league_id:
            return jsonify({"error": "Please provide a league code"}), 400

        df = fetch_league_data(league_id, start_gw, end_gw)
        champions_df = get_gameweek_champions(df)
        data = {
            "league_data": df.to_dict(orient='records'),
            "champions_data": champions_df.to_dict(orient='records')
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download_excel():
    try:
        league_id = request.form.get('league_code')
        start_gw = request.form.get('start_gameweek')
        end_gw = request.form.get('end_gameweek')
        if not league_id:
            return jsonify({"error": "Please provide a league code"}), 400

        df = fetch_league_data(league_id, start_gw, end_gw)
        champions_df = get_gameweek_champions(df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='League Data')
            champions_df.to_excel(writer, index=False, sheet_name='Gameweek Champions')
        output.seek(0)

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
