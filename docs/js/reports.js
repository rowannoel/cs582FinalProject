//Used by reports.html (with Chart.js CDN loaded in the HTML).

let salesChart = null;

document.addEventListener("DOMContentLoaded", () => {
    const daysSelect = document.getElementById("topProductsDays");
    if (daysSelect) {
        daysSelect.addEventListener("change", loadTopProducts);
    }
    loadTopProducts();
    loadDailySales();
    loadLowStock();
});

async function loadTopProducts() {
    const daysSelect = document.getElementById("topProductsDays");
    const days = daysSelect ? daysSelect.value : "30";

    try {
        const res = await fetch(`${API_BASE}/api/reports/top-products?days=${days}`);
        if (!res.ok) throw new Error("Failed to fetch top products");
        const rows = await res.json();

        const tbody = document.querySelector("#topProductsTable tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        if (!rows || rows.length === 0) {
            tbody.innerHTML = "<tr><td colspan='2'>No data.</td></tr>";
            return;
        }

        rows.forEach(r => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${r.name}</td>
                <td>$${Number(r.revenue).toFixed(2)}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

async function loadDailySales() {
    try {
        const res = await fetch(`${API_BASE}/api/reports/daily-sales?days=90`);
        if (!res.ok) throw new Error("Failed to fetch daily sales");
        const data = await res.json();

        const ctx = document.getElementById("salesChart");
        if (!ctx) return;

        if (salesChart) {
            salesChart.destroy();
        }

        salesChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: data.dates,
                datasets: [
                    {
                        label: "Daily Revenue",
                        data: data.revenues,
                        fill: false
                    },
                    {
                        label: "7-Day Moving Avg",
                        data: data.moving_avg,
                        fill: false
                    }
                ]
            }
        });
    } catch (err) {
        console.error(err);
    }
}

async function loadLowStock() {
    const container = document.getElementById("lowStockWarnings");
    if (!container) return;

    try {
        const res = await fetch(`${API_BASE}/api/reports/low-stock`);
        if (!res.ok) throw new Error("Failed to fetch low stock");
        const rows = await res.json();

        if (!rows || rows.length === 0) {
            container.innerHTML = "<p>No low-stock items.</p>";
            return;
        }

        let html = "<ul>";
        rows.forEach(p => {
            html += `<li>⚠️ ${p.name} — ${p.stock_quantity} left (reorder level: ${p.reorder_level})</li>`;
        });
        html += "</ul>";
        container.innerHTML = html;
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Error loading low-stock report.</p>";
    }
}
