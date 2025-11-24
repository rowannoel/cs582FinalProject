//Used by product.html?id=###

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    if (!id) {
        const div = document.getElementById("productDetail");
        if (div) div.innerHTML = "<p>Missing product id.</p>";
        return;
    }
    loadProduct(parseInt(id, 10));
});

async function loadProduct(id) {
    const container = document.getElementById("productDetail");
    if (!container) return;

    try {
        const res = await fetch(`${API_BASE}/api/products/${id}`);
        if (!res.ok) {
            container.innerHTML = "<p>Product not found.</p>";
            return;
        }
        const p = await res.json();
        const safeName = (p.name || "").replace(/"/g, "&quot;");
        container.innerHTML = `
            <h2>${safeName}</h2>
            <p>${p.description || ""}</p>
            <p>Category: ${p.category || "N/A"}</p>
            <p><strong>Price: $${Number(p.price).toFixed(2)}</strong></p>
            <button onclick="addToCart(${p.id}, '${safeName.replace(/'/g, "\\'")}', ${Number(p.price)})">
                Add to Cart
            </button>
        `;
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Error loading product.</p>";
    }
}
