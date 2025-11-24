// Change this to match current backends host/port
const API_BASE = "http://127.0.0.1:5000";

function getCart() {
    return JSON.parse(localStorage.getItem("cart") || "[]");
}

function saveCart(cart) {
    localStorage.setItem("cart", JSON.stringify(cart));
}

function addToCart(productId, name, price) {
    const cart = getCart();
    const existing = cart.find(i => i.product_id === productId);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({
            product_id: productId,
            name: name,
            price: parseFloat(price),
            quantity: 1
        });
    }
    saveCart(cart);
    alert("Added to cart.");
}

function updateCartQuantity(index, qty) {
    const cart = getCart();
    const q = parseInt(qty, 10);
    cart[index].quantity = isNaN(q) || q <= 0 ? 1 : q;
    saveCart(cart);
    if (typeof renderCart === "function") {
        renderCart();
    }
}

function removeFromCart(index) {
    const cart = getCart();
    cart.splice(index, 1);
    saveCart(cart);
    if (typeof renderCart === "function") {
        renderCart();
    }
}

function clearCart() {
    localStorage.removeItem("cart");
}
