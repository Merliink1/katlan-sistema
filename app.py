from flask import Flask, render_template, request, redirect, session, jsonify
from datetime import datetime
import json, os, unicodedata

import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# ================= GOOGLE =================
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

CREDS = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", SCOPE)
CLIENT = gspread.authorize(CREDS)

PLANILHA = CLIENT.open_by_key("1HZk_CSqMU-0fotoQM0FRNcBqvgl8Oc0MFSg_OVUvm8U")
ABA = PLANILHA.get_worksheet(0)

# ================= FUNÇÕES =================
def carregar(arq):
    if not os.path.exists(arq):
        return []
    with open(arq, "r", encoding="utf-8") as f:
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
    salvar(ARQ_USUARIOS, [
        {"user": "admin", "senha": "123456", "perfil": "admin", "ativo": True}
    ])

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
        return redirect('/')

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

# ================= PLANILHA =================
@app.route('/planilha')
def planilha():
    return jsonify(ABA.get_all_records())

# ================= REGISTRAR =================
@app.route('/registrar', methods=['POST'])
def registrar():

    data = request.json

    headers = ABA.row_values(1)
    linha = [""] * len(headers)

    data_formatada = datetime.now().strftime("%d/%m/%Y")

    mapa = {
        "PROTOCOLO": data.get("protocolo"),
        "NOME DO INTERESSADO": data.get("nome"),
        "ESTADO": data.get("estado"),
        "TIPO DE REGISTRO": data.get("tipo"),
        "DATA DO REGISTRO": data_formatada,
        "STATUS": data.get("status")
    }

    for i, col in enumerate(headers):
        linha[i] = mapa.get(col.upper(), "")

    ABA.append_row(linha)

    return jsonify({"msg": "Salvo"})

# ================= DEFERIMENTO =================
@app.route('/deferimento', methods=['POST'])
def deferimento():

    data = request.json

    curso = normalizar(data.get("curso"))
    tipo = data.get("tipo")

    resolucao = RESOLUCOES.get(curso, "RESOLUÇÃO NÃO IDENTIFICADA")

    curso_formatado = curso.upper()
    resolucao_formatada = resolucao.upper()

    if tipo == "definitivo":

        texto = f"""REGISTRO DEFERIDO.
CADASTRO FINALIZADO E ATIVO. VOCÊ PODERÁ ACESSAR O SEU AMBIENTE PROFISSIONAL ATRAVÉS DA SENHA ENCAMINHADA POR E-MAIL. PARA VERIFICAR SUAS ATRIBUIÇÕES TÉCNICAS COM HABILITAÇÃO EM {curso}, CONSULTE A {resolucao}, ONDE CONSTAM AS RESPONSABILIDADES E DIRETRIZES ESPECÍFICAS PARA O EXERCÍCIO DE SUA PROFISSÃO. 

POR MEIO DE SEU AMBIENTE PROFISSIONAL SERÁ POSSÍVEL GERAR SUA ANUIDADE E, APÓS A COMPENSAÇÃO DO PAGAMENTO NO SISTEMA, PODERÁ EMITIR SUA CARTEIRA PROFISSIONAL. PARA MAIS INFORMAÇÕES SOBRE SUA ANUIDADE, ENTRE EM CONTATO PELO CANAL (98) 98279-0023.
"""

    else:

        texto = f"""REGISTRO DEFERIDO.
CADASTRO FINALIZADO E ATIVO. POR SE TRATAR DE REGISTRO PROVISÓRIO, O MESMO TERÁ VALIDADE DE 01 ANO PASSANDO A CONSTAR DA DATA DE EFETIVAÇÃO. VOCÊ PODERÁ ACESSAR O SEU AMBIENTE PROFISSIONAL ATRAVÉS DA SENHA ENCAMINHADA POR E-MAIL. PARA VERIFICAR SUAS ATRIBUIÇÕES TÉCNICAS COM HABILITAÇÃO EM {curso}, CONSULTE A {resolucao}, ONDE CONSTAM AS RESPONSABILIDADES E DIRETRIZES ESPECÍFICAS PARA O EXERCÍCIO DE SUA PROFISSÃO. 

POR MEIO DE SEU AMBIENTE PROFISSIONAL SERÁ POSSÍVEL GERAR SUA ANUIDADE E, APÓS A COMPENSAÇÃO DO PAGAMENTO NO SISTEMA, PODERÁ EMITIR SUA CERTIDÃO DE QUITAÇÃO DE PESSOA FÍSICA E TER ACESSO A SUA CARTEIRA PROFISSIONAL DIGITAL. PARA MAIS INFORMAÇÕES SOBRE SUA ANUIDADE, ENTRE EM CONTATO PELO CANAL (98) 98279-0023.
"""

    return jsonify({"texto": texto})

# ================= USUÁRIOS =================
@app.route('/usuarios')
def usuarios():
    return jsonify(carregar(ARQ_USUARIOS))

@app.route('/listar_usuarios')
def listar_usuarios():
    usuarios = carregar(ARQ_USUARIOS)

    # 🔥 garante campo ativo em todos
    for u in usuarios:
        if 'ativo' not in u:
            u['ativo'] = True

    salvar(ARQ_USUARIOS, usuarios)

    return jsonify(usuarios)

@app.route('/alterar_senha', methods=['POST'])
def alterar_senha():

    data = request.json
    usuarios = carregar(ARQ_USUARIOS)

    for u in usuarios:
        if u['user'] == data.get('user'):
            u['senha'] = data.get('senha')
            break

    salvar(ARQ_USUARIOS, usuarios)

    return jsonify({"msg": "Senha atualizada"})


@app.route('/excluir_usuario', methods=['POST'])
def excluir_usuario():

    data = request.json
    usuarios = carregar(ARQ_USUARIOS)

    usuarios = [u for u in usuarios if u['user'] != data.get('user')]

    salvar(ARQ_USUARIOS, usuarios)

    return jsonify({"msg": "Excluído"})

@app.route('/toggle_usuario', methods=['POST'])
def toggle_usuario():

    data = request.json
    usuarios = carregar(ARQ_USUARIOS)

    for u in usuarios:
        if u.get('user') == data.get('user'):

            # 🔥 garante campo ativo
            atual = u.get('ativo', True)
            u['ativo'] = not atual

    salvar(ARQ_USUARIOS, usuarios)

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

# ================= EXEC =================
if __name__ == "__main__":
    app.run()