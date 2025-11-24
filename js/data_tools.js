// data_tools.html

async function recomputeTotals() {
    const resultDiv = document.getElementById("toolsResult");
    try {
        const res = await fetch(`${API_BASE}/api/tools/recompute-order-totals`, {
            method: "POST"
        });
        const data = await res.json();
        if (resultDiv) {
            resultDiv.innerText = data.message || "Recomputed order totals.";
        }
    } catch (err) {
        console.error(err);
        if (resultDiv) {
            resultDiv.innerText = "Error recomputing order totals.";
        }
    }
}

async function refreshSummary() {
    const resultDiv = document.getElementById("toolsResult");
    try {
        const res = await fetch(`${API_BASE}/api/tools/refresh-90day-summary`, {
            method: "POST"
        });
        const data = await res.json();
        if (resultDiv) {
            resultDiv.innerText = data.message || "Refreshed 90-day summary.";
        }
    } catch (err) {
        console.error(err);
        if (resultDiv) {
            resultDiv.innerText = "Error refreshing 90-day summary.";
        }
    }
}
