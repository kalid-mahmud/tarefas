const express = require('express');
const cors = require('cors');
const app = express();
const bodyParser = require('body-parser');

// Importar as rotas
const routes = require('./backend/routes'); // Caminho corrigido!

// Configurar o CORS para permitir requisições do seu frontend no Vercel
app.use(cors({
  origin: 'https://tarefas-sand.vercel.app',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Usar o body-parser para interpretar o corpo das requisições JSON
app.use(bodyParser.json());

// Usar as rotas definidas
app.use('/api', routes);

// Configuração do banco de dados SQLite
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('project.db', err => {
    if (err) {
        console.error('Erro ao conectar ao banco de dados:', err.message);
    } else {
        console.log('Conectado ao banco de dados SQLite.');
    }
});

// A rota raiz
app.get('/', (req, res) => {
    res.send('Servidor rodando!');
});

// Iniciar o servidor na porta 5000
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
});