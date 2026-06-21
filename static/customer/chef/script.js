const statusLabels = {
  NEW: "Accept Order",
  ACCEPTED: "Start Cooking",
  COOKING: "Mark Ready",
  READY: "Mark Served",
};
const nextStatuses = { NEW: "ACCEPTED", ACCEPTED: "COOKING", COOKING: "READY", READY: "SERVED" };

function apiStatusFilter() {
  const page = document.body.dataset.page;
  const status = document.body.dataset.status || "ACTIVE";
  if (page === "orders") return status === "ALL" ? "ALL" : status;
  return "ACTIVE";
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

function renderOrder(order) {
  const items = order.items.map(item => `
    <li>
      <div><strong>${escapeHtml(item.dish_name)}</strong>${item.notes ? `<p class="notes">Note: ${escapeHtml(item.notes)}</p>` : ""}</div>
      <span class="quantity">× ${escapeHtml(item.quantity)}</span>
    </li>`).join("");
  const next = nextStatuses[order.status];
  const action = next ? `<button class="action-button" data-next-status="${next}">${statusLabels[order.status]}</button>` : `<span class="served-label">Completed</span>`;
  return `<article class="order-card status-${order.status.toLowerCase()}" data-order-id="${order.id}" data-status="${order.status}">
    <div class="card-topline"><span class="order-id">Order #${order.id}</span><span class="status-pill">${order.status}</span></div>
    <div class="table-number">Table ${escapeHtml(order.table_number ?? order.table_id)}</div>
    <ul class="item-list">${items}</ul>
    <div class="card-actions">${action}</div>
  </article>`;
}

async function refreshOrders() {
  const grid = document.querySelector("#ordersGrid");
  if (!grid) return;
  const response = await fetch(`/api/chef/orders?status=${encodeURIComponent(apiStatusFilter())}`);
  if (!response.ok) throw new Error("Failed to load orders");
  const data = await response.json();
  grid.innerHTML = data.orders.length ? data.orders.map(renderOrder).join("") : document.querySelector("#emptyTemplate").innerHTML;
}

async function updateStatus(card, status) {
  const button = card.querySelector("button");
  if (button) button.disabled = true;
  const response = await fetch(`/api/chef/order/${card.dataset.orderId}/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    alert(data.error || "Unable to update order status");
  }
  await refreshOrders();
}

document.addEventListener("click", event => {
  const actionButton = event.target.closest("[data-next-status]");
  if (actionButton) {
    event.preventDefault();
    updateStatus(actionButton.closest(".order-card"), actionButton.dataset.nextStatus);
  }
  if (event.target.closest("[data-refresh-orders]")) refreshOrders().catch(error => alert(error.message));
});

setInterval(() => refreshOrders().catch(console.error), 5000);