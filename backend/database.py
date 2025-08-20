# backend/database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///project.db')
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_team_admin = Column(Boolean, default=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    # Adicione a relação 'team' aqui para que o 'backref' na classe Team funcione
    # corretamente, e para que User possa acessar o objeto Team ao qual pertence.
    team = relationship("Team", back_populates="members", foreign_keys=[team_id]) # <-- Adicione esta linha


class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'))
    # Aqui está a mudança principal: especifique foreign_keys para a relação members
    members = relationship("User", back_populates="team", foreign_keys=[User.team_id]) # <-- Linha modificada
    boards = relationship("Board", backref="team")

class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))
    lists = relationship("List", backref="board")

class List(Base):
    __tablename__ = 'lists'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    board_id = Column(Integer, ForeignKey('boards.id'))
    tasks = relationship("Task", backref="list")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))
    due_date = Column(String(20))
    assigned_to = Column(Integer, ForeignKey('users.id'))
    list_id = Column(Integer, ForeignKey('lists.id'))

# Cria as tabelas no banco de dados
Base.metadata.create_all(engine)