// data_tools.html
// Auto-detect backend API location
const API_BASE = (() => {
    // Local HTML server
    if (window.location.origin.includes("localhost:8000")) {
        return "http://127.0.0.1:5000";
    }
    // GitHub Pages (production)
    return "https://rowannoel.github.io/cs582FinalProject";
})();

async function checkOrderTotals() {
    const statusDiv = document.getElementById("orderTotalsStatus");
    try {
        const res = await fetch(`${API_BASE}/api/tools/check-order-totals`);
        const data = await res.json();

        if (data.errors && data.errors.length > 0) {
            let html = `<p style="color: red;">⚠️ Found ${data.errors.length} orders with incorrect totals:</p><ul>`;
            data.errors.forEach(err => {
                html += `<li>Order #${err.order_id}: Stored = $${err.stored_total}, Should be = $${err.correct_total}</li>`;
            });
            html += "</ul>";
            statusDiv.innerHTML = html;
        } else {
            statusDiv.innerHTML = '<p style="color: green;">✓ All order totals are correct!</p>';
        }
    } catch (err) {
        console.error(err);
        statusDiv.innerHTML = "<p>Error checking order totals.</p>";
    }
}

async function recomputeTotals() {
    const resultDiv = document.getElementById("toolsResult");

    // Show before state
    await checkOrderTotals();

    try {
        const res = await fetch(`${API_BASE}/api/tools/recompute-order-totals`, {
            method: "POST"
        });
        const data = await res.json();
        if (resultDiv) {
            resultDiv.innerHTML = `<p style="color: green;">${data.message || "Recomputed order totals."}</p>`;
        }

        // Show after state
        setTimeout(checkOrderTotals, 500);
    } catch (err) {
        console.error(err);
        if (resultDiv) {
            resultDiv.innerText = "Error recomputing order totals.";
        }
    }
}

async function refreshSummary() {
    const beforeDiv = document.getElementById("summaryBefore");
    const afterDiv = document.getElementById("summaryAfter");
    const resultDiv = document.getElementById("toolsResult");

    try {
        // Get summary before
        const beforeRes = await fetch(`${API_BASE}/api/tools/get-90day-summary`);
        const beforeData = await beforeRes.json();
        if (beforeDiv) {
            beforeDiv.innerHTML = `<p><strong>Before:</strong> ${beforeData.order_count} orders, $${beforeData.total_revenue} revenue</p>`;
        }

        // Refresh
        const res = await fetch(`${API_BASE}/api/tools/refresh-90day-summary`, {
            method: "POST"
        });
        const data = await res.json();

        // Get summary after
        const afterRes = await fetch(`${API_BASE}/api/tools/get-90day-summary`);
        const afterData = await afterRes.json();
        if (afterDiv) {
            afterDiv.innerHTML = `<p><strong>After:</strong> ${afterData.order_count} orders, $${afterData.total_revenue} revenue</p>`;
        }

        if (resultDiv) {
            resultDiv.innerHTML = `<p style="color: green;">${data.message}</p>`;
        }
    } catch (err) {
        console.error(err);
        if (resultDiv) {
            resultDiv.innerText = "Error refreshing 90-day summary.";
        }
    }
}
