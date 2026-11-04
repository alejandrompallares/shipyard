const test = require('node:test');
const assert = require('node:assert');
const store = require('../src/store');

test('create computes total and starts pending', () => {
  store.reset();
  const o = store.create({ customer: 'Cliente de prueba', items: [{ sku: 'A', price: 5, qty: 2 }] });
  assert.equal(o.total, 10);
  assert.equal(o.status, 'pending');
});

test('setStatus rejects unknown status', () => {
  store.reset();
  const o = store.create({ customer: 'Cliente de prueba', items: [{ sku: 'A', price: 1, qty: 1 }] });
  assert.throws(() => store.setStatus(o.id, 'lost'));
});
