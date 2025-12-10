import os
import time
import psycopg2
from flask import Flask, request, jsonify, render_template
import logging

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s myshop-app: %(message)s',
                    datefmt='%b %d %H:%M:%S')

# --- 1. Configuração do Banco de Dados ---
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# --- 2. Configuração do Flask ---
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- 3. Função de Conexão ---


def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Conexão com o PostgreSQL bem-sucedida!")
            return conn
        except psycopg2.OperationalError:
            print("Erro ao conectar... Tentando novamente em 5s.")
            time.sleep(5)
            retries -= 1
    print("ERRO: Não foi possível conectar ao banco de dados.")
    return None

# --- 4. Função de Inicialização do Banco ---


def init_db():
    conn = get_db_connection()
    if conn is None:
        return

    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            item TEXT NOT NULL,
            qtd INTEGER
        );
        ''')

        cur.execute("SELECT * FROM users WHERE username = 'admin'")
        if cur.fetchone() is None:
            print("Populando o banco de dados...")
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', 'senha123'))
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)", ('pedro', 'password'))
            cur.execute("INSERT INTO carts (username, item, qtd) VALUES (%s, %s, %s)",
                        ('admin', 'Servidor Dell', 2))
            cur.execute("INSERT INTO carts (username, item, qtd) VALUES (%s, %s, %s)",
                        ('admin', 'Cadeira de Escritório', 1000))
            cur.execute("INSERT INTO carts (username, item, qtd) VALUES (%s, %s, %s)",
                        ('pedro', 'Teclado Mecânico', 1))
        conn.commit()
    print("Banco de dados inicializado.")

# --- ROTA HOME (MOVIDA PARA CÁ - ANTES DO APP.RUN) ---


@app.route("/home", methods=['GET'])
def home():
    # Retorna JSON simples (Status 200)
    return jsonify({"status": "Loja Online Ativa", "versao": "1.0"}), 200

# Se você quiser usar o HTML visual que criamos antes, use este:


@app.route("/", methods=['GET'])
def index():
    # Retorna o arquivo index.html da pasta templates
    return render_template("index.html")

# --- 5. Endpoint de Login ---


@app.route("/login", methods=['POST'])
def login():
    dados = request.get_json()
    usuario_enviado = dados.get('usuario')
    senha_enviada = dados.get('senha')

    if "'" in usuario_enviado or "OR" in usuario_enviado.upper():
        msg_alerta = f"[ALERTA DE SEGURANÇA] SQL Injection Detectado! IP: {request.remote_addr} Payload: {usuario_enviado}"
        print(msg_alerta)
        logging.critical(msg_alerta)

    query = "SELECT * FROM users WHERE username = '" + usuario_enviado + \
        "' AND password = '" + senha_enviada + "'"  # nosec
    print(f"\n[LOG] Executando SQL: {query}")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "DB Off"}), 503

    with conn.cursor() as cur:
        try:
            cur.execute(query)
            user = cur.fetchone()
            if user:
                return jsonify({"mensagem": f"Bem-vindo, {user[1]}!"}), 200
            else:
                return jsonify({"erro": "Inválido"}), 401
        except Exception as e:
            return jsonify({"erro": "Erro SQL"}), 500

# --- 6. Endpoint de Carrinho ---


@app.route("/carrinho/<string:nome_usuario>", methods=['GET'])
def obter_carrinho(nome_usuario):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "DB Off"}), 503
    with conn.cursor() as cur:
        cur.execute(
            "SELECT item, qtd FROM carts WHERE username = %s", (nome_usuario,))
        items = cur.fetchall()
        if not items:
            return jsonify({"erro": "Vazio"}), 404
        return jsonify([{"item": i, "qtd": q} for i, q in items]), 200


# --- 7. Execução do Servidor (SEMPRE NO FINAL) ---
if __name__ == '__main__':
    init_db()
    print("Iniciando o servidor Flask...")
    app.run(debug=False, host='0.0.0.0', port=5000)  # nosec
