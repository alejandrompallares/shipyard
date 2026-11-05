const { Router } = require('express');
const store = require('../store');

const router = Router();

router.get('/', (req, res) => {
  res.json(store.list({ status: req.query.status }));
});

router.get('/:id', (req, res) => {
  const order = store.get(req.params.id);
  if (!order) return res.status(404).json({ error: 'not found' });
  res.json(order);
});

router.post('/', (req, res) => {
  const { customer, items } = req.body || {};
  if (!customer || !Array.isArray(items) || items.length === 0) {
    return res.status(400).json({ error: 'customer and items are required' });
  }
  res.status(201).json(store.create({ customer, items }));
});

router.patch('/:id/status', (req, res) => {
  try {
    const order = store.setStatus(req.params.id, req.body.status);
    if (!order) return res.status(404).json({ error: 'not found' });
    res.json(order);
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

module.exports = router;
