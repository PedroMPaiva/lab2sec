import os
import time
import psycopg2  # Novo import para falar com o Postgres
from flask import Flask, request, jsonify
import logging

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s myshop-app: %(message)s',
                    datefmt='%b %d %H:%M:%S')

# --- 1. Configuração do Banco de Dados ---
# O Docker Compose vai "injetar" estes valores no nosso ambiente
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# --- 2. Configuração do Flask ---
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- 3. Função de Conexão (Novo) ---
# Esta função nos conecta ao banco de dados.
# Inclui um loop de "retry" pois o app pode iniciar antes do banco.


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
            print(
                "Erro ao conectar... O banco de dados pode estar iniciando. Tentando novamente em 5s.")
            time.sleep(5)  # Espera 5 segundos e tenta de novo
            retries -= 1
    print("ERRO: Não foi possível conectar ao banco de dados após várias tentativas.")
    return None  # Retorna None se falhar

# --- 4. Função de Inicialização do Banco (Novo) ---
# Esta função cria nossas tabelas e insere os dados de teste


def init_db():
    conn = get_db_connection()
    if conn is None:
        print("ERRO: Impossível inicializar o banco. Conexão nula.")
        return

    # 'with' garante que o cursor e a conexão sejam fechados
    with conn.cursor() as cur:
        # Cria a tabela de usuários
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        ''')
        # Cria a tabela de carrinhos
        cur.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            item TEXT NOT NULL,
            qtd INTEGER
        );
        ''')

        # Verifica se o admin já existe antes de inserir
        cur.execute("SELECT * FROM users WHERE username = 'admin'")
        if cur.fetchone() is None:
            print("Populando o banco de dados com dados de teste...")
            # Insere os usuários
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', 'senha123'))
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)", ('pedro', 'password'))

            # Insere os carrinhos
            cur.execute("INSERT INTO carts (username, item, qtd) VALUES (%s, %s, %s)",
                        ('admin', 'Servidor Dell', 2))
            cur.execute("INSERT INTO carts (username, item, qtd) VALUES (%s, %s, %s)",
                        # O valor 1000 que você testou
                        ('admin', 'Cadeira de Escritório', 1000))
            cur.execute("INSERT INTO carts (username, item, qtd) VALUES (%s, %s, %s)",
                        ('pedro', 'Teclado Mecânico', 1))

        conn.commit()  # Salva as alterações no banco
    print("Banco de dados inicializado com sucesso.")

# --- 5. Endpoint de Login (Refatorado e VULNERÁVEL) ---


@app.route("/login", methods=['POST'])
def login():
    dados = request.get_json()
    usuario_enviado = dados.get('usuario')
    senha_enviada = dados.get('senha')
    if "'" in usuario_enviado or "OR" in usuario_enviado.upper():
        msg_alerta = f"[ALERTA DE SEGURANÇA] SQL Injection Detectado! IP Origem: {request.remote_addr} Payload: {usuario_enviado}"
        print(msg_alerta)            # Mostra no terminal do Docker
        # <--- SALVA NO ARQUIVO app.log PARA O WAZUH LER
        logging.critical(msg_alerta)

    # --- AQUI ESTÁ A VULNERABILIDADE DE SQL INJECTION (REAL) ---
    # Estamos construindo a query por concatenação de strings.
    # Esta é a "dívida técnica" que simula o código legado.
    query = "SELECT * FROM users WHERE username = '" + usuario_enviado + \
        "' AND password = '" + senha_enviada + "'"  # nosec
    print(f"\n[LOG] Executando SQL vulnerável: {query}")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Servidor indisponível"}), 503

    with conn.cursor() as cur:
        try:
            cur.execute(query)
            user = cur.fetchone()  # Pega o primeiro resultado

            if user:
                # O ataque 'admin' OR 1=1 --' VAI retornar um usuário (o admin)
                # e o login será um sucesso.
                print(f"[LOG] Usuário encontrado: {user[1]}")
                return jsonify({"mensagem": f"Bem-vindo, {user[1]}!"}), 200
            else:
                return jsonify({"erro": "Usuário ou senha inválidos"}), 401
        except Exception as e:
            print(f"ERRO DE SQL: {e}")
            return jsonify({"erro": "Erro na consulta"}), 500

# --- 6. Endpoint de Carrinho (Refatorado e VULNERÁVEL) ---


@app.route("/carrinho/<string:nome_usuario>", methods=['GET'])
def obter_carrinho(nome_usuario):
    # --- AQUI ESTÁ A FALHA (IDOR) ---
    # O código ainda confia cegamente no 'nome_usuario' vindo da URL.
    # Ele não checa se o usuário logado é o 'nome_usuario'.
    print(f"\n[LOG] Requisição recebida para o carrinho de: {nome_usuario}")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"erro": "Servidor indisponível"}), 503

    with conn.cursor() as cur:
        # A query em si é segura (parametrizada) para evitar uma *segunda* SQLi.
        # A falha de segurança aqui é o IDOR (a lógica de negócio).
        query = "SELECT item, qtd FROM carts WHERE username = %s"
        cur.execute(query, (nome_usuario,))
        carrinho_items = cur.fetchall()  # Pega todos os itens

        if not carrinho_items:
            return jsonify({"erro": "Carrinho não encontrado"}), 404

        # Formata a saída
        carrinho = [{"item": item, "qtd": qtd} for item, qtd in carrinho_items]
        return jsonify(carrinho), 200


# --- 7. "Abra o Restaurante" (Atualizado) ---
if __name__ == '__main__':
    print("Iniciando o serviço...")
    # 1. Primeiro, garanta que o banco e as tabelas existam
    init_db()
    # 2. Depois, inicie o servidor web
    print("Iniciando o servidor Flask em http://0.0.0.0:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)  # nosec
