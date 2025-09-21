import sqlite3  
from flask import Flask, render_template, request, redirect, url_for, flash
import database as db
import os

app = Flask(__name__)
app.secret_key = 'secret_key_123'

# Rota principal - Lista todos os usuários
@app.route('/')
def index():
    try:
        conn = db.create_connection()
        users = db.get_all_users(conn)
        conn.close()
        return render_template('index.html', users=users)
    except Exception as e:
        return f"Erro: {str(e)}"

# Rota para adicionar novo usuário
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            age = request.form.get('age', 0) or 0
            
            if name and email:
                conn = db.create_connection()
                user_id = db.insert_user(conn, (name, email, age))
                conn.close()
                
                if user_id:
                    flash('Usuário adicionado com sucesso!', 'success')
                else:
                    flash('Erro ao adicionar usuário. Email pode já existir.', 'error')
                
                return redirect(url_for('index'))
            else:
                flash('Nome e email são obrigatórios!', 'error')
        except Exception as e:
            flash(f'Erro: {str(e)}', 'error')
    
    return render_template('add-user.html')

# Rota para editar usuário
@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = db.create_connection()
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            age = request.form.get('age', 0) or 0
            
            if name and email:
                success = db.update_user(conn, (name, email, age, user_id))
                conn.close()
                
                if success:
                    flash('Usuário atualizado com sucesso!', 'success')
                else:
                    flash('Erro ao atualizar usuário.', 'error')
                
                return redirect(url_for('index'))
            else:
                flash('Nome e email são obrigatórios!', 'error')
        except Exception as e:
            flash(f'Erro: {str(e)}', 'error')
    
    user = db.get_user_by_id(conn, user_id)
    conn.close()
    
    if user:
        return render_template('edit-user.html', user=user)
    else:
        flash('Usuário não encontrado!', 'error')
        return redirect(url_for('index'))

# Rota para deletar usuário
@app.route('/delete/<int:user_id>')
def delete_user(user_id):
    try:
        conn = db.create_connection()
        success = db.delete_user(conn, user_id)
        conn.close()
        
        if success:
            flash('Usuário deletado com sucesso!', 'success')
        else:
            flash('Erro ao deletar usuário.', 'error')
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('index'))
@app.route('/debug-db')
def debug_database():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Ignorar tabelas internas do SQLite
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
        """)
        tables = cursor.fetchall()
        # 3. Começar a criar o HTML
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🔍 Debug do Banco de Dados</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                h2 { color: #555; margin-top: 30px; }
                h3 { color: #777; }
                table { border-collapse: collapse; width: 100%; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .success { color: green; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>🔍 Debug do Banco de Dados</h1>
        """
        
        # 4. Se não encontrar tabelas
        if not tables:
            html += "<p class='error'>❌ Nenhuma tabela encontrada no banco!</p>"
        else:
            html += f"<p class='success'>✅ Encontradas {len(tables)} tabelas</p>"
        
        # 5. Para cada tabela encontrada
        for table in tables:
            table_name = table[0]
            html += f"<h2>📋 Tabela: {table_name}</h2>"
            
            # 6. Mostrar a ESTRUTURA da tabela
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            html += "<h3>🏗️ Estrutura da Tabela:</h3>"
            html += "<ul>"
            for col in columns:
                # col[1] = nome da coluna, col[2] = tipo de dados
                html += f"<li><strong>{col[1]}</strong> ({col[2]})</li>"
            html += "</ul>"
            
            # 7. Mostrar os DADOS da tabela
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            html += f"<h3>📝 Dados ({len(rows)} registros):</h3>"
            
            if rows:
                html += "<table>"
                
                # Cabeçalhos da tabela
                html += "<tr>"
                for col in columns:
                    html += f"<th>{col[1]}</th>"
                html += "</tr>"
                
                # Dados de cada linha
                for row in rows:
                    html += "<tr>"
                    for value in row:
                        html += f"<td>{value}</td>"
                    html += "</tr>"
                
                html += "</table>"
            else:
                html += "<p class='error'>❌ Nenhum dado encontrado nesta tabela</p>"
        
        # 8. Finalizar o HTML
        html += """
        </body>
        </html>
        """
        
        conn.close()
        return html
        
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Erro</title></head>
        <body>
            <h1 style='color: red;'>❌ Erro ao acessar o banco</h1>
            <p><strong>Erro:</strong> {str(e)}</p>
            <p>Verifique se o arquivo users.db existe e está acessível.</p>
        </body>
        </html>
        """

if __name__ == '__main__':
    # Inicializa o banco de dados
    db.init_db()
    
    # Verifica se os templates existem
    templates = ['index.html', 'add-user.html', 'edit-user.html']
    for template in templates:
        path = os.path.join('templates', template)
        if not os.path.exists(path):
            print(f"⚠️ Aviso: {path} não encontrado!")
        else:
            print(f"✅ {path} encontrado")
    
    print("🚀 Servidor iniciando...")
    app.run(debug=True, host='0.0.0.0', port=5000)