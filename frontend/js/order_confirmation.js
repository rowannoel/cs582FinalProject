// order_confirmation.html?id=###

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    if (!id) {
        const div = document.getElementById("orderDetails");
        if (div) div.innerHTML = "<p>Missing order id.</p>";
        return;
    }
    loadOrder(parseInt(id, 10));
});

async function loadOrder(orderId) {
    const container = document.getElementById("orderDetails");
    if (!container) return;

    try {
        const res = await fetch(`${API_BASE}/api/order/${orderId}`);
        if (!res.ok) {
            container.innerHTML = "<p>Order not found.</p>";
            return;
        }
        const data = await res.json();
        const order = data.order;
        const items = data.items || [];

        let html = `
            <p>Order #${order.id}</p>
            <p>Name: ${order.customer_name}</p>
            <p>Total: $${Number(order.total_amount).toFixed(2)}</p>
            <h3>Items</h3>
            <ul>
        `;
        items.forEach(i => {
            html += `
                <li>${i.name} — ${i.quantity} × $${Number(i.unit_price).toFixed(2)}
                = $${Number(i.line_total).toFixed(2)}</li>
            `;
        });
        html += "</ul>";

        container.innerHTML = html;
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Error loading order.</p>";
    }
}
