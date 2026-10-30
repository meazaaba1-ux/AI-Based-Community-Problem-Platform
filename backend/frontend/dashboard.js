
const API_URL = "http://127.0.0.1:8000";

// --------------------------------------------------
// LOAD LOGGED-IN USER'S REPORTS
// --------------------------------------------------

async function loadReports() {

    const container = document.getElementById("reportsContainer");

    const userId = localStorage.getItem("user_id");

    // Check login
    if (!userId) {
        window.location.href = "login.html";
        return;
    }

    try {

        // Get only this user's reports
        const response = await fetch(
            `${API_URL}/problems?user_id=${encodeURIComponent(userId)}`
        );

        if (!response.ok) {
            throw new Error("Failed to load reports");
        }

        const reports = await response.json();

        // ------------------------------------------
        // STATISTICS
        // ------------------------------------------

        document.getElementById("totalReports").textContent =
            reports.length;

        const pending = reports.filter(
            report => report.status === "pending"
        ).length;

        const resolved = reports.filter(
            report => report.status === "resolved"
        ).length;

        document.getElementById("pendingReports").textContent =
            pending;

        document.getElementById("resolvedReports").textContent =
            resolved;

        // ------------------------------------------
        // DISPLAY REPORTS
        // ------------------------------------------

        if (reports.length === 0) {

            container.innerHTML =
                '<p class="empty-message">No reports yet.</p>';

            return;
        }

        container.innerHTML = "";

        reports.forEach(report => {

            const card = document.createElement("div");

            card.className = "report-item";

            const title = document.createElement("h3");
            title.textContent = report.title || "Untitled report";

            const description = document.createElement("p");
            description.textContent = report.description || "";

            const location = document.createElement("p");
            location.textContent =
                "Location: " + (report.location || "Not provided");

            const category = document.createElement("p");
            category.textContent =
                "Category: " + (report.category || "Unclassified");

            const status = document.createElement("span");
            status.className = "status";

            const reportStatus = report.status || "pending";

            status.textContent =
                "Status: " + reportStatus.replace("_", " ");

            if (reportStatus === "resolved") {
                status.classList.add("resolved");
            }

            if (reportStatus === "in_progress") {
                status.classList.add("in-progress");
            }

            card.appendChild(title);
            card.appendChild(description);
            card.appendChild(location);
            card.appendChild(category);
            card.appendChild(status);

            container.appendChild(card);

        });

    } catch (error) {

        console.error("Dashboard reports error:", error);

        container.innerHTML =
            '<p class="empty-message">Unable to load your reports. Please check that the backend is running.</p>';
    }
}


// --------------------------------------------------
// REPORT A PROBLEM
// --------------------------------------------------

function reportProblem() {

    const userId = localStorage.getItem("user_id");

    if (!userId) {
        alert("Please login first.");
        window.location.href = "login.html";
        return;
    }

    window.location.href = "report.html";
}


// --------------------------------------------------
// LOGOUT
// --------------------------------------------------

function logout() {

    localStorage.removeItem("user_id");
    localStorage.removeItem("name");
    localStorage.removeItem("email");
    localStorage.removeItem("role");
    localStorage.removeItem("access_token");

    window.location.href = "login.html";
}


// --------------------------------------------------
// LOAD DASHBOARD
// --------------------------------------------------

loadReports();
