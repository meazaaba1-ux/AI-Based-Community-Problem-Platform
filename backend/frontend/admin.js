
const API_URL = "http://127.0.0.1:8000";

const reportsTable = document.getElementById("reportsTable");
const message = document.getElementById("message");

async function loadReports() {
    message.textContent = "Loading reports...";
    reportsTable.innerHTML = "";

    try {
        const response = await fetch(`${API_URL}/problems`);

        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const reports = await response.json();

        // Update dashboard summary cards.
        document.getElementById("totalReports").textContent =
            reports.length;

        document.getElementById("pendingReports").textContent =
            reports.filter(report =>
                String(report.status).toLowerCase() === "pending"
            ).length;

        document.getElementById("resolvedReports").textContent =
            reports.filter(report =>
                String(report.status).toLowerCase() === "resolved"
            ).length;

        if (reports.length === 0) {
            message.textContent = "No community reports found.";
            return;
        }

        reports.forEach(report => {
            const row = document.createElement("tr");

            // Report ID
            const idCell = document.createElement("td");
            idCell.textContent = report.id;

            // Report title
            const titleCell = document.createElement("td");
            titleCell.textContent = report.title;

            // Report location
            const locationCell = document.createElement("td");
            locationCell.textContent = report.location;

            // AI-predicted category
            const categoryCell = document.createElement("td");
            categoryCell.textContent =
                report.category || "Not classified";

            // Report status
            const statusCell = document.createElement("td");
            statusCell.textContent = report.status;

            // Status update dropdown
            const actionCell = document.createElement("td");
            const statusSelect = document.createElement("select");

            ["pending", "in_progress", "resolved"].forEach(status => {
                const option = document.createElement("option");

                option.value = status;
                option.textContent = status;

                if (status === report.status) {
                    option.selected = true;
                }

                statusSelect.appendChild(option);
            });

            statusSelect.addEventListener("change", async () => {
                const newStatus = statusSelect.value;

                statusSelect.disabled = true;

                try {
                    const updateResponse = await fetch(
                        `${API_URL}/problems/${report.id}/status?status=${encodeURIComponent(newStatus)}`,
                        { method: "PATCH" }
                    );

                    const data = await updateResponse.json();

                    if (!updateResponse.ok) {
                        throw new Error(
                            data.detail || "Could not update status"
                        );
                    }

                    message.textContent =
                        `Report #${report.id} status updated to ${data.status}.`;

                    // Reload reports and summary cards.
                    await loadReports();

                } catch (error) {
                    alert("Status update failed: " + error.message);
                    await loadReports();
                }
            });

            actionCell.appendChild(statusSelect);

            // Add all six columns to the row.
            row.append(
                idCell,
                titleCell,
                locationCell,
                categoryCell,
                statusCell,
                actionCell
            );

            reportsTable.appendChild(row);
        });

        message.textContent =
            `Loaded ${reports.length} report(s) successfully.`;

    } catch (error) {
        console.error("Error loading reports:", error);

        message.textContent =
            "Unable to load reports. Check that the backend is running.";
    }
}

loadReports();
