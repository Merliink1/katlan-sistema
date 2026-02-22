from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime
import json, os, unicodedata

# ================= CONFIG =================
app = Flask(__name__, static_folder='static')
app.secret_key = 'derc_pf_secret'

DATA_PATH = "database"

if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

ARQ_USUARIOS = os.path.join(DATA_PATH, "usuarios.json")
ARQ_ACESSOS = os.path.join(DATA_PATH, "acessos.json")
ARQ_ANALISES = os.path.join(DATA_PATH, "historico.json")
ARQ_CHAT = os.path.join(DATA_PATH, "chat.json")

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

# ================= USUÁRIO PADRÃO =================
if not os.path.exists(ARQ_USUARIOS):
    with open(ARQ_USUARIOS, 'w') as f:
        json.dump([
            {
                "user": "admin",
                "senha": "123",
                "perfil": "admin",
                "ativo": True
            }
        ], f)
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

    user = request.form.get('user')
    senha = request.form.get('senha')

    usuarios = carregar(ARQ_USUARIOS)

    # 👇 COLOCA AQUI
    print("USUÁRIO:", user)
    print("SENHA:", senha)
    print("ARQ:", ARQ_USUARIOS)
    print("DADOS:", usuarios)

    for u in usuarios:
        if u['user'] == user and u['senha'] == senha:

            if not u.get("ativo", True):
                return render_template('login.html', erro="Usuário desativado")

            session['user'] = user
            session['perfil'] = u.get('perfil', 'user')
            session['login_time'] = str(datetime.now())

            return redirect('/sistema')

    return render_template('login.html', erro="Usuário ou senha inválidos")

# ================= SISTEMA =================
@app.route('/sistema')
def sistema():

    if 'user' not in session:
        from flask import url_for

        return redirect(url_for('sistema'))

    return render_template('sistema.html',
                           usuario=session['user'],
                           cursos=RESOLUCOES.keys())

# ================= LOGOUT =================
@app.route('/logout')
def logout():

    acessos = carregar(ARQ_ACESSOS)

    acessos.append({
        "usuario": session.get('user'),
        "entrada": session.get('login_time'),
        "saida": str(datetime.now())
    })

    salvar(ARQ_ACESSOS, acessos)

    session.clear()
    return redirect('/')

# ================= CHAT =================
@app.route('/chat_enviar', methods=['POST'])
def chat_enviar():

    if 'user' not in session:
        return jsonify({"erro": "não logado"})

    data = request.json
    chat = carregar(ARQ_CHAT)

    chat.append({
        "usuario": session.get('user'),
        "mensagem": data.get("mensagem"),
        "hora": datetime.now().strftime("%H:%M")
    })

    salvar(ARQ_CHAT, chat)

    return jsonify({"ok": True})

@app.route('/chat_listar')
def chat_listar():
    return jsonify(carregar(ARQ_CHAT))

# ================= REGISTRAR =================
@app.route('/registrar', methods=['POST'])
def registrar():

    data = request.json
    historico = carregar(ARQ_ANALISES)

    historico.append({
        "protocolo": data.get("protocolo"),
        "nome": data.get("nome"),
        "estado": data.get("estado"),
        "tipo": data.get("tipo"),
        "status": data.get("status"),
        "data": datetime.now().strftime("%d/%m/%Y")
    })

    salvar(ARQ_ANALISES, historico)

    return jsonify({"msg": "Salvo"})

# ================= DEFERIMENTO =================
@app.route('/deferimento', methods=['POST'])
def deferimento():

    try:
        data = request.json or {}

        curso = data.get("curso") or ""
        tipo = data.get("tipo") or ""

        curso = curso.strip()

        resolucao = RESOLUCOES.get(curso, "RESOLUÇÃO NÃO IDENTIFICADA")

        if tipo == "definitivo":

            texto = f"""REGISTRO DEFERIDO.
Cadastro finalizado e ATIVO. Você poderá acessar o seu ambiente profissional através da senha encaminhada por e-mail. Para verificar suas atribuições técnicas com habilitação em {curso}, consulte a {resolucao}, onde constam as responsabilidades e diretrizes específicas para o exercício de sua profissão.

Por meio de seu ambiente profissional será possível gerar sua anuidade e, após a compensação do pagamento no sistema, poderá emitir sua carteira profissional. Para mais informações sobre sua anuidade, entre em contato pelo canal (98) 98279-0023.
"""

        else:

            texto = f"""REGISTRO DEFERIDO.
Cadastro finalizado e ATIVO. Por se tratar de Registro Provisório, o mesmo terá validade de 01 ano passando a constar da data de efetivação. Você poderá acessar o seu ambiente profissional através da senha encaminhada por e-mail. Para verificar suas atribuições técnicas com habilitação em {curso}, consulte a {resolucao}, onde constam as responsabilidades e diretrizes específicas para o exercício de sua profissão.

Por meio de seu ambiente profissional será possível gerar sua anuidade e, após a compensação do pagamento no sistema, poderá emitir sua certidão de quitação de pessoa física e ter acesso a sua carteira profissional digital. Para mais informações sobre sua anuidade, entre em contato pelo canal  (98) 98279-0023
"""

        return jsonify({"texto": texto})

    except Exception as e:
        print("ERRO NO DEFERIMENTO:", e)
        return jsonify({"texto": "Erro interno no servidor"}), 500

# ================= USUÁRIOS =================
@app.route('/listar_usuarios')
def listar_usuarios():

    cursor.execute("SELECT user, perfil, ativo FROM usuarios")
    dados = cursor.fetchall()

    lista = []

    for u in dados:
        lista.append({
            "user": u[0],
            "perfil": u[1],
            "ativo": u[2]
        })

    return jsonify(lista)

@app.route('/alterar_senha', methods=['POST'])
def alterar_senha():

    data = request.json

    cursor.execute(
        "UPDATE usuarios SET senha=%s WHERE user=%s",
        (data.get('senha'), data.get('user'))
    )

    conn.commit()

    return jsonify({"msg": "Senha atualizada"})

@app.route('/excluir_usuario', methods=['POST'])
def excluir_usuario():

    data = request.json

    cursor.execute(
        "DELETE FROM usuarios WHERE user=%s",
        (data.get('user'),)
    )

    conn.commit()

    return jsonify({"msg": "Excluído"})

@app.route('/toggle_usuario', methods=['POST'])
def toggle_usuario():

    data = request.json
    user = data.get('user')

    cursor.execute("SELECT ativo FROM usuarios WHERE user=%s", (user,))
    atual = cursor.fetchone()

    if atual:
        novo = not atual[0]

        cursor.execute(
            "UPDATE usuarios SET ativo=%s WHERE user=%s",
            (novo, user)
        )

        conn.commit()

    return jsonify({"msg": "Atualizado"})
    
# ================= HISTÓRICO =================
@app.route('/salvar_analise', methods=['POST'])
def salvar_analise():

    data = request.json
    historico = carregar(ARQ_ANALISES)

    historico.append({
        "usuario": session.get('user'),
        "data": str(datetime.now()),
        "texto": data.get("texto")
    })

    salvar(ARQ_ANALISES, historico)

    return jsonify({"msg": "ok"})

@app.route('/historico')
def historico():
    return jsonify(carregar(ARQ_ANALISES))

# ================= CADASTRAR USUARIO =================
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"msg": "Dados inválidos"}), 400

        user = data.get('user')
        senha = data.get('senha')
        perfil = data.get('perfil')

        if not user or not senha:
            return jsonify({"msg": "Preencha usuário e senha"}), 400

        usuarios = carregar(ARQ_USUARIOS)

        if usuarios is None:
            usuarios = []

        # evitar duplicado
        for u in usuarios:
            if u['user'] == user:
                return jsonify({"msg": "Usuário já existe"}), 400

        usuarios.append({
            "user": user,
            "senha": senha,
            "perfil": perfil,
            "ativo": True
        })

        salvar(ARQ_USUARIOS, usuarios)

        return jsonify({"msg": "Cadastrado com sucesso"})

    except Exception as e:
        print("ERRO cadastrar_usuario:", e)
        return jsonify({"msg": str(e)}), 500

# ================= INCLUSÃO DE TITULO =================
@app.route('/deferimento_titulo', methods=['POST'])
def deferimento_titulo():

    try:
        data = request.json or {}

        curso = data.get("curso") or ""
        curso = curso.strip()

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

        return jsonify({"texto": texto})

    except Exception as e:
        print("ERRO NO DEFERIMENTO TÍTULO:", e)
        return jsonify({"texto": "Erro interno no servidor"}), 500

# ================= EXEC =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


