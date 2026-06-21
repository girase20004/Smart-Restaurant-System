const tableNumber = document.body.dataset.tableNumber;
const cartKey = `sroms-cart-${tableNumber}`;
const money = (value) => `₹${Number(value || 0).toFixed(2)}`;
const getCart = () => JSON.parse(sessionStorage.getItem(cartKey) || '[]');
const saveCart = (cart) => { sessionStorage.setItem(cartKey, JSON.stringify(cart)); updateCartCount(); };

function updateCartCount(){
  const count = getCart().reduce((sum,item)=>sum + item.quantity,0);
  document.querySelectorAll('#cart-count').forEach((el)=>{ el.textContent = count; });
}

function addToCart(menuId, name, price){
  const cart = getCart();
  const item = cart.find((entry)=>entry.menu_id === Number(menuId) && !entry.notes);
  if(item){ item.quantity += 1; } else { cart.push({menu_id:Number(menuId), name, price:Number(price), quantity:1, notes:''}); }
  saveCart(cart);
  alert(`${name} added to cart`);
}

function renderCart(){
  const container = document.getElementById('cart-items');
  if(!container) return;
  const cart = getCart();
  if(!cart.length){ container.innerHTML = '<p class="muted">Your cart is empty. Add delicious items from the menu.</p>'; }
  else{
    container.innerHTML = cart.map((item,index)=>`
      <div class="cart-item">
        <div class="cart-row"><strong>${item.name}</strong><span>${money(item.price * item.quantity)}</span></div>
        <div class="cart-row">
          <div class="qty-controls"><button data-dec="${index}">−</button><span>${item.quantity}</span><button data-inc="${index}">+</button></div>
          <button class="secondary" data-remove="${index}">Remove</button>
        </div>
        <input class="note" data-note="${index}" value="${item.notes || ''}" placeholder="Cooking notes: No onion, Less spicy">
      </div>`).join('');
  }
  updateTotals();
}

function updateTotals(){
  const cart = getCart();
  const subtotal = cart.reduce((sum,item)=>sum + item.price * item.quantity,0);
  const gst = subtotal * 0.05;
  const total = subtotal + gst;
  const set = (id,value)=>{ const el=document.getElementById(id); if(el) el.textContent = money(value); };
  set('subtotal', subtotal); set('gst', gst); set('total', total);
}

async function loadRunningBill(){
  const target = document.getElementById('running-bill');
  if(!target || !tableNumber) return;
  const response = await fetch(`/customer/${tableNumber}/bill`);
  const data = await response.json();
  const bill = data.bill || {items:[], total:0};
  if(!bill.items.length){ target.innerHTML = '<p class="muted">No active bill yet.</p>'; return; }
  target.innerHTML = `${bill.items.map((item)=>`<div class="bill-line"><span>${item.dish_name} × ${item.quantity}</span><strong>${money(item.line_total)}</strong></div>`).join('')}<div class="bill-line"><span>GST</span><strong>${money(bill.gst)}</strong></div><div class="bill-line"><span>Total</span><strong>${money(bill.total)}</strong></div>`;
}

async function placeOrder(){
  const message = document.getElementById('order-message');
  const cart = getCart();
  if(!cart.length){ if(message) message.textContent='Your cart is empty.'; return; }
  const response = await fetch('/customer/place_order', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({table_number:tableNumber, items:cart.map(({menu_id,quantity,notes})=>({menu_id,quantity,notes}))})});
  const data = await response.json();
  if(!response.ok){ if(message) message.textContent=data.message || 'Unable to place order.'; return; }
  saveCart([]); renderCart(); await loadRunningBill();
  if(message) message.textContent = `Order placed successfully. Current total ${money(data.bill.total)}.`;
}

document.addEventListener('click', (event)=>{
  const addButton = event.target.closest('[data-add-to-cart]');
  if(addButton) addToCart(addButton.dataset.menuId, addButton.dataset.name, addButton.dataset.price);
  const cart = getCart();
  if(event.target.matches('[data-inc]')){ cart[event.target.dataset.inc].quantity += 1; saveCart(cart); renderCart(); }
  if(event.target.matches('[data-dec]')){ const item=cart[event.target.dataset.dec]; item.quantity=Math.max(1,item.quantity-1); saveCart(cart); renderCart(); }
  if(event.target.matches('[data-remove]')){ cart.splice(event.target.dataset.remove,1); saveCart(cart); renderCart(); }
  if(event.target.id === 'place-order') placeOrder();
});

document.addEventListener('input', (event)=>{
  if(event.target.matches('[data-note]')){ const cart=getCart(); cart[event.target.dataset.note].notes=event.target.value; saveCart(cart); }
});

updateCartCount();
renderCart();
loadRunningBill();