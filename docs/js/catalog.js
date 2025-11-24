//Used by index.html

document.addEventListener("DOMContentLoaded", () => {
    loadProducts();
});

async function loadProducts() {
    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");
    const search = searchInput ? searchInput.value : "";
    const category = categoryFilter ? categoryFilter.value : "";

    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (category) params.append("category", category);

    try {
        const res = await fetch(`${API_BASE}/api/products?` + params.toString());
        if (!res.ok) {
            throw new Error("Network response was not ok");
        }
        const products = await res.json();
        renderProductList(products);
    } catch (err) {
        console.error(err);
        const list = document.getElementById("productList");
        if (list) list.innerHTML = "<p>Error loading products.</p>";
    }
}

function renderProductList(products) {
    const list = document.getElementById("productList");
    if (!list) return;

    list.innerHTML = "";

    if (!products || products.length === 0) {
        list.innerHTML = "<p>No products found.</p>";
        return;
    }

    products.forEach(p => {
        const div = document.createElement("div");
        div.className = "product-card";
        const safeName = (p.name || "").replace(/"/g, "&quot;");
        div.innerHTML = `
            <h3><a href="product.html?id=${p.id}">${safeName}</a></h3>
            <p>${p.description || ""}</p>
            <p><strong>$${Number(p.price).toFixed(2)}</strong></p>
            <button onclick="addToCart(${p.id}, '${safeName.replace(/'/g, "\\'")}', ${Number(p.price)})">
                Add to Cart
            </button>
        `;
        list.appendChild(div);
    });
}