// Carrega as variáveis de ambiente do arquivo .env
require('dotenv').config();

const express = require('express');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const { Sequelize, DataTypes, Op } = require('sequelize');
const bcrypt = require('bcryptjs');
const nodemailer = require('nodemailer');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 5000;
const SECRET_KEY = 'sua_chave_secreta';

// Configuração do Sequelize e conexão com o banco de dados SQLite
const sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: 'database.sqlite'
});

// Configuração do Nodemailer com as credenciais do SendGrid
const transporter = nodemailer.createTransport({
    host: 'smtp.sendgrid.net',
    port: 587,
    secure: false, // Use TLS
    auth: {
        user: 'apikey',
        pass: process.env.SENDGRID_API_KEY, // Usa a variável de ambiente para segurança
    },
});

// Definição do modelo de usuário, agora com campo de e-mail e token
const User = sequelize.define('User', {
    username: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true
    },
    password: {
        type: DataTypes.STRING,
        allowNull: false
    },
    role: {
        type: DataTypes.STRING,
        allowNull: false
    },
    email: { 
        type: DataTypes.STRING,
        allowNull: false,
        unique: true
    },
    resetPasswordToken: { 
        type: DataTypes.STRING,
        allowNull: true
    },
    resetPasswordExpires: { 
        type: DataTypes.DATE,
        allowNull: true
    }
});

// Função para popular o banco de dados com usuários iniciais
const populateDb = async () => {
    try {
        await User.sync({ force: false }); // Mantém a tabela se já existir
        const count = await User.count();
        if (count === 0) {
            const initialUsers = [
                { username: 'admin_geral', password: 'admin123', role: 'admin', email: 'admin@example.com' },
                { username: 'joao_silva', password: 'joao123', role: 'editor', email: 'joao@example.com' },
                { username: 'maria_ferreira', password: 'maria123', role: 'reader', email: 'maria@example.com' }
            ];
            for (const user of initialUsers) {
                user.password = bcrypt.hashSync(user.password, 10);
            }
            await User.bulkCreate(initialUsers);
            console.log('Banco de dados populado com usuários iniciais.');
        }
    } catch (error) {
        console.error('Erro ao popular o banco de dados:', error);
    }
};

// Middleware
app.use(cors());
app.use(express.json());

// Rota de login
app.post('/api/login', async (req, res) => {
    console.log('Recebendo solicitação de login...'); // Ponto de depuração 1

    const { username, password } = req.body;
    
    try {
        const user = await User.findOne({ where: { username } }); 

        if (user && bcrypt.compareSync(password, user.password)) {
            console.log('Login bem-sucedido!'); // Ponto de depuração 2
            const token = jwt.sign({ username: user.username, role: user.role }, SECRET_KEY, { expiresIn: '1h' });
            return res.json({ token });
        }
        
        console.log('Login falhou. Credenciais inválidas.'); // Ponto de depuração 3
        return res.status(401).json({ error: 'Credenciais inválidas' });

    } catch (error) {
        console.error('Erro no processamento do login:', error); // Ponto de depuração 4
        return res.status(500).json({ error: 'Ocorreu um erro interno. Tente novamente.' });
    }
});

// Rota para solicitar redefinição de senha
app.post('/api/reset-password-request', async (req, res) => {
    const { email } = req.body;
    const user = await User.findOne({ where: { email } });

    if (!user) {
        return res.status(404).json({ error: 'Nenhum usuário encontrado com este e-mail.' });
    }

    const resetToken = uuidv4();
    const tokenExpires = Date.now() + 3600000; // Token expira em 1 hora

    await User.update({
        resetPasswordToken: resetToken,
        resetPasswordExpires: tokenExpires
    }, {
        where: { email }
    });

    const resetUrl = `http://localhost:5173/redefinir-senha?token=${resetToken}`;

    const mailOptions = {
        to: user.email,
        from: "kalidcpd@hotmail.com", // E-mail verificado no SendGrid
        subject: 'Redefinição de Senha',
        html: `
            <h1>Redefinição de Senha</h1>
            <p>Você solicitou uma redefinição de senha. Clique no link abaixo para criar uma nova senha:</p>
            <a href="${resetUrl}">${resetUrl}</a>
            <p>Este link expira em 1 hora.</p>
        `
    };

    try {
        await transporter.sendMail(mailOptions);
        res.status(200).json({ message: 'E-mail de redefinição enviado com sucesso.' });
    } catch (error) {
        console.error('Erro ao enviar e-mail:', error);
        res.status(500).json({ error: 'Erro ao enviar e-mail de redefinição.' });
    }
});

// Rota para redefinir a senha
app.post('/api/reset-password', async (req, res) => {
    const { token, newPassword } = req.body;

    const user = await User.findOne({
        where: {
            resetPasswordToken: token,
            resetPasswordExpires: { [Op.gt]: Date.now() }
        }
    });

    if (!user) {
        return res.status(400).json({ error: 'Token inválido ou expirado.' });
    }

    const hashedPassword = bcrypt.hashSync(newPassword, 10);
    await user.update({
        password: hashedPassword,
        resetPasswordToken: null,
        resetPasswordExpires: null
    });

    res.status(200).json({ message: 'Senha atualizada com sucesso.' });
});

// Middleware de verificação de token
const tokenVerification = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(403).json({ error: 'Token não fornecido' });
    }

    jwt.verify(token, SECRET_KEY, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Token inválido' });
        }
        req.user = user;
        next();
    });
};

// Rotas protegidas (todas usando o banco de dados agora)
app.get('/api/user', tokenVerification, async (req, res) => {
    const loggedInUser = await User.findOne({ where: { username: req.user.username } });
    res.json({ username: loggedInUser.username, role: loggedInUser.role });
});

app.get('/api/users', tokenVerification, async (req, res) => {
    const users = await User.findAll({ attributes: ['username', 'role', 'email'] });
    res.json(users);
});

app.post('/api/users', tokenVerification, async (req, res) => {
    if (req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Acesso negado. Apenas administradores podem criar usuários.' });
    }

    const { username, password, role, email } = req.body;

    if (!username || !password || !role || !email) {
        return res.status(400).json({ error: 'Todos os campos são obrigatórios.' });
    }

    try {
        const hashedPassword = bcrypt.hashSync(password, 10);
        const newUser = await User.create({ username, password: hashedPassword, role, email });
        res.status(201).json({ message: 'Usuário criado com sucesso.', user: newUser });
    } catch (error) {
        if (error.name === 'SequelizeUniqueConstraintError') {
            return res.status(409).json({ error: 'Nome de usuário ou e-mail já existe.' });
        }
        res.status(500).json({ error: 'Erro ao criar usuário.' });
    }
});

app.put('/api/users/:username', tokenVerification, async (req, res) => {
    if (req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Acesso negado. Apenas administradores podem editar usuários.' });
    }

    const { username } = req.params;
    const { password, role } = req.body;

    const [updated] = await User.update(
        { password: password ? bcrypt.hashSync(password, 10) : undefined, role },
        { where: { username } }
    );

    if (updated) {
        const updatedUser = await User.findOne({ where: { username } });
        return res.status(200).json({ message: 'Usuário atualizado com sucesso.', user: updatedUser });
    }

    res.status(404).json({ error: 'Usuário não encontrado.' });
});

app.delete('/api/users/:username', tokenVerification, async (req, res) => {
    if (req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Acesso negado. Apenas administradores podem deletar usuários.' });
    }

    const { username } = req.params;
    const deleted = await User.destroy({ where: { username } });

    if (deleted) {
        return res.status(200).json({ message: 'Usuário deletado com sucesso.' });
    }

    res.status(404).json({ error: 'Usuário não encontrado.' });
});

app.listen(PORT, async () => {
    try {
        await sequelize.authenticate();
        console.log('Conexão com o banco de dados SQLite estabelecida com sucesso.');
        await populateDb();
        console.log(`Servidor rodando na porta ${PORT}`);
    } catch (error) {
        console.error('Erro ao conectar com o banco de dados:', error);
    }
const PORT = process.env.PORT || 5000;
// ...
app.listen(PORT, async () => {
    // ...
    console.log(`Servidor rodando na porta ${PORT}`);

});