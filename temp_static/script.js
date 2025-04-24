

function showSpinner() {
    document.getElementById("loading-spinner").style.display = "flex";
}
function hideSpinner() {
    document.getElementById("loading-spinner").style.display = "none";
}



let currentController = null;


document.getElementById("download-btn").addEventListener("click", async () => {
    const leagueCode = document.getElementById("league_code").value;
    const startGameweek = document.getElementById("start_gameweek").value;
    const endGameweek = document.getElementById("end_gameweek").value;
    const loadingSpinner = document.getElementById("loading-spinner");

    if (!leagueCode) {
        alert("Please provide a league code.");
        return;
    }

    const formData = new FormData();
    formData.append("league_code", leagueCode);
    if (startGameweek) formData.append("start_gameweek", startGameweek);
    if (endGameweek) formData.append("end_gameweek", endGameweek);
    currentController = new AbortController();
    try {
        showSpinner();
        const response = await fetch("/download", {
            method: "POST",
            body: formData,
            signal: currentController.signal
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = `league_${leagueCode}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const errorData = await response.json();
            alert(errorData.error || "An error occurred while downloading the file.");
        }
    } catch (error) {
        if (error.name === "AbortError") {
            alert("Download cancelled.");
        } else {
            console.error("Error downloading file:", error);
            alert("Failed to download file. Please try again.");
        }
    } finally {
        hideSpinner();
        currentController = null;
    }
});

function isWholeNumber(n) {
    return Number.isInteger(n);
}


document.getElementById("fetch-form").addEventListener("submit", function(e) {
    const start = parseFloat(document.getElementById("start_gameweek").value);
    const end = parseFloat(document.getElementById("end_gameweek").value);
    if (
        (start && (!isWholeNumber(start) || start < 1 || start > 38)) ||
        (end && (!isWholeNumber(end) || end < 1 || end > 38))
    ) {
        alert("Gameweek values must be whole numbers between 1 and 38.");
        e.preventDefault();
    }
});

document.getElementById("display-btn").addEventListener("click", async () => {
    const leagueCode = document.getElementById("league_code").value;
    const startGameweek = document.getElementById("start_gameweek").value;
    const endGameweek = document.getElementById("end_gameweek").value;
    const loadingSpinner = document.getElementById("loading-spinner");

    if (!leagueCode) {
        alert("Please provide a league code.");
        return;
    }

    const formData = new FormData();
    formData.append("league_code", leagueCode);
    if (startGameweek) formData.append("start_gameweek", startGameweek);
    if (endGameweek) formData.append("end_gameweek", endGameweek);

    currentController = new AbortController();
    try {
        showSpinner();
        const response = await fetch("/fetch_data", {
            method: "POST",
            body: formData,
            signal: currentController.signal
        });

        if (!response.ok) {
            const errorData = await response.json();
            alert(errorData.error || "An error occurred while fetching data.");
            return;
        }

        const data = await response.json();
        displayLeagueData(data.league_data);
        displayChampionsData(data.champions_data);

        document.getElementById("table-container").style.display = "block";
        document.getElementById("champions-table-container").style.display = "block";
    } catch (error) {
        if (error.name === "AbortError") {
            alert("Fetch cancelled.");
        } else {
            console.error("Error fetching data:", error);
            alert("Failed to fetch data. Please try again.");
        }
    } finally {
        hideSpinner();
        currentController = null;
    }

});
function displayLeagueData(leagueData) {
    const tableHeaders = document.getElementById("table-headers");
    const tableBody = document.getElementById("table-body");

    tableHeaders.innerHTML = "";
    tableBody.innerHTML = "";

    if (!Array.isArray(leagueData) || leagueData.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='100%'>No data available.</td></tr>";
        return;
    }

    // Create headers
    const headers = Object.keys(leagueData[0]);
    headers.forEach(header => {
        const th = document.createElement("th");
        th.textContent = header;
        tableHeaders.appendChild(th);
    });

    // Create rows
    leagueData.forEach(row => {
        const tr = document.createElement("tr");
        headers.forEach(header => {
            const td = document.createElement("td");
            td.textContent = row[header];
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

function displayChampionsData(championsData) {
    const championsTableBody = document.getElementById("champions-table-body");
    championsTableBody.innerHTML = "";

    if (!Array.isArray(championsData) || championsData.length === 0) {
        championsTableBody.innerHTML = "<tr><td colspan='3'>No data available.</td></tr>";
        return;
    }

    championsData.forEach(row => {
        const tr = document.createElement("tr");
        ["Gameweek", "Champion(s)", "Points"].forEach(header => {
            const td = document.createElement("td");
            td.textContent = row[header];
            tr.appendChild(td);
        });
        championsTableBody.appendChild(tr);
    });
}

// Cancel button logic
document.getElementById("cancel-spinner-btn").addEventListener("click", () => {
    if (currentController) currentController.abort();
    hideSpinner();
});


const toggle = document.getElementById("dark-mode-toggle");
toggle.addEventListener("change", () => {
    document.body.classList.toggle("dark-mode", toggle.checked);
});
