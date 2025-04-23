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

    try {
        // Show the spinner
        loadingSpinner.style.display = "flex";

        const response = await fetch("/download", {
            method: "POST",
            body: formData,
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
        console.error("Error downloading file:", error);
        alert("Failed to download file. Please try again.");
    } finally {
        // Hide the spinner
        loadingSpinner.style.display = "none";
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

    try {
        // Show the spinner
        loadingSpinner.style.display = "flex";

        const response = await fetch("/fetch_data", {
            method: "POST",
            body: formData,
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
        console.error("Error fetching data:", error);
        alert("Failed to fetch data. Please try again.");
    } finally {
        // Hide the spinner
        loadingSpinner.style.display = "none";
    }
});

function displayLeagueData(leagueData) {
    const tableHeaders = document.getElementById("table-headers");
    const tableBody = document.getElementById("table-body");

    tableHeaders.innerHTML = "";
    tableBody.innerHTML = "";

    if (leagueData.length === 0) return;

    Object.keys(leagueData[0]).forEach((header) => {
        const th = document.createElement("th");
        th.textContent = header;
        tableHeaders.appendChild(th);
    });

    leagueData.forEach((row) => {
        const tr = document.createElement("tr");
        Object.values(row).forEach((value) => {
            const td = document.createElement("td");
            td.textContent = value;
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

function displayChampionsData(championsData) {
    const championsTableBody = document.getElementById("champions-table-body");

    championsTableBody.innerHTML = "";

    championsData.forEach((row) => {
        const tr = document.createElement("tr");
        Object.values(row).forEach((value) => {
            const td = document.createElement("td");
            td.textContent = value;
            tr.appendChild(td);
        });
        championsTableBody.appendChild(tr);
    });
}

const toggle = document.getElementById("dark-mode-toggle");
toggle.addEventListener("change", () => {
    document.body.classList.toggle("dark-mode", toggle.checked);
});
