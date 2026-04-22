const express = require('express');
const axios = require('axios');
const path = require('path');
 
const app = express();
const API_URL = process.env.API_URL || "http://api:8000";
 
app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});
 
app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`);
    res.status(response.status).json(response.data);
  } catch (err) {    
    if (err.response) {
      res.status(err.response.status).json(err.response.data);
    } else {
      res.status(502).json({ error: "Could not reach API", detail: err.message });
    }
  }
});
 
app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`);
    res.status(response.status).json(response.data);
  } catch (err) {
    if (err.response) {
      res.status(err.response.status).json(err.response.data);
    } else {
      res.status(502).json({ error: "Could not reach API", detail: err.message });
    }
  }
});
 
app.listen(3000, () => {
  console.log('Frontend running on port 3000');
});
 


