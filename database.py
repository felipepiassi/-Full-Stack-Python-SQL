import sqlite3
from sqlite3 import Error

def create_connection():
    """Cria uma conexão com o banco de dados SQLite"""
    conn = None
    try:
        conn = sqlite3.connect('users.db')
        print("Conexão com SQLite estabelecida")
        return conn
    except Error as e:
        print(f"Erro ao conectar com SQLite: {e}")
    return conn

def create_table(conn):
    """Cria a tabela de usuários se não existir"""
    try:
        sql_create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql_create_users_table)
        conn.commit()
        print("Tabela 'users' criada ou já existe")
    except Error as e:
        print(f"Erro ao criar tabela: {e}")

def insert_user(conn, user):
    """Insere um novo usuário na tabela"""
    sql = '''INSERT INTO users(name, email, age)
             VALUES(?,?,?)'''
    cursor = conn.cursor()
    try:
        cursor.execute(sql, user)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Erro ao inserir usuário: {e}")
        return None

def get_all_users(conn):
    """Retorna todos os usuários"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    return cursor.fetchall()

def get_user_by_id(conn, user_id):
    """Retorna um usuário pelo ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def update_user(conn, user):
    """Atualiza um usuário existente"""
    sql = '''UPDATE users
             SET name = ?, email = ?, age = ?
             WHERE id = ?'''
    cursor = conn.cursor()
    try:
        cursor.execute(sql, user)
        conn.commit()
        return True
    except Error as e:
        print(f"Erro ao atualizar usuário: {e}")
        return False

def delete_user(conn, user_id):
    """Deleta um usuário pelo ID"""
    sql = 'DELETE FROM users WHERE id = ?'
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (user_id,))
        conn.commit()
        return True
    except Error as e:
        print(f"Erro ao deletar usuário: {e}")
        return False

# Inicialização do banco de dados
def init_db():
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        conn.close()