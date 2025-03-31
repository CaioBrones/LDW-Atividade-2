from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import sqlite3

DATABASE = 'database.db'

# Lista de celulares pré-cadastrados
celulares = [
    {"nome": "iPhone 13", "preco": "5.999,00"},
    {"nome": "Samsung Galaxy S21", "preco": "4.499,00"},
    {"nome": "Xiaomi Mi 11", "preco": "3.999,00"},
    {"nome": "Google Pixel 6", "preco": "4.299,00"},
    {"nome": "OnePlus 9 Pro", "preco": "4.799,00"},
    {"nome": "Motorola Edge 20", "preco": "3.499,00"},
]

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            concluida BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def init_app(app):
    init_db()  # Garante que o banco existe

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        if request.method == 'POST':
            nome = request.form['nome']
            preco = request.form['preco']
            
            # Corrige a formatação do preço para o banco de dados
            preco_float = float(preco.replace('.', '').replace(',', '.'))
            
            cursor.execute(
                'INSERT INTO produtos (nome, preco) VALUES (?, ?)',
                (nome, preco_float)
            )
            conn.commit()
        
        # Recupera produtos do banco
        cursor.execute('SELECT * FROM produtos')
        produtos_db = [{
            'id': row[0],
            'nome': row[1],
            'preco': f"{row[2]:.2f}".replace('.', ',')
        } for row in cursor.fetchall()]
        
        conn.close()
        
        return render_template(
            'cadastro.html',
            celulares=celulares,
            produtos=produtos_db
        )

    @app.route('/editar/<int:id>', methods=['GET', 'POST'])
    def editar(id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        if request.method == 'POST':
            novo_nome = request.form['nome']
            novo_preco = request.form['preco']
            preco_float = float(novo_preco.replace('.', '').replace(',', '.'))
            
            cursor.execute(
                'UPDATE produtos SET nome = ?, preco = ? WHERE id = ?',
                (novo_nome, preco_float, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('cadastro'))
        
        cursor.execute('SELECT * FROM produtos WHERE id = ?', (id,))
        produto_db = cursor.fetchone()
        conn.close()
        
        if not produto_db:
            return redirect(url_for('cadastro'))
        
        # Garantindo que o dicionário tem todas chaves necessárias
        produto = {
            'id': produto_db[0],
            'nome': produto_db[1],
            'preco': f"{produto_db[2]:.2f}".replace('.', ','),
            'concluida': produto_db[3]
        }
        
        print(f"DEBUG - Produto enviado para template: {produto}")  # Para verificar no console
        return render_template('editar.html', produto=produto)

    @app.route('/atualizar/<int:id>', methods=['POST'])
    def atualizar(id):
        # Esta rota pode ser usada se preferir um formulário separado
        nome = request.form['nome']
        preco = request.form['preco']
        preco_float = float(preco.replace('.', '').replace(',', '.'))
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE produtos SET nome = ?, preco = ? WHERE id = ?',
            (nome, preco_float, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('cadastro'))

    @app.route('/excluir/<int:id>')
    def excluir(id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('cadastro'))

    @app.route('/produtos', methods=['GET', 'POST'])
    def produtos():
        if request.method == 'POST':
            # Processar o formulário de cadastro de novos celulares
            nome = request.form.get('nome')
            preco = request.form.get('preco')

            if nome and preco:
                novo_celular = {
                    "nome": nome,
                    "preco": preco,
                }
                celulares.append(novo_celular)
                return redirect(url_for('produtos'))

        return render_template('produtos.html', celulares=celulares)

    @app.route('/consumo')
    def consumo():
        url = "https://www.gsmarena.com/makers.php3"
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            marcas = [{
                'nome': a.text.strip(),
                'link': f"https://www.gsmarena.com/{a['href']}"
            } for a in soup.find('table').find_all('a')]
            return render_template('consumo.html', marcas=marcas)
        except Exception as e:
            return f"Erro: {e}", 500