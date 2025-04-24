# FPL League Data Fetcher

This web application allows you to fetch, view, and download Fantasy Premier League (FPL) league data for any public league. You can specify a range of gameweeks to analyze, see per-gameweek points for all managers, and identify the top scorer(s) for each gameweek.

---

## Features

- **Fetch FPL League Data:** Enter a league code to retrieve all managers and their points for each gameweek.
- **Gameweek Range:** Specify a start and end gameweek (1–38) to focus on a particular part of the season.
- **Display Data:** View the league data and gameweek champions directly on the website in neat, scrollable tables.
- **Download Excel:** Download the league data and gameweek champions as an Excel file with two sheets.


---

## How It Works

1. **Enter League Code:**  
   Input the FPL league code in the form. Optionally, set a start and end gameweek.

2. **Display Data:**  
   Click "Display Data" to fetch and view the league standings and gameweek champions for the selected range.

3. **Download Excel:**  
   Click "Download Excel" to download the same data as an Excel file.

4. **Dark Mode:**  
   Use the toggle switch in the header to switch between light and dark themes.

5. **Loading Spinner:**  
   While fetching or downloading, a spinner appears. You can cancel the operation at any time.

---

## Technical Details

- **Backend:** Python (Flask)
    - Fetches data from the official FPL API.
    - Handles pagination for large leagues.
    - Filters data by the selected gameweek range.
    - Calculates gameweek champions (highest points per gameweek, including ties).
    - Serves data as JSON for display and as an Excel file for download.

- **Frontend:** HTML, CSS, JavaScript
    - Responsive, modern UI with dark mode support.
    - Scrollable, styled tables for large datasets.
    - Custom validation for gameweek input fields.
    - Loading spinner with cancel functionality.

---

## Usage

1. **Run the Flask app:**
    ```sh
    python FplLeague.py
    ```
2. **Open your browser:**  
   Go to `http://localhost:8080` (or the server's IP if deployed).

3. **Enter a league code** (find this on the FPL website), set your desired gameweek range, and use the buttons to fetch or download data.

---

## Notes

- Only public FPL leagues are supported.
- Gameweek values must be whole numbers between 1 and 38.
- The app uses the official FPL API, so data is as up-to-date as the FPL site.

---

## License

This project is for educational and personal use only. Not affiliated with the official Fantasy Premier League.