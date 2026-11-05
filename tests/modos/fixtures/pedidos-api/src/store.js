// In-memory store. Data is lost on restart.
const orders = new Map();
let nextId = 1;

const STATUSES = ['pending', 'paid', 'shipped', 'cancelled'];

function list({ status } = {}) {
  const all = [...orders.values()];
  return status ? all.filter((o) => o.status === status) : all;
}

function get(id) {
  return orders.get(Number(id));
}

function create({ customer, items }) {
  const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
  const order = { id: nextId++, customer, items, total, status: 'pending', createdAt: new Date().toISOString() };
  orders.set(order.id, order);
  return order;
}

function setStatus(id, status) {
  const order = get(id);
  if (!order) return null;
  if (!STATUSES.includes(status)) throw new Error(`invalid status: ${status}`);
  order.status = status;
  return order;
}

function reset() {
  orders.clear();
  nextId = 1;
}

module.exports = { list, get, create, setStatus, reset, STATUSES };
