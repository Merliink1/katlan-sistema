# ================= IMPORTS =================
from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime
import json, os, unicodedata
import psycopg2
import bcrypt

# ================= CONFIG APP =================
app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", "derc_pf_secret")

# ================= BANCO =================
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL não configurado")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn, conn.cursor()

# 🔥 INICIALIZA BANCO
def init_db():

    conn, cursor = get_db()

    # usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        user TEXT UNIQUE,
        senha TEXT,
        perfil TEXT,
        ativo BOOLEAN DEFAULT TRUE
    )
    """)

    # logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        acao TEXT,
        texto TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # chat
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        mensagem TEXT,
        hora TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # historico
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id SERIAL PRIMARY KEY,
        usuario TEXT,
        texto TEXT,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # 🔥 CRIA ADMIN SE NÃO EXISTIR
    cursor.execute("SELECT id FROM usuarios WHERE user=%s", ("admin",))
    if not cursor.fetchone():

        senha_hash = bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode()

        cursor.execute(
            "INSERT INTO usuarios (user, senha, perfil) VALUES (%s, %s, %s)",
            ("admin", senha_hash, "admin")
        )

        conn.commit()

    cursor.close()
    conn.close()


# 🔥 chama ao iniciar
init_db()

# ================= FUNÇÕES =================
def carregar(arq):
    if not os.path.exists(arq):
        with open(arq, 'w') as f:
            json.dump([], f)
    with open(arq) as f:
        return json.load(f)

def salvar(arq, dados):
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def normalizar(txt):
    if not txt:
        return ""
    txt = txt.strip().upper()
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt)
                  if unicodedata.category(c) != 'Mn')
    return txt

# ================= RESOLUÇÕES =================
RESOLUCOES = {

# ELÉTRICA / TECNOLOGIA
"ELETROTECNICA": "RESOLUÇÃO Nº 074 DE 05 DE JULHO DE 2019, RESOLUÇÃO Nº 39 DE 26 DE OUTUBRO DE 2018 E RESOLUÇÃO Nº 094 DE 13 DE FEVEREIRO DE 2020",
"ELETRONICA": "RESOLUÇÃO Nº 111 DE 08 DE OUTUBRO DE 2020",
"ELETROELETRONICA": "RESOLUÇÃO Nº 118 DE 14 DE DEZEMBRO DE 2020",
"TELECOMUNICACOES": "RESOLUÇÃO Nº 083 DE 30 DE OUTUBRO DE 2019",
"REDE DE COMPUTADORES": "RESOLUÇÃO Nº 106 DE 15 DE JULHO DE 2020",
"INFORMATICA": "RESOLUÇÃO Nº 146 DE 02 DE SETEMBRO DE 2021",
"MICROINFORMATICA": "RESOLUÇÃO Nº 146 DE 02 DE SETEMBRO DE 2021",

# MECÂNICA / INDUSTRIAL
"MECANICA": "RESOLUÇÃO Nº 101 DE 04 DE JUNHO DE 2020",
"ELETROMECANICA": "RESOLUÇÃO Nº 121 DE 14 DE DEZEMBRO DE 2020",
"MECATRONICA": "RESOLUÇÃO Nº 120 DE 14 DE DEZEMBRO DE 2020",
"AUTOMACAO INDUSTRIAL": "RESOLUÇÃO Nº 119 DE 14 DE DEZEMBRO DE 2020",
"MANUTENCAO AUTOMOTIVA": "RESOLUÇÃO Nº 140 DE 02 DE JULHO DE 2021",
"MANUTENCAO DE MAQUINAS INDUSTRIAIS": "RESOLUÇÃO Nº 216 DE 29 DE MARÇO DE 2023",
"REFRIGERACAO E CLIMATIZACAO": "RESOLUÇÃO Nº 123 DE 14 DE DEZEMBRO DE 2020",

# CONSTRUÇÃO CIVIL
"EDIFICACOES": "RESOLUÇÃO Nº 058 DE 22 DE MARÇO DE 2019, RESOLUÇÃO Nº 186 DE 15 DE JUNHO DE 2022, RESOLUÇÃO Nº 108 DE 08 DE OUTUBRO DE 2020 E RESOLUÇÃO Nº 205 DE 20 DE DEZEMBRO DE 2022",
"ESTRADAS": "RESOLUÇÃO Nº 109 DE 08 DE OUTUBRO DE 2020",
"DESENHO DA CONSTRUCAO CIVIL": "RESOLUÇÃO Nº 122 DE 14 DE DEZEMBRO DE 2020",

# AMBIENTAL
"MEIO AMBIENTE": "RESOLUÇÃO Nº 110 DE 08 DE OUTUBRO DE 2020",
"SANEAMENTO": "RESOLUÇÃO Nº 103 DE 15 DE JULHO DE 2020",

# MINERAÇÃO / GEO
"MINERACAO": "RESOLUÇÃO Nº 104 DE 15 DE JULHO DE 2020",
"AGRIMENSURA": "RESOLUÇÃO Nº 089 DE 06 DE DEZEMBRO DE 2019 E RESOLUÇÃO Nº 159 DE 29 DE NOVEMBRO DE 2021",
"GEODESIA": "RESOLUÇÃO Nº 089 DE 06 DE DEZEMBRO DE 2019 E RESOLUÇÃO Nº 159 DE 29 DE NOVEMBRO DE 2021",
"CARTOGRAFIA": "RESOLUÇÃO Nº 089 DE 06 DE DEZEMBRO DE 2019 E RESOLUÇÃO Nº 159 DE 29 DE NOVEMBRO DE 2021",
"GEOPROCESSAMENTO": "RESOLUÇÃO Nº 089 DE 06 DE DEZEMBRO DE 2019 E RESOLUÇÃO Nº 159 DE 29 DE NOVEMBRO DE 2021",

# QUÍMICA / ALIMENTOS
"QUIMICA": "RESOLUÇÃO CONJUNTA Nº 01 DE 15 DE DEZEMBRO DE 2023",
"ALIMENTOS": "RESOLUÇÃO Nº 095 DE 13 DE FEVEREIRO DE 2020",
"AGROINDUSTRIA": "RESOLUÇÃO Nº 246 DE 20 DE DEZEMBRO DE 2023",

# METAL / SOLDAGEM
"SOLDAGEM": "RESOLUÇÃO Nº 107 DE 12 DE AGOSTO DE 2020 E RESOLUÇÃO Nº 114 DE 08 DE OUTUBRO DE 2020",
"METALURGIA": "RESOLUÇÃO Nº 107 DE 12 DE AGOSTO DE 2020 E RESOLUÇÃO Nº 114 DE 08 DE OUTUBRO DE 2020",

# ENERGIA
"PETROLEO E GAS": "RESOLUÇÃO Nº 138 DE 02 DE JULHO DE 2021",
"SISTEMAS DE ENERGIA RENOVAVEL": "RESOLUÇÃO Nº 178 DE 04 DE MARÇO DE 2022",
"SISTEMA DE ENERGIA RENOVAVEL": "RESOLUÇÃO Nº 178 DE 04 DE MARÇO DE 2022",
"EM SISTEMAS DE ENERGIA RENOVAVEL": "RESOLUÇÃO Nº 178 DE 04 DE MARÇO DE 2022",

# OUTROS
"DESIGN DE INTERIORES": "RESOLUÇÃO Nº 096 DE 13 DE FEVEREIRO DE 2020",
"PAISAGISMO": "RESOLUÇÃO Nº 248 DE 20 DE DEZEMBRO DE 2023",
"PORTOS": "RESOLUÇÃO Nº 143 DE 02 DE SETEMBRO DE 2021",
"INSTRUMENTACAO": "RESOLUÇÃO Nº 260 DE 03 DE ABRIL DE 2024"
}

# ================= ROTAS =================
@app.route('/')
def index():
    return render_template('login.html')

# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():

    conn = None
    cursor = None

    try:
        user = (request.form.get('user') or "").strip()
        senha = (request.form.get('senha') or "").strip()

        # 🔒 validação básica
        if not user or not senha:
            return render_template('login.html', erro="Preencha usuário e senha")

        conn, cursor = get_db()

        cursor.execute("""
            SELECT user, senha, perfil, ativo
            FROM usuarios
            WHERE user=%s
        """, (user,))

        u = cursor.fetchone()

        # 🔒 usuário não encontrado
        if not u:
            return render_template('login.html', erro="Usuário ou senha inválidos")

        # 🔒 valida senha com hash
        if not bcrypt.checkpw(senha.encode(), u[1].encode()):
            return render_template('login.html', erro="Usuário ou senha inválidos")

        # 🔒 usuário desativado
        if not u[3]:
            return render_template('login.html', erro="Usuário desativado")

        # 🔥 cria sessão
        session['user'] = u[0]
        session['perfil'] = u[2]
        session['login_time'] = str(datetime.now())

        # 🔥 LOG de login
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            u[0],
            "login",
            "Usuário entrou no sistema"
        ))

        conn.commit()

        return redirect('/sistema')

    except Exception as e:
        print("ERRO LOGIN:", e)
        return render_template('login.html', erro="Erro interno")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= SISTEMA =================
@app.route('/sistema')
def sistema():

    if 'user' not in session:
        return redirect('/')

    return render_template(
        'sistema.html',
        usuario=session.get('user'),
        cursos=RESOLUCOES.keys()
    )

# ================= LOGOUT =================
@app.route('/logout')
def logout():

    conn = None
    cursor = None

    try:
        if 'user' in session:

            conn, cursor = get_db()

            cursor.execute("""
                INSERT INTO logs (usuario, acao, texto)
                VALUES (%s, %s, %s)
            """, (
                session.get('user'),
                "logout",
                "Usuário saiu do sistema"
            ))

            conn.commit()

    except Exception as e:
        print("ERRO LOGOUT:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # 🔥 limpa sessão SEMPRE
    session.clear()

    return redirect('/')

# ================= CHAT =================
@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        data = request.json or {}

        mensagem = (data.get("mensagem") or "").strip()

        # 🔒 valida mensagem
        if not mensagem:
            return jsonify({"erro": "mensagem vazia"}), 400

        if len(mensagem) > 1000:
            return jsonify({"erro": "mensagem muito longa"}), 400

        conn, cursor = get_db()

        hora = datetime.now().strftime("%H:%M")

        # 🔥 salva chat
        cursor.execute("""
            INSERT INTO chat (usuario, mensagem, hora)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            mensagem,
            hora
        ))

        # 🔥 salva log
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            "chat",
            mensagem[:200]  # limita log
        ))

        conn.commit()

        return jsonify({"ok": True})

    except Exception as e:
        print("ERRO CHAT ENVIAR:", e)
        return jsonify({"erro": "falha no envio"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/chat_listar')
def chat_listar():

    # 🔒 valida login
    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        conn, cursor = get_db()

        cursor.execute("""
            SELECT usuario, mensagem, hora
            FROM chat
            ORDER BY id DESC
            LIMIT 100
        """)

        dados = cursor.fetchall()

        lista = []

        for d in dados:
            lista.append({
                "usuario": d[0] or "Desconhecido",
                "mensagem": d[1] or "",
                "hora": d[2] or ""
            })

        return jsonify(lista)

    except Exception as e:
        print("ERRO LISTAR CHAT:", e)
        return jsonify({"erro": "falha ao carregar chat"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= REGISTRAR =================
@app.route('/registrar', methods=['POST'])
def registrar():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        data = request.json or {}

        protocolo = data.get('protocolo')
        status = data.get('status')

        if not protocolo or not status:
            return jsonify({"msg": "Dados incompletos"}), 400

        conn, cursor = get_db()

        texto = f"PROTOCOLO: {protocolo} | STATUS: {status}"

        # 🔥 salva no histórico
        cursor.execute("""
            INSERT INTO historico (usuario, texto)
            VALUES (%s, %s)
        """, (
            session.get('user'),
            texto
        ))

        # 🔥 salva log
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            "registro",
            texto
        ))

        conn.commit()

        return jsonify({"msg": "Salvo"})

    except Exception as e:
        print("ERRO REGISTRAR:", e)
        return jsonify({"msg": "Erro"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= DEFERIMENTO =================
@app.route('/deferimento', methods=['POST'])
def deferimento():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        data = request.json or {}

        curso = (data.get("curso") or "").strip()
        tipo = data.get("tipo") or ""

        if not curso:
            return jsonify({"texto": "Curso não informado"}), 400

        resolucao = RESOLUCOES.get(curso, "RESOLUÇÃO NÃO IDENTIFICADA")

        # 🔥 TEXTO
        if tipo == "definitivo":
            texto = f"""REGISTRO DEFERIDO.
Cadastro finalizado e ATIVO. Você poderá acessar o seu ambiente profissional através da senha encaminhada por e-mail. Para verificar suas atribuições técnicas com habilitação em {curso}, consulte a {resolucao}, onde constam as responsabilidades e diretrizes específicas para o exercício de sua profissão.

Por meio de seu ambiente profissional será possível gerar sua anuidade e, após a compensação do pagamento no sistema, poderá emitir sua carteira profissional. Para mais informações sobre sua anuidade, entre em contato pelo canal (98) 98279-0023.
"""
        else:
            texto = f"""REGISTRO DEFERIDO.
Cadastro finalizado e ATIVO. Por se tratar de Registro Provisório, o mesmo terá validade de 01 ano passando a constar da data de efetivação. Você poderá acessar o seu ambiente profissional através da senha encaminhada por e-mail. Para verificar suas atribuições técnicas com habilitação em {curso}, consulte a {resolucao}, onde constam as responsabilidades e diretrizes específicas para o exercício de sua profissão.

Por meio de seu ambiente profissional será possível gerar sua anuidade e, após a compensação do pagamento no sistema, poderá emitir sua certidão de quitação de pessoa física e ter acesso a sua carteira profissional digital. Para mais informações sobre sua anuidade, entre em contato pelo canal (98) 98279-0023
"""

        # 🔥 abre conexão só uma vez
        conn, cursor = get_db()

        # 🔥 log
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            "deferimento",
            f"{curso} | {tipo}"
        ))

        conn.commit()

        return jsonify({"texto": texto})

    except Exception as e:
        print("ERRO NO DEFERIMENTO:", e)
        return jsonify({"texto": "Erro interno no servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= USUÁRIOS =================
@app.route('/listar_usuarios')
def listar_usuarios():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        conn, cursor = get_db()

        cursor.execute("""
            SELECT user, perfil, ativo
            FROM usuarios
            ORDER BY user
        """)

        dados = cursor.fetchall()

        lista = []

        for u in dados:
            lista.append({
                "user": u[0],
                "perfil": u[1],
                "ativo": u[2]
            })

        return jsonify(lista)

    except Exception as e:
        print("ERRO LISTAR USUARIOS:", e)
        return jsonify({"erro": "falha ao listar"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/alterar_senha', methods=['POST'])
def alterar_senha():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        data = request.json

        user = data.get('user')
        nova = data.get('senha')

        if not user or not nova:
            return jsonify({"msg": "Dados inválidos"}), 400

        conn, cursor = get_db()

        senha_hash = bcrypt.hashpw(nova.encode(), bcrypt.gensalt()).decode()

        cursor.execute("""
            UPDATE usuarios 
            SET senha=%s 
            WHERE user=%s
        """, (senha_hash, user))

        conn.commit()

        return jsonify({"msg": "Senha atualizada"})

    except Exception as e:
        print("ERRO alterar_senha:", e)
        return jsonify({"msg": "Erro interno"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/excluir_usuario', methods=['POST'])
def excluir_usuario():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    # 🔒 só admin pode excluir
    if session.get('perfil') != 'admin':
        return jsonify({"erro": "sem permissão"}), 403

    conn = None
    cursor = None

    try:
        data = request.json
        user = data.get('user')

        if not user:
            return jsonify({"msg": "Usuário inválido"}), 400

        # 🔒 não pode excluir a si mesmo
        if user == session.get('user'):
            return jsonify({"msg": "Você não pode excluir seu próprio usuário"}), 400

        # 🔒 não pode excluir admin
        if user == 'admin':
            return jsonify({"msg": "Não é permitido excluir o admin"}), 400

        conn, cursor = get_db()

        cursor.execute("DELETE FROM usuarios WHERE user=%s", (user,))
        conn.commit()

        # 🔥 LOG
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            "excluir_usuario",
            f"Usuário excluído: {user}"
        ))

        conn.commit()

        return jsonify({"msg": "Excluído com sucesso"})

    except Exception as e:
        print("ERRO excluir_usuario:", e)
        return jsonify({"msg": "Erro interno"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/toggle_usuario', methods=['POST'])
def toggle_usuario():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    # 🔒 só admin pode alterar status
    if session.get('perfil') != 'admin':
        return jsonify({"erro": "sem permissão"}), 403

    conn = None
    cursor = None

    try:
        data = request.json
        user = data.get('user')

        if not user:
            return jsonify({"msg": "Usuário inválido"}), 400

        # 🔒 não pode desativar a si mesma
        if user == session.get('user'):
            return jsonify({"msg": "Você não pode alterar seu próprio status"}), 400

        # 🔒 não pode desativar admin
        if user == 'admin':
            return jsonify({"msg": "Não é permitido alterar o admin"}), 400

        conn, cursor = get_db()

        cursor.execute(
            "SELECT ativo FROM usuarios WHERE user=%s",
            (user,)
        )

        atual = cursor.fetchone()

        if not atual:
            return jsonify({"msg": "Usuário não encontrado"}), 404

        novo = not atual[0]

        cursor.execute(
            "UPDATE usuarios SET ativo=%s WHERE user=%s",
            (novo, user)
        )

        conn.commit()

        # 🔥 LOG
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            "toggle_usuario",
            f"{'Ativado' if novo else 'Desativado'} usuário: {user}"
        ))

        conn.commit()

        return jsonify({"msg": "Atualizado com sucesso"})

    except Exception as e:
        print("ERRO toggle_usuario:", e)
        return jsonify({"msg": "Erro interno"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= HISTÓRICO =================
@app.route('/salvar_analise', methods=['POST'])
def salvar_analise():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        data = request.json or {}

        texto = (data.get("texto") or "").strip()

        # 🔒 valida texto
        if not texto:
            return jsonify({"erro": "Texto vazio"}), 400

        # 🔒 limite (evita travar banco)
        if len(texto) > 5000:
            return jsonify({"erro": "Texto muito grande"}), 400

        conn, cursor = get_db()

        # 🔥 salva histórico
        cursor.execute("""
            INSERT INTO historico (usuario, texto)
            VALUES (%s, %s)
        """, (
            session.get('user'),
            texto
        ))

        # 🔥 salva log (resumido)
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            "analise",
            texto[:200]  # salva só começo pra não poluir log
        ))

        conn.commit()

        return jsonify({"msg": "ok"})

    except Exception as e:
        print("ERRO HISTORICO:", e)
        return jsonify({"erro": "falha"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/historico')
def historico():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        conn, cursor = get_db()

        cursor.execute("""
            SELECT usuario, texto, data
            FROM historico
            ORDER BY data DESC
            LIMIT 200
        """)

        dados = cursor.fetchall()

        lista = []

        for d in dados:
            lista.append({
                "usuario": d[0],
                "texto": d[1],
                "data": d[2].strftime("%d/%m/%Y %H:%M") if d[2] else ""
            })

        return jsonify(lista)

    except Exception as e:
        print("ERRO LISTAR HISTORICO:", e)
        return jsonify({"erro": "falha ao carregar"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= CADASTRAR USUARIO =================
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():

    if 'user' not in session:
        return jsonify({"msg": "não autorizado"}), 401

    if session.get('perfil') != 'admin':
        return jsonify({"msg": "acesso negado"}), 403

    conn = None
    cursor = None

    try:
        data = request.get_json() or {}

        user = (data.get('user') or "").strip()
        senha = (data.get('senha') or "").strip()
        perfil = (data.get('perfil') or "usuario").strip()

        if not user or not senha:
            return jsonify({"msg": "Preencha usuário e senha"}), 400

        conn, cursor = get_db()

        cursor.execute("SELECT id FROM usuarios WHERE user=%s", (user,))
        if cursor.fetchone():
            return jsonify({"msg": "Usuário já existe"}), 400

        # 🔐 HASH
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

        cursor.execute(
            "INSERT INTO usuarios (user, senha, perfil) VALUES (%s, %s, %s)",
            (user, senha_hash, perfil)
        )

        conn.commit()

        return jsonify({"msg": "Cadastrado com sucesso"})

    except Exception as e:
        print("ERRO cadastrar_usuario:", e)
        return jsonify({"msg": "Erro interno"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= INCLUSÃO DE TITULO =================
@app.route('/deferimento_titulo', methods=['POST'])
def deferimento_titulo():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        data = request.json or {}

        curso = (data.get("curso") or "").strip()

        resolucao = RESOLUCOES.get(curso, "RESOLUÇÃO NÃO IDENTIFICADA")

        texto = f"""INCLUSÃO DE TÍTULO DEFERIDA.
Informamos que o título de Técnico em {curso} encontra-se cadastrado em seu registro profissional. Para verificar suas atribuições técnicas, consulte a {resolucao}, onde constam as responsabilidades e diretrizes específicas para o exercício de sua profissão.

Para que o título incluso conste na carteira digital (imediatamente) ou na 1ª ou 2ª via da carteira física, será necessário realizar a inclusão do título.
Na guia FERRAMENTAS, selecione a opção "ALTERAR TÍTULOS IMPRESSOS NA CARTEIRA" e, posteriormente, escolha os títulos que deseja incluir e clique em SALVAR.

Em casos de 1ª ou 2ª via da carteira física, a atualização será possível caso o documento ainda não tenha sido emitido ou enviado.
"""

        # 🔥 REGRA DOS CURSOS
        curso_check = normalizar(curso)

        if any(x in curso_check for x in ["AGRIMENSURA", "GEODESIA", "CARTOGRAFIA", "GEOPROCESSAMENTO"]):
            texto += '\nComunicamos que deverá solicitar mediante o protocolo a "Revisão de atribuições em Georreferenciamento" caso deseje emitir TRTs para atividades de georreferenciamento.'

        # 🔥 SALVA HISTÓRICO
        conn, cursor = get_db()

        cursor.execute("""
            INSERT INTO historico (usuario, texto)
            VALUES (%s, %s)
        """, (
            session.get('user'),
            f"INCLUSÃO DE TÍTULO - {curso}"
        ))

        # 🔥 LOG
        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            "deferimento_titulo",
            f"Curso: {curso}"
        ))

        conn.commit()

        return jsonify({"texto": texto})

    except Exception as e:
        print("ERRO NO DEFERIMENTO TÍTULO:", e)
        return jsonify({"texto": "Erro interno no servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
@app.route('/log', methods=['POST'])
def log():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        data = request.json or {}

        acao = data.get('acao', 'acao_nao_informada')
        texto = data.get('texto', '')

        conn, cursor = get_db()

        cursor.execute("""
            INSERT INTO logs (usuario, acao, texto)
            VALUES (%s, %s, %s)
        """, (
            session.get('user'),
            acao,
            texto
        ))

        conn.commit()

        return jsonify({"ok": True})

    except Exception as e:
        print("ERRO LOG:", e)
        return jsonify({"erro": "falha ao salvar log"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/listar_logs')
def listar_logs():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    conn = None
    cursor = None

    try:
        conn, cursor = get_db()

        cursor.execute("""
            SELECT usuario, acao, texto, data
            FROM logs
            ORDER BY data DESC
            LIMIT 200
        """)

        dados = cursor.fetchall()

        lista = []

        for d in dados:
            lista.append({
                "usuario": d[0],
                "acao": d[1],
                "texto": d[2],
                "data": d[3].strftime("%d/%m/%Y %H:%M") if d[3] else ""
            })

        return jsonify(lista)

    except Exception as e:
        print("ERRO LISTAR LOGS:", e)
        return jsonify({"erro": "falha ao carregar logs"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/relatorio')
def relatorio():

    if 'user' not in session:
        return jsonify({"erro": "não logado"}), 401

    # 🔒 apenas admin
    if session.get('perfil') != 'admin':
        return jsonify({"erro": "sem permissão"}), 403

    conn = None
    cursor = None

    try:
        conn, cursor = get_db()

        cursor.execute("""
            SELECT usuario, COUNT(*) AS total
            FROM logs
            GROUP BY usuario
            ORDER BY total DESC
        """)

        dados = cursor.fetchall()

        lista = []

        for d in dados:
            lista.append({
                "usuario": d[0] or "Desconhecido",
                "acoes": int(d[1])
            })

        return jsonify(lista)

    except Exception as e:
        print("ERRO RELATORIO:", e)
        return jsonify({"erro": "falha ao gerar relatório"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ================= EXEC =================
if __name__ == '__main__':
    print("Rodando local...")
    app.run(debug=True)

