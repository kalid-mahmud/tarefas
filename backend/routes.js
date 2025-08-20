const express = require('express');
const routes = express.Router();

// Rota de teste
routes.get('/', (req, res) => {
    return res.send('Servidor rodando e pronto para receber requisições!');
});

module.exports = routes;