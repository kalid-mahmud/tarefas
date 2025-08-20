# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import jwt
import bcrypt
import datetime
from functools import wraps
from database import Session, User, Team, Board, List, Task, engine

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'uma_chave_secreta_forte_e_aleatoria'

# Função para gerar o token JWT
def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'is_admin': user.is_admin,
        'is_team_admin': user.is_team_admin,
        'team_id': user.team_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Função de decorador para proteger as rotas
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Session().query(User).filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
        
        return f(current_user, *args, **kwargs)
    return decorated

# Rota de Autenticação
@app.route('/api/login', methods=['POST'])
def login():
    session = Session()
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = session.query(User).filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
            token = generate_token(user)
            return jsonify({'message': 'Login successful', 'token': token})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    finally:
        session.close()

# Rota de Criação de Admin (SETUP INICIAL)
@app.route('/api/register_admin', methods=['POST'])
def register_admin():
    session = Session()
    try:
        if session.query(User).filter_by(is_admin=True).first():
            return jsonify({'error': 'Admin user already exists'}), 409

        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        admin_user = User(username=username, password_hash=password_hash, is_admin=True)
        session.add(admin_user)
        session.commit()

        return jsonify({'message': 'Admin user created successfully'}), 201
    finally:
        session.close()

# NOVA ROTA: Criação de Usuários
@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    session = Session()
    try:
        if not current_user.is_admin:
            return jsonify({'error': 'Permission denied'}), 403

        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, password_hash=password_hash)
        session.add(new_user)
        session.commit()

        return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201
    finally:
        session.close()

# Rotas de Equipes (Protegidas)
@app.route('/api/teams', methods=['POST'])
@token_required
def create_team(current_user):
    session = Session()
    try:
        if not current_user.is_admin:
            return jsonify({'error': 'Permission denied'}), 403

        data = request.json
        team_name = data.get('name')
        admin_username = data.get('admin_username')

        if not team_name or not admin_username:
            return jsonify({'error': 'Team name and admin username are required'}), 400

        team_admin_user = session.query(User).filter_by(username=admin_username).first()
        if not team_admin_user:
            return jsonify({'error': 'Team admin user not found'}), 404

        new_team = Team(name=team_name, admin_id=team_admin_user.id)
        session.add(new_team)
        session.commit()

        team_admin_user.is_team_admin = True
        team_admin_user.team_id = new_team.id
        session.commit()

        return jsonify({'message': 'Team created successfully', 'team_id': new_team.id}), 201
    finally:
        session.close()

@app.route('/api/teams', methods=['GET'])
@token_required
def get_teams(current_user):
    session = Session()
    try:
        if current_user.is_admin:
            teams = session.query(Team).all()
        elif current_user.is_team_admin:
            teams = session.query(Team).filter_by(id=current_user.team_id).all()
        else:
            teams = session.query(Team).filter_by(id=current_user.team_id).all()
        
        teams_data = [{'id': team.id, 'name': team.name} for team in teams]
        return jsonify(teams_data)
    finally:
        session.close()


# Rotas para Boards (Quadros)
@app.route('/api/boards', methods=['POST'])
@token_required
def create_board(current_user):
    session = Session()
    try:
        data = request.json
        board_name = data.get('name')
        team_id = data.get('team_id')

        if not board_name or not team_id:
            return jsonify({'error': 'Board name and team ID are required'}), 400
        
        if not current_user.is_admin and not (current_user.is_team_admin and current_user.team_id == team_id):
            return jsonify({'error': 'Permission denied'}), 403

        new_board = Board(name=board_name, team_id=team_id)
        session.add(new_board)
        session.commit()
        return jsonify({'message': 'Board created successfully', 'board_id': new_board.id}), 201
    finally:
        session.close()

@app.route('/api/boards/<int:team_id>', methods=['GET'])
@token_required
def get_boards(current_user, team_id):
    session = Session()
    try:
        if not current_user.is_admin and not current_user.team_id == team_id:
            return jsonify({'error': 'Permission denied'}), 403

        boards = session.query(Board).filter_by(team_id=team_id).all()
        boards_data = [{'id': board.id, 'name': board.name} for board in boards]
        return jsonify(boards_data)
    finally:
        session.close()

# Rotas para Lists (Colunas Kanban)
@app.route('/api/lists', methods=['POST'])
@token_required
def create_list(current_user):
    session = Session()
    try:
        data = request.json
        list_name = data.get('name')
        board_id = data.get('board_id')

        if not list_name or not board_id:
            return jsonify({'error': 'List name and board ID are required'}), 400

        board = session.query(Board).filter_by(id=board_id).first()
        if not board:
            return jsonify({'error': 'Board not found'}), 404

        if not current_user.is_admin and not (current_user.is_team_admin and current_user.team_id == board.team_id):
            return jsonify({'error': 'Permission denied'}), 403

        new_list = List(name=list_name, board_id=board_id)
        session.add(new_list)
        session.commit()
        return jsonify({'message': 'List created successfully', 'list_id': new_list.id}), 201
    finally:
        session.close()

