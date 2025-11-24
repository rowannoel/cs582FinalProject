//Used by cart.html

document.addEventListener("DOMContentLoaded", () => {
    renderCart();
    const form = document.getElementById("checkoutForm");
    if (form) {
        form.addEventListener("submit", submitOrder);
    }
});

function renderCart() {
    const cart = getCart();
    const container = document.getElementById("cartItems");
    const totalEl = document.getElementById("cartTotal");
    if (!container || !totalEl) return;

    container.innerHTML = "";
    let total = 0;

    if (cart.length === 0) {
        container.innerHTML = "<p>Your cart is empty.</p>";
        totalEl.innerText = "";
        return;
    }

    cart.forEach((item, index) => {
        const price = Number(item.price);
        const quantity = Number(item.quantity);
        const lineTotal = price * quantity;
        total += lineTotal;

        const div = document.createElement("div");
        div.className = "cart-item";
        div.innerHTML = `
            <span class="cart-name">${item.name}</span>
            <span class="cart-price">$${price.toFixed(2)}</span>
            <input type="number" min="1" value="${quantity}"
                   onchange="updateCartQuantity(${index}, this.value)">
            <span class="cart-line">$${lineTotal.toFixed(2)}</span>
            <button onclick="removeFromCart(${index})">Remove</button>
        `;
        container.appendChild(div);
    });

    totalEl.innerText = "Cart Total: $" + total.toFixed(2);
}

async function submitOrder(event) {
    event.preventDefault();
    const cart = getCart();
    if (cart.length === 0) {
        alert("Your cart is empty.");
        return;
    }

    const form = event.target;
    const customer = {
        name: form.name.value.trim(),
        email: form.email.value.trim(),
        address: form.address.value.trim(),
        city: form.city.value.trim(),
        state: form.state.value.trim(),
        zip: form.zip.value.trim()
    };

    if (!customer.name) {
        alert("Name is required.");
        return;
    }

    const payload = {
        customer: customer,
        items: cart
    };

    try {
        const res = await fetch(`${API_BASE}/api/order`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            alert("Error placing order.");
            return;
        }

        const data = await res.json();
        const orderId = data.order_id;
        clearCart();
        window.location.href = `order_confirmation.html?id=${orderId}`;
    } catch (err) {
        console.error(err);
        alert("Error connecting to server.");
    }
}