# NOVA ROTA: Obter listas de um quadro
@app.route('/api/boards/<int:board_id>/lists', methods=['GET'])
@token_required
def get_lists(current_user, board_id):
    session = Session()
    try:
        board = session.query(Board).filter_by(id=board_id).first()
        if not board:
            return jsonify({'error': 'Board not found'}), 404

        # Permissão: verifica se o usuário é membro da equipe do quadro
        if not current_user.is_admin and not current_user.team_id == board.team_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        lists = session.query(List).filter_by(board_id=board_id).all()
        lists_data = [{'id': lst.id, 'name': lst.name} for lst in lists]
        return jsonify(lists_data)
    finally:
        session.close()


# Rotas para Tarefas (Cards)
@app.route('/api/tasks', methods=['POST'])
@token_required
def create_task(current_user):
    session = Session()
    try:
        data = request.json
        title = data.get('title')
        list_id = data.get('list_id')
        assigned_to_id = data.get('assigned_to_id')
        description = data.get('description')
        due_date = data.get('due_date')

        if not title or not list_id:
            return jsonify({'error': 'Title and list_id are required'}), 400

        task_list = session.query(List).filter_by(id=list_id).first()
        if not task_list:
            return jsonify({'error': 'List not found'}), 404

        board = session.query(Board).filter_by(id=task_list.board_id).first()
        
        # Permissão: Apenas membros da equipe podem criar tarefas
        if not current_user.is_admin and not current_user.team_id == board.team_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        new_task = Task(
            title=title, 
            list_id=list_id, 
            assigned_to=assigned_to_id,
            description=description,
            due_date=due_date
        )
        session.add(new_task)
        session.commit()
        return jsonify({'message': 'Task created successfully', 'task_id': new_task.id}), 201
    finally:
        session.close()

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    session = Session()
    try:
        data = request.json
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Permissão: Apenas membros da equipe podem atualizar tarefas
        list_obj = session.query(List).filter_by(id=task.list_id).first()
        board = session.query(Board).filter_by(id=list_obj.board_id).first()

        if not current_user.is_admin and not current_user.team_id == board.team_id:
            return jsonify({'error': 'Permission denied'}), 403

        # Atualiza os campos se eles existirem na requisição
        if 'title' in data: task.title = data['title']
        if 'description' in data: task.description = data['description']
        if 'due_date' in data: task.due_date = data['due_date']
        if 'assigned_to_id' in data: task.assigned_to = data['assigned_to_id']
        if 'list_id' in data: task.list_id = data['list_id']

        session.commit()
        return jsonify({'message': 'Task updated successfully'})
    finally:
        session.close()

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    session = Session()
    try:
        task = session.query(Task).filter_by(id=task_id).first()
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Permissão: Apenas membros da equipe podem deletar tarefas
        list_obj = session.query(List).filter_by(id=task.list_id).first()
        board = session.query(Board).filter_by(id=list_obj.board_id).first()

        if not current_user.is_admin and not current_user.team_id == board.team_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        session.delete(task)
        session.commit()
        return jsonify({'message': 'Task deleted successfully'})
    finally:
        session.close()

@app.route('/api/lists/<int:list_id>/tasks', methods=['GET'])
@token_required
def get_tasks_by_list(current_user, list_id):
    session = Session()
    try:
        list_obj = session.query(List).filter_by(id=list_id).first()
        if not list_obj:
            return jsonify({'error': 'List not found'}), 404
        
        board = session.query(Board).filter_by(id=list_obj.board_id).first()
        if not board:
            return jsonify({'error': 'Board not found for this list'}), 404
            
        # Permissão: Apenas membros da equipe podem ver as tarefas
        if not current_user.is_admin and not current_user.team_id == board.team_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        tasks = session.query(Task).filter_by(list_id=list_id).all()
        tasks_data = [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'due_date': task.due_date,
                'assigned_to': task.assigned_to,
                'list_id': task.list_id
            } for task in tasks
        ]
        return jsonify(tasks_data)
    finally:
        session.close()

if __name__ == '__main__':
    session = Session()
    if not session.query(User).filter_by(is_admin=True).first():
        print("Admin user not found. Please create one by making a POST request to /api/register_admin with a JSON body: {'username': 'your_admin_username', 'password': 'your_admin_password'}.")
    session.close()

    app.run(debug=True, host='0.0.0.0', port=5000)