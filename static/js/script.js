// ================= CONTROLE DE TELAS =================
function abrir(id, btn){

    document.querySelectorAll('.card').forEach(el=>{
        el.classList.add('hidden');
    });

    document.querySelectorAll('.menu-lateral button').forEach(b=>{
        b.classList.remove('active');
    });

    let tela = document.getElementById(id);
    if(tela) tela.classList.remove('hidden');

    if(btn){
        btn.classList.add('active');
    }

    if(id === 'analiseUnica'){
        montarAnaliseUnica();
    }

    if(id === 'analiseSimultanea'){
        montarAnaliseSimultanea();
    }

    if(id === 'admin'){
        carregarUsuarios();
    }

    if(id === 'interrupcaoRegistro'){
    carregarSelectIndeferimento();
    carregarSelectDeferimento();
}
}

// ================= LOGOUT =================
function logout(){
    window.location = "/logout";
}

// ================= DARK MODE =================
function toggleDark(){
    document.body.classList.toggle("dark");

    if(document.body.classList.contains("dark")){
        localStorage.setItem("dark","1");
    }else{
        localStorage.removeItem("dark");
    }
}

// ================= DATA =================
function atualizarHora(){
    let el = document.getElementById("dataHora");
    if(!el) return;

    setInterval(()=>{
        let agora = new Date();
        el.innerHTML = agora.toLocaleString();
    },1000);
}

// ================= COPIAR =================
function copiarTexto(id){
    let el = document.getElementById(id);
    if(!el) return;

    let texto = el.value;

    navigator.clipboard.writeText(texto)
    .then(()=>alert("Copiado com sucesso"))
    .catch(()=>alert("Erro ao copiar"));
}

// ================= CHAT =================
let ultimaQtdMsg = 0;

function enviarChat(){

    let input = document.getElementById("chatInput") || document.getElementById("chatInput2");
    if(!input) return;

    let msg = input.value.trim();
    if(!msg) return;

    fetch("/chat_enviar",{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({mensagem:msg})
    })
    .then(()=>{
        input.value="";
        carregarChat();
    });
}

function carregarChat(){

    fetch("/chat_listar")
    .then(r=>r.json())
    .then(lista=>{

        let div1 = document.getElementById("chatMensagens");
        let div2 = document.getElementById("chatMensagens2");

        let html = "";

        lista.slice(-50).forEach(m=>{
            html += `<div><b>${m.usuario}</b> (${m.hora})<br>${m.mensagem}</div>`;
        });

        if(div1) div1.innerHTML = html;
        if(div2) div2.innerHTML = html;

        if(lista.length > ultimaQtdMsg){
            mostrarNotificacao();
        }

        ultimaQtdMsg = lista.length;
    });
}

function mostrarNotificacao(){
    let notif = document.getElementById("notif");
    if(!notif) return;

    notif.classList.remove("hidden");

    setTimeout(()=>{
        notif.classList.add("hidden");
    },3000);
}

// ================= BASE =================
const DESPACHOS = {

    // ================= DIPLOMA =================
    diploma_sistec:{
        titulo:"Diploma sem validação no SISTEC/MEC",
        texto:`O seu diploma não está registrado no SISTEC/MEC. Por isso, solicitamos que entre em contato com a sua instituição de ensino para que o cadastro seja realizado no sistema do MEC. Caso necessário, requisitamos à instituição um ofício que ratifique os documentos apresentados.`
    },

    diploma_antigo:{
        titulo:"Diploma emitido antes da criação do SISTEC",
        texto:`Identificamos que seu diploma não se encontra cadastrado no SISTEC/MEC, devido à sua emissão ter sido anterior à criação deste sistema pelo Ministério da Educação (MEC) em 2009, conforme estabelecido pela Resolução CNE/CEB nº 3/2009. Solicitamos que entre em contato com a instituição de ensino responsável e solicite o cadastro do mesmo junto ao sistema do MEC ou que encaminhe um documento (declaração de veracidade/ofício) informando a confirmação de aluno egresso ao e-mail dercpf@crt02.gov.br. Adicionalmente, entraremos em contato solicitando que a instituição de ensino emita um ofício para ratificar os documentos, se porventura necessário.`
    },

    diploma_incompleto:{
        titulo:"Diploma incompleto",
        texto:`Diploma do curso técnico deve ser enviado frente e verso.`
    },

    diploma_ilegivel:{
        titulo:"Diploma ilegível",
        texto:`Diploma do curso técnico está com os dados ilegíveis, portanto encaminhar diploma do curso técnico frente e verso em uma imagem de melhor qualidade.`
    },

    diploma_curso_diferente:{
        titulo:"Curso diferente",
        texto:`Comunicamos que o curso apresentado no diploma não corresponde com a nomenclatura do curso apresentada no SISTEC/MEC. Sendo assim, solicitamos que entre em contato com a instituição de ensino e peça a correção. Estamos aguardando o retorno das informações acerca dos dados apresentados.`
    },

    diploma_codigo_diferente:{
        titulo:"Código diferente",
        texto:`Comunicamos que o código apresentado no diploma não corresponde com o código no SISTEC/MEC. Sendo assim, solicitamos que entre em contato com a instituição de ensino e peça a correção. Estamos aguardando o retorno das informações acerca dos dados apresentados.`
    },

    diploma_instituicao_extinta:{
        titulo:"Instituição deixou de existir",
        texto:`Tendo em vista que a instituição de ensino em que se formou deixou de existir, conforme a resolução 141/2021, Art.12º §1, do qual informa que em casos que as escolas que já não existam, caberá ao profissional buscar os meios legais para obter tais documentos, através das Secretarias Estaduais de Educação que deverão encaminhar o documento (declaração de veracidade/ofício) informando a confirmação de aluno egresso ao e-mail dercpf@crt02.gov.br. Portanto o protocolo ficará aberto dentre o prazo de 30 dias aguardando resposta, se o processo de documentação demorar além do prazo, poderá entrar em contato com o telefone (98) 98279-0023 solicitando a reabertura do protocolo.`
    },

    diploma_carga_horaria:{
        titulo:"Carga horária inferior",
        texto:`O diploma do curso técnico deve atender à carga horária mínima exigida pelo Catálogo Nacional de Cursos Técnicos (CNCT), conforme a Resolução CNE/CP nº 1, de 5 de janeiro de 2021.`
    },

    diploma_nao_tecnico:{
        titulo:"Diploma não é de curso técnico",
        texto:`O diploma apresentado não é considerado diploma de curso técnico, por não atender às diretrizes da Educação Profissional Técnica de Nível Médio estabelecidas pelo MEC, conforme a Resolução CNE/CP nº 1, de 5 de janeiro de 2021, e o Catálogo Nacional de Cursos Técnicos (CNCT).`
    },

    diploma_print:{
        titulo:"Captura de tela",
        texto:`Captura de tela não é aceito, portanto encaminhe o documento do diploma do curso técnico frente e verso.`
    },

    // ================= DECLARAÇÃO =================
    declaracao_egresso:{
        titulo:"Declaração de egresso",
        texto:`Encaminhamos uma solicitação de informação de aluno egresso para a instituição de ensino e estamos aguardando o retorno das informações.`
    },

    declaracao_desatualizada:{
        titulo:"Declaração desatualizada",
        texto:`Encaminhe uma declaração de conclusão de curso atualizada com data válida.`
    },

    // ================= HISTÓRICO =================
    historico_completo:{
        titulo:"Histórico completo e assinado",
        texto:`Histórico do curso técnico completo contendo todas as páginas e assinado pela instituição de ensino.`
    },

    historico_divergente:{
        titulo:"Divergência entre histórico e diploma",
        texto:`O curso informado no histórico escolar diverge do curso constante no diploma. Recomenda-se contatar a instituição de ensino para que sejam realizadas as devidas correções.`
    },

    historico_ilegivel:{
        titulo:"Histórico ilegível",
        texto:`O histórico do curso técnico apresentado está com os dados ilegíveis, portanto encaminhe novamente o histórico do curso técnico em uma imagem de melhor qualidade.`
    },

    historico_print:{
        titulo:"Captura de tela",
        texto:`Captura de tela não é aceito, portanto encaminhe o documento do histórico do curso técnico.`
    },

    // ================= IDENTIDADE =================
    id_frente_verso:{
        titulo:"Documento frente e verso",
        texto:`Documento de identificação com foto deve ser enviado frente e verso.`
    },

    id_foto_antiga:{
        titulo:"Foto desatualizada",
        texto:`Sua carteira de identidade civil (RG) contém foto desatualizada. Devido ao decurso do tempo, a foto do documento não expressa a identificação da pessoa que o porta, portanto não poderá ser aceito. Solicitamos o envio de outro documento de identificação com foto válido em todo o Território Nacional.`
    },

    id_ilegivel:{
        titulo:"Documento ilegível",
        texto:`Seu documento de identificação com foto consta com os dados ilegíveis, portanto encaminhe novamente o documento em uma imagem de melhor qualidade.`
    },

    id_print:{
        titulo:"Print de tela",
        texto:`Print de tela não é aceito, portanto encaminhe o documento de identificação com foto frente e verso.`
    },

    id_rg_desatualizado:{
        titulo:"RG desatualizada",
        texto:`Sua Carteira de Identidade Civil (RG), com data de expedição em {data} está desatualizada. Apresente um novo documento, de acordo com o Decreto nº 10.977, de 23 de fevereiro de 2022 ou outro documento de identificação com foto válido em todo o Território Nacional.`,
        precisaData:true
    },

    // ================= RESIDÊNCIA =================
    res_desatualizado:{
        titulo:"Comprovante desatualizado",
        texto:`O comprovante de residência encaminhado encontra-se desatualizado. Portanto solicitamos que encaminhe um comprovante de residência em seu nome ou no nome dos seus pais com data máxima de 90 dias ou encaminhe uma declaração de residência de próprio punho preenchida pelo solicitante do registro profissional. Link de acesso ao modelo de declaração:
https://drive.google.com/file/d/1o_0_3avoY0ZVdZICBq1MeZ6NQIfTZUDn/view?usp=sharing`
    },

    res_terceiro:{
        titulo:"Em nome de terceiro",
        texto:`O comprovante de residência encaminhado encontra-se em nome de terceiros. Portanto solicitamos que encaminhe um comprovante de residência em seu nome ou no nome dos seus pais com data máxima de 90 dias ou encaminhe uma declaração de residência de próprio punho preenchida pelo solicitante do registro profissional. Link de acesso ao modelo de declaração: https://drive.google.com/file/d/1o_0_3avoY0ZVdZICBq1MeZ6NQIfTZUDn/view?usp=sharing`
    },

    res_nota:{
        titulo:"Nota fiscal não é aceito",
        texto:`Nota fiscal não é aceito como comprovante de residência. Portanto encaminhe um comprovante de residência em seu nome ou no nome dos seus pais com data máxima de 90 dias ou encaminhe uma declaração de residência de próprio punho preenchida pelo solicitante do registro profissional. Link de acesso ao modelo de declaração: https://drive.google.com/file/d/1o_0_3avoY0ZVdZICBq1MeZ6NQIfTZUDn/view?usp=sharing`
    },

    res_declaracao_errada:{
        titulo:"Declaração assinada por terceiro",
        texto:`A declaração de residência deve ser preenchida e assinada pelo próprio solicitante. Não é necessário que outra pessoa ateste ou confirme que o solicitante reside no endereço informado. Link de acesso ao modelo de declaração: https://drive.google.com/file/d/1o_0_3avoY0ZVdZICBq1MeZ6NQIfTZUDn/view?usp=sharing`
    },

    res_print:{
        titulo:"Print de tela",
        texto:`Print de tela não é aceito, portanto encaminhe o documento do comprovante de residência atualizado.`
    },

    res_declaracao_incompleta:{
        titulo:"Declaração incompleta",
        texto:`A declaração de residência deve ser corretamente preenchida, contendo todos os dados obrigatórios, como CEP, logradouro, data, local e assinatura do solicitante. Link de acesso ao modelo de declaração: https://drive.google.com/file/d/1o_0_3avoY0ZVdZICBq1MeZ6NQIfTZUDn/view?usp=sharing`
    },

    res_ilegivel:{
        titulo:"Comprovante ilegível",
        texto:`Comprovante de residência consta com os dados de endereço ilegíveis, portanto encaminhe novamente o documento em uma imagem de melhor qualidade.`
    },

    res_pagamento:{
        titulo:"Comprovante de pagamento",
        texto:`Comprovante de pagamento não é aceito como comprovante de residência. Portanto encaminhe um comprovante de residência em seu nome ou no nome dos seus pais com data máxima de 90 dias ou encaminhe uma declaração de residência de próprio punho preenchida pelo solicitante do registro profissional. Link de acesso ao modelo de declaração: https://drive.google.com/file/d/1o_0_3avoY0ZVdZICBq1MeZ6NQIfTZUDn/view?usp=sharing`
    },

    res_sem:{
        titulo:"Sem comprovante",
        texto:`Encaminhe um comprovante de residência em seu nome ou no nome dos seus pais com data máxima de 90 dias ou encaminhe uma declaração de residência de próprio punho preenchida pelo solicitante do registro profissional. Link de acesso ao modelo de declaração: https://drive.google.com/file/d/1o_0_3avoY0ZVdZICBq1MeZ6NQIfTZUDn/view?usp=sharing`
    },

    // ================= FOTO =================
    foto_padrao:{
        titulo:"Foto desatualizada",
        texto:`A foto deverá estar no formato 3x4, atualizada e seguindo o padrão de fotografia para a documentação. O rosto deve estar em evidência, ombros alinhados, fundo branco, boa qualidade de imagem e sem sombras. Segue o modelo de fotografia exigido: https://drive.google.com/file/d/12Gb2_DKVXMYQGj2_UTPm3RYa1Sae-BAs/view?usp=sharing`
    },

    // ================= TÍTULO DE ELEITOR =================
    titulo_incompleto:{
        titulo:"Título de eleitor incompleto",
        texto:`O título de eleitor deve ser encaminhado frente e verso.`
    },

    titulo_print:{
        titulo:"Print não aceito",
        texto:`Captura de tela não é aceita. Encaminhe o documento completo.`
    },

    // ================= CERTIDÃO ELEITORAL =================
    eleitor_ausencia:{
        titulo:"Ausência às urnas",
        texto:`A Certidão de Quitação Eleitoral apresentada informa que você não está quite com a justiça eleitoral devido a ausência às urnas. Portanto verifique a sua situação com a justiça eleitoral e posteriormente encaminhe a documentação atualizada.`
    },

    eleitor_desatualizado:{
        titulo:"Desatualização",
        texto:`A Certidão de Quitação Eleitoral apresentada está desatualizada portanto, verifique a sua situação com a justiça eleitoral e posteriormente encaminhe a documentação atualizada.`
    },

    eleitor_print:{
        titulo:"Captura de tela não é aceito",
        texto:`Print de tela não é aceito, portanto encaminhe o documento do título de eleitor frente e verso.`
    },

    eleitor_comprovante:{
        titulo:"Comprovante de votação não é aceito",
        texto:`Comprovante de votação não é aceito como certidão de quitação eleitoral. Portanto verifique a sua situação com a justiça eleitoral e posteriormente encaminhe a documentação atualizada.`
    },

    eleitor_requerimento:{
        titulo:"Requerimento de Votação não é aceito",
        texto:`Requerimento de Votação não é aceito como certidão de quitação eleitoral. Portanto verifique a sua situação com a justiça eleitoral e posteriormente encaminhe a documentação atualizada.`
    },

    eleitor_crimes:{
        titulo:"Certidão de crimes eleitorais não é aceito",
        texto:`Certidão de crimes eleitorais não é aceito como certidão de quitação eleitoral. Portanto verifique a sua situação com a justiça eleitoral e posteriormente encaminhe a documentação atualizada.`
    },

    eleitor_antecedentes:{
        titulo:"Certidão de antecedentes criminais não é aceito",
        texto:`Certidão de antecedentes criminais não é aceito como certidão de quitação eleitoral. Portanto verifique a sua situação com a justiça eleitoral e posteriormente encaminhe a documentação atualizada.`
    },

    // ================= MILITAR =================
    militar_sem:{
        titulo:"Documento não apresentado",
        texto:`Apresente documento que comprove a regularidade com o serviço militar.`
    },

    militar_invalido:{
        titulo:"Documento inválido",
        texto:`O documento militar apresentado está inválido. Encaminhe documento atualizado.`
    },

    militar_sem_carimbo:{
        titulo:"Sem carimbo",
        texto:`O certificado de reservista encaminhado não se encontra com os carimbos conforme informações no verso. Solicitamos que verifique sua situação junto ao órgão competente e posteriormente encaminhe a documentação atualizada.`
    },

    militar_print:{
        titulo:"Print não aceito",
        texto:`Captura de tela não é aceita como documento militar.`
    },

    militar_incompleto:{
        titulo: "Militar incompleto",
        texto:`A prova de quitação militar apresentada está incompleta. Encaminhe o documento completo constando frente e verso.`
    }

};

// ================= ESTADO =================
let selecoesUnica = [];
let selecoesSim = {};

// ================= ANALISE UNICA =================

const ICONES = {

    diploma: `
    <svg viewBox="0 0 24 24">
        <path d="M6 2h9l5 5v15H6z"/>
        <path d="M9 9h6M9 13h6M9 17h4"/>
    </svg>
    `,

    declaracao: `
    <svg viewBox="0 0 24 24">
        <path d="M4 4h16v16H4z"/>
        <path d="M8 8h8M8 12h8M8 16h5"/>
    </svg>
    `,

    historico: `
    <svg viewBox="0 0 24 24">
        <path d="M3 5h18v14H3z"/>
        <path d="M7 9h10M7 13h10"/>
    </svg>
    `,

    id: `
    <svg viewBox="0 0 24 24">
        <rect x="2" y="6" width="20" height="12"/>
        <circle cx="8" cy="12" r="2"/>
        <path d="M12 10h6M12 14h4"/>
    </svg>
    `,

    foto: `
    <svg viewBox="0 0 24 24">
        <rect x="3" y="5" width="18" height="14"/>
        <circle cx="12" cy="12" r="3"/>
    </svg>
    `,

    titulo: `
    <svg viewBox="0 0 24 24">
        <path d="M3 6h18v12H3z"/>
        <path d="M8 10h8M8 14h5"/>
    </svg>
    `,

    eleitor: `
    <svg viewBox="0 0 24 24">
        <path d="M20 6L9 17l-5-5"/>
    </svg>
    `,

    res: `
    <svg viewBox="0 0 24 24">
        <path d="M3 10L12 3l9 7v10H3z"/>
    </svg>
    `,

    militar: `
    <svg viewBox="0 0 24 24">
        <path d="M12 2l3 6 6 .9-4.5 4.4 1 6.7-5.5-3-5.5 3 1-6.7L3 8.9 9 8z"/>
    </svg>
    `
};

function montarAnaliseUnica(){

    selecoesUnica = [];

    let area = document.getElementById("areaUnica");

    area.innerHTML = `

    <div class="card-topo">
        <strong>PROFISSIONAL</strong>

        <div class="acoes">
            <button class="btn-copiar" onclick="copiarTexto('saidaUnica')">COPIAR</button>
            <button class="btn-limpar" onclick="limparAnaliseUnica()">LIMPAR</button>
        </div>
    </div>

    <input id="nomeUnico" placeholder="Nome do profissional" oninput="atualizarUnica()">

    <div id="listaUnica" class="tags"></div>

    <!-- CAMPOS -->
    <div class="grid-unica">

        ${campoUnico("Diploma","diploma",`
        <svg viewBox="0 0 24 24">
        <path d="M6 2h9l5 5v15H6z"/>
        </svg>
        `)}

        ${campoUnico("Declaração","declaracao",`
        <svg viewBox="0 0 24 24">
        <path d="M6 2h12v20H6z"/>
        </svg>
        `)}

        ${campoUnico("Histórico","historico",`
        <svg viewBox="0 0 24 24">
        <path d="M4 4h16v16H4z"/>
        </svg>
        `)}

        ${campoUnico("Identidade","id",`
        <svg viewBox="0 0 24 24">
        <rect x="2" y="5" width="20" height="14"/>
        <circle cx="8" cy="12" r="2"/>
        </svg>
        `)}

        ${campoUnico("Foto","foto",`
        <svg viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="4"/>
        </svg>
        `)}

        ${campoUnico("Tít. Eleitor","titulo",`
        <svg viewBox="0 0 24 24">
        <path d="M3 6h18v12H3z"/>
        </svg>
        `)}

        ${campoUnico("Quitação Eleitoral","eleitor",`
        <svg viewBox="0 0 24 24">
        <path d="M20 6L9 17l-5-5"/>
        </svg>
        `)}

        ${campoUnico("Residência","res",`
        <svg viewBox="0 0 24 24">
        <path d="M3 10L12 3l9 7v10H3z"/>
        </svg>
        `)}

        ${campoUnico("Serv. Militar","militar",`
        <svg viewBox="0 0 24 24">
        <path d="M12 2l3 6 6 .9-4.5 4.4 1 6.7-5.5-3-5.5 3 1-6.7L3 8.9 9 8z"/>
        </svg>
        `)}

    </div>

    <textarea id="saidaUnica" placeholder="Selecione as pendências..."></textarea>
    `;
}

function campoUnico(nome,tipo,icone){
    return `
    <div class="item">

        <label>
            ${icone}
            <strong>${nome}</strong>
        </label>

        <select onchange="addTextoUnico(this)">
            <option value="">Selecionar</option>

            ${Object.entries(DESPACHOS)
                .filter(([k])=>k.startsWith(tipo + "_"))
                .map(([k,v])=>`<option value="${k}">${v.titulo}</option>`)
                .join("")}

        </select>

    </div>`;
}


function addTextoUnico(sel){

    let key = sel.value;
    if(!key) return;

    let item = DESPACHOS[key];

    if(item.precisaData){
        abrirModalData((data)=>{
            let texto = item.texto.replace("{data}",data);
            adicionarItemUnico(item.titulo,texto);
        });
    }else{
        adicionarItemUnico(item.titulo,item.texto);
    }

    sel.selectedIndex = 0;
}

function atualizarUnica(){

    let nomeEl = document.getElementById("nomeUnico");
    let area = document.getElementById("saidaUnica");
    let lista = document.getElementById("listaUnica");

    if(!area || !lista) return;

    let nome = nomeEl ? nomeEl.value : "";

    // TAGS
    lista.innerHTML = selecoesUnica.map((item,i)=>`
        <div class="tag">
            ${item.titulo} 
            <b onclick="removerUnica(${i})">x</b>
        </div>
    `).join("");

    // TEXTO BASE
    let texto = `Prezado(a) ${nome},\n\n`;

    if(selecoesUnica.length > 0){

        texto += "Após análise da solicitação, foram identificadas as seguintes pendências:\n\n";

        selecoesUnica.forEach((item,i)=>{

            let base = item.texto.trim();

            // remove ponto final se existir
            if(base.endsWith(".")){
                base = base.slice(0, -1);
            }

            // ultimo item = ponto
            let final = (i === selecoesUnica.length - 1) ? "." : ";";

            texto += `${i+1}. ${base}${final}\n\n`;
        });

        texto += "Dessa forma, solicitamos o envio da documentação pendente para continuidade da análise da solicitação.";
    }

    area.value = texto;
}

function removerUnica(i){
    selecoesUnica.splice(i,1);
    atualizarUnica();
}

function limparAnaliseUnica(){

    selecoesUnica = [];

    let nome = document.getElementById("nomeUnico");
    let area = document.getElementById("saidaUnica");
    let lista = document.getElementById("listaUnica");

    if(nome) nome.value="";
    if(area) area.value="";
    if(lista) lista.innerHTML="";
}

function adicionarItemUnico(titulo,texto){

    if(selecoesUnica.find(i=>i.titulo===titulo)) return;

    selecoesUnica.push({titulo,texto});
    atualizarUnica();
}

// ================= ANALISE SIMULTANEA =================
function montarAnaliseSimultanea(){

    let container = document.getElementById("containerAnalise");
    container.innerHTML = "";

    for(let i=1;i<=6;i++){

        selecoesSim[i]=[];

        let div = document.createElement("div");
        div.className="cardAnalise";

        div.innerHTML=`
        
        <div class="card-topo">
            <strong>PROFISSIONAL ${i}</strong>

            <div class="acoes">
                <button class="btn-copiar" onclick="copiarTexto('saida${i}')">COPIAR</button>
                <button class="btn-limpar" onclick="limparSim(${i})">LIMPAR</button>
            </div>
        </div>

        <input id="nome${i}" placeholder="Nome" oninput="atualizarSim(${i})">

        <div id="lista${i}" class="tags"></div>

        ${campoSim(i,"Diploma","diploma")}
        ${campoSim(i,"Declaração","declaracao")}
        ${campoSim(i,"Histórico","historico")}
        ${campoSim(i,"Identidade","id")}
        ${campoSim(i,"Foto","foto")}
        ${campoSim(i,"Residência","res")}
        ${campoSim(i,"Título de Eleitor","titulo")}
        ${campoSim(i,"Quitação Eleitoral","eleitor")}
        ${campoSim(i,"Militar","militar")}

        <textarea id="saida${i}" placeholder="Selecione as pendências..."></textarea>
        `;

        container.appendChild(div);
    }
}

function campoSim(i,nome,tipo){
    return `
    <div class="item">

        <label>
            ${icone(tipo)}
            <span>${nome}</span>
        </label>

        <select onchange="addTextoSim(this,${i})">
            <option value="">Selecionar</option>

            ${Object.entries(DESPACHOS)
                .filter(([k]) => k.startsWith(tipo + "_"))
                .map(([k,v])=>`<option value="${k}">${v.titulo}</option>`)
                .join("")}

        </select>

    </div>`;
}

function icone(tipo){

    const icones = {

        diploma:`<svg viewBox="0 0 24 24"><path d="M4 4h16v16H4z"/></svg>`,

        declaracao:`<svg viewBox="0 0 24 24"><path d="M6 2h9l5 5v15H6z"/></svg>`,

        historico:`<svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10"/></svg>`,

        id:`<svg viewBox="0 0 24 24"><path d="M3 5h18v14H3zM7 10h4"/></svg>`,

        foto:`<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/></svg>`,

        res:`<svg viewBox="0 0 24 24"><path d="M3 10L12 3l9 7v10H3z"/></svg>`,

        titulo:`<svg viewBox="0 0 24 24"><path d="M6 2h12v20H6z"/></svg>`,

        eleitor:`<svg viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>`,

        militar:`<svg viewBox="0 0 24 24"><path d="M12 2l8 4-8 4-8-4z"/></svg>`
    };

    return icones[tipo] || "";
}
function addTextoSim(sel,i){

    let key = sel.value;
    if(!key) return;

    let item = DESPACHOS[key];

    if(item.precisaData){
        abrirModalData((data)=>{
            let texto = item.texto.replace("{data}",data);
            adicionarItemSim(i,item.titulo,texto);
        });
    }else{
        adicionarItemSim(i,item.titulo,item.texto);
    }

    sel.selectedIndex=0;
}

function adicionarItemSim(i,titulo,texto){

    if(selecoesSim[i].find(x=>x.titulo===titulo)) return;

    selecoesSim[i].push({titulo,texto});
    atualizarSim(i);
}

function atualizarSim(i){

    let nome = document.getElementById("nome"+i)?.value || "";
    let area = document.getElementById("saida"+i);
    let lista = document.getElementById("lista"+i);

    if(!area || !lista) return;

    let arr = selecoesSim[i];

    // TAGS
    lista.innerHTML = arr.map((item,index)=>`
        <div class="tag">${item.titulo} <b onclick="removerSim(${i},${index})">x</b></div>
    `).join("");

    let texto = `Prezado(a) ${nome},\n\n`;

    if(arr.length > 0){

        texto += "Após análise da solicitação, foram identificadas as seguintes pendências:\n\n";

        arr.forEach((item,index)=>{

            let base = item.texto.trim();

            // remove ponto final
            if(base.endsWith(".")){
                base = base.slice(0, -1);
            }

            let final = (index === arr.length - 1) ? "." : ";";

            texto += `${index+1}. ${base}${final}\n\n`;

        });

        texto += "Dessa forma, solicitamos o envio da documentação pendente para continuidade da análise da solicitação.";

    }

    area.value = texto;
}

function removerSim(i,index){
    selecoesSim[i].splice(index,1);
    atualizarSim(i);
}

function limparSim(i){

    selecoesSim[i] = [];

    let nome = document.getElementById("nome"+i);
    let area = document.getElementById("saida"+i);
    let lista = document.getElementById("lista"+i);

    if(nome) nome.value="";
    if(area) area.value="";
    if(lista) lista.innerHTML="";
}

function limparTudoSim(){
    for(let i=1;i<=6;i++){
        limparSim(i);
    }
}

// ================= INIT =================
window.onload = function(){

    if(localStorage.getItem("dark")){
        document.body.classList.add("dark");
    }

    atualizarHora();
    montarAnaliseUnica();
    montarAnaliseSimultanea();
    setInterval(carregarChat,2000);
    carregarChat();

    carregarSelectIndeferimento();
    carregarSelectDeferimento();
}

// ================= MODAL DATA =================
let callbackData = null;

function abrirModalData(callback){
    callbackData = callback;

    let modal = document.getElementById("modalData");
    let input = document.getElementById("inputData");

    if(input) input.value = "";

    if(modal) modal.classList.remove("hidden");

    setTimeout(()=>{
        if(input){
            input.focus();

            input.onkeydown = function(e){
                if(e.key === "Enter"){
                    confirmarData();
                }
            }
        }
    },100);
}

function fecharModal(){
    let modal = document.getElementById("modalData");
    if(modal) modal.classList.add("hidden");
}

function confirmarData(){

    let input = document.getElementById("inputData");
    if(!input) return;

    let valor = input.value.replace(/\D/g,'');

    if(valor.length !== 8){
        alert("Digite 8 números.");
        return;
    }

    let data = valor.replace(/(\d{2})(\d{2})(\d{4})/,"$1/$2/$3");

    fecharModal();

    if(callbackData) callbackData(data);
}

// fechar clicando fora
function fecharModalFora(e){
    if(e.target.id === "modalData"){
        fecharModal();
    }
}

// ================= ABERTURA DE TELAS =================

function abrirAnaliseUnica(){
    abrir('analiseUnica');
    montarAnaliseUnica();
}

function abrirAnaliseSimultanea(){
    abrir('analiseSimultanea');
    montarAnaliseSimultanea();
}

function abrirDeferUnico(){
    abrir('deferimentoUnico');
}

function abrirDeferSimultaneo(){
    abrir('deferimentoSimultaneo');
}

console.log("JS carregado");

function normalizarCurso(texto){

    if(!texto) return "";

    return texto
        .toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // remove acento
        .replace(/\btecnico\b/g, "")
        .replace(/\btécnico\b/g, "")
        .replace(/\bem\b/g, "")
        .replace(/\bde\b/g, "")
        .replace(/\s+/g, " ")
        .trim();
}

function gerarDefer(){

    let cursoOriginal = document.getElementById("curso")?.value || "";
    let curso = normalizarCurso(cursoOriginal);
    let tipo = document.getElementById("tipo")?.value;
    let area = document.getElementById("saidaDefer");

    if(!curso || !tipo){
        if(area) area.value = "";
        return;
    }

    fetch("/deferimento", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            curso: curso,
            tipo: tipo
        })
    })
    .then(r => r.json())
    .then(res => {

        let texto = res.texto || "";

        let cursoUpper = cursoOriginal.toUpperCase();

        if(
            cursoUpper.includes("AGRIMENSURA") ||
            cursoUpper.includes("GEODÉSIA") ||
            cursoUpper.includes("GEODESIA") ||
            cursoUpper.includes("CARTOGRAFIA") ||
            cursoUpper.includes("GEOPROCESSAMENTO")
        ){
           texto += "\nComunicamos que deverá solicitar mediante o protocolo a \"Revisão de atribuições em Georreferenciamento\" caso deseje emitir TRTs para atividades de georreferenciamento.";
        }

        area.value = texto;

    })
    .catch(() => {
        area.value = "Erro ao conectar com o servidor.";
    });
}

// ================= ADMIN =================

function carregarUsuarios(){

    fetch("/listar_usuarios")
    .then(r=>r.json())
    .then(lista=>{

        let tabela = document.getElementById("tabelaUsuarios");
        if(!tabela) return;

        tabela.innerHTML = `
        <tr>
            <th>Usuário</th>
            <th>Perfil</th>
            <th>Status</th>
            <th>Ações</th>
        </tr>
        `;

        lista.forEach(u=>{

            let status = u.ativo ? "Ativo" : "Inativo";

            tabela.innerHTML += `
            <tr>
                <td>${escapeHtml(u.user)}</td>
                <td>${escapeHtml(u.perfil)}</td>
                <td>${status}</td>

                <td>
                    <button onclick="toggleUsuario('${encodeURIComponent(u.user)}')">
                        ${u.ativo ? "Inativar" : "Ativar"}
                    </button>

                    <button onclick="alterarSenha('${encodeURIComponent(u.user)}')">
                        Senha
                    </button>

                    <button onclick="excluirUsuario('${encodeURIComponent(u.user)}')">
                        Excluir
                    </button>
                </td>
            </tr>
            `;
        });

    });
}


// ================= FUNÇÕES =================
function escapeHtml(text){
    return text
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");
}


// ATIVAR / INATIVAR
function toggleUsuario(user){

    user = decodeURIComponent(user);

    fetch("/toggle_usuario",{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({user:user})
    })
    .then(()=>carregarUsuarios());
}


// ALTERAR SENHA
function alterarSenha(user){

    user = decodeURIComponent(user);

    let nova = prompt("Digite a nova senha:");

    if(!nova) return;

    fetch("/alterar_senha",{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            user:user,
            senha:nova
        })
    })
    .then(()=>{
        alert("Senha atualizada");
        carregarUsuarios(); // ✔ atualiza lista
    });
}


// EXCLUIR
function excluirUsuario(user){

    user = decodeURIComponent(user);

    if(!confirm("Deseja excluir o usuário?")) return;

    fetch("/excluir_usuario",{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({user:user})
    })
    .then(()=>carregarUsuarios());
}
// ================= CADASTRAR USUARIO =================
function cadastrarUsuario(){

    let user = document.getElementById("novo_user").value.trim();
    let senha = document.getElementById("nova_senha").value.trim();
    let perfil = document.getElementById("perfil").value;

    if(!user || !senha){
        alert("Preencha usuário e senha");
        return;
    }

    fetch("/cadastrar_usuario",{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            user:user,
            senha:senha,
            perfil:perfil
        })
    })
    .then(async r => {
        let data = await r.json();

        if(!r.ok){
            throw new Error(data.msg || "Erro no servidor");
        }

        return data;
    })
    .then(res=>{
        alert(res.msg);
        carregarUsuarios();
    })
    .catch(err=>{
        alert("Erro: " + err.message);
        console.error(err);
    });
}

function limparCampo(id){
    let campo = document.getElementById(id);
    if(campo){
        campo.value = "";
    }
}

function gerarDeferTitulo(){

    let cursoOriginal = document.getElementById("cursoTitulo")?.value || "";
    let curso = normalizarCurso(cursoOriginal);
    let area = document.getElementById("saidaDeferTitulo");

    if(!curso){
        if(area) area.value = "";
        return;
    }

    fetch("/deferimento_titulo", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            curso: curso
        })
    })
    .then(r => r.json())
    .then(res => {
        if(area){
            area.value = res.texto || "Erro ao gerar texto.";
        }
    })
    .catch(() => {
        if(area){
            area.value = "Erro ao conectar com o servidor.";
        }
    });
}

function gerarInterrupcao(tipo){

    let selectId = tipo === "indeferimento" ? "selectIndeferimento" : "selectDeferimentoInt";
    let saidaId = tipo === "indeferimento" ? "saidaIndeferimento" : "saidaDeferimentoInt";

    let select = document.getElementById(selectId);
    let area = document.getElementById(saidaId);

    if(!select || !area) return;

    let chave = select.value;
    let item = TEXTOS_INTERRUPCAO[tipo][chave];

    if(!item){
        area.value = "";
        return;
    }

    // 🔥 TRATAMENTO DE NÚMERO (CBO)
    if(item.precisaNumero){

        abrirModalNumero((numero)=>{
    let texto = item.texto.replace("{numero}", numero);
    area.value = texto;
    select.selectedIndex = 0; // 🔥 reseta
});

    } else {
        area.value = item.texto;
        select.selectedIndex = 0; // 🔥 reseta
    }
}

const TEXTOS_INTERRUPCAO = {

    indeferimento: {

        incompleta: {
            titulo: "Solicitação incompleta",
            texto: `INTERRUPÇÃO INDEFERIDA.
O requerimento de solicitação não atende aos normativos da Resolução 141/2021 do CFT conforme Capítulo III onde estabelece os procedimentos e requisitos quanto à Interrupção de registro profissional. Solicite novamente a interrupção através de protocolo, o mesmo deve apresentar uma declaração de não ocupação de cargo ou atividade na área de sua formação técnica profissional, constando nome completo e CPF, assinada pelo requerente e datada e A CARTEIRA DE TRABALHO DIGITAL CONSTANDO AS INFORMAÇÕES DOS TRABALHOS E IDENTIFICAÇÃO DO TITULAR DA CTPS, como documentação comprobatória. Se a solicitação estiver relacionada a motivo de saúde, o requerente deverá apresentar documento que comprove a carta de concessão ou decisão de benefício do INSS.

Caso necessite de esclarecimentos adicionais por favor entrar em contato com 98 98279-0023.

Ressaltamos que, conforme o Art. 35 da Resolução CFT nº 045/2018, é vedado o exercício de atividades fiscalizadas pelo sistema CFT/CRTs por profissionais técnicos industriais sem o devido registro ativo, o que destaca a importância da regularização para o desempenho das funções.`
        },

        trt: {
            titulo: "Com TRT ou Responsável Técnico",
            texto: `INTERRUPÇÃO INDEFERIDA.
Prezado Profissional, analisamos em nosso sistema e conforme a resolução nº 141/2021, Art.13º, onde consta que a interrupção do registro é facultada ao profissional que, temporariamente, não pretende exercer a profissão e que atenda certas condições. Portanto solicitamos que seja dada baixa em suas TRTs ativas e posteriormente seja solicitado baixa em sua Responsabilidade Técnica ativa.

Ademais informamos que após os procedimentos informados, solicite novamente a interrupção através de protocolo, o mesmo deve apresentar uma declaração de não ocupação de cargo ou atividade na área de sua formação técnica profissional, constando nome completo e CPF, assinada pelo requerente e datada e A CARTEIRA DE TRABALHO DIGITAL CONSTANDO AS INFORMAÇÕES DOS TRABALHOS E IDENTIFICAÇÃO DO TITULAR DA CTPS, como documentação comprobatória. Se a solicitação estiver relacionada a motivo de saúde, o requerente deverá apresentar documento que comprove a carta de concessão ou decisão de benefício do INSS.

Caso necessite de esclarecimentos adicionais por favor entrar em contato com 98 98279-0023.

Ressaltamos que, conforme o Art. 35 da Resolução CFT nº 045/2018, é vedado o exercício de atividades fiscalizadas pelo sistema CFT/CRTs por profissionais técnicos industriais sem o devido registro ativo, o que destaca a importância da regularização para o desempenho das funções.`
        },

        cbo: {
            titulo: "Exercendo atividades técnicas",
            texto: `INTERRUPÇÃO INDEFERIDA.
O requerimento apresentado não atende aos requisitos estabelecidos na Resolução CFT nº 141/2021, especificamente no Capítulo III, que trata dos procedimentos e condições para a interrupção do registro profissional. Após análise do CBO {numero}, constatou-se que as atividades descritas estão diretamente relacionadas às prerrogativas e atribuições de técnicos industriais.

Ressaltamos que, conforme o Art. 35 da Resolução CFT nº 045/2018, é vedado o exercício de atividades fiscalizadas pelo sistema CFT/CRTs por profissionais técnicos industriais sem o devido registro ativo, o que destaca a importância da regularização para o desempenho das funções.

Posteriormente, caso não exerça atividades técnicas, poderá solicitar novamente a interrupção mediante protocolo. Para tanto, será necessário apresentar uma declaração de não ocupação de cargo ou atividade na área de formação técnica profissional, contendo nome completo, CPF, assinatura do requerente e data, além da carteira de trabalho digital com informações sobre vínculos empregatícios e dados de identificação. Se a solicitação estiver relacionada a motivo de saúde, o requerente deverá apresentar documento que comprove a carta de concessão ou decisão de benefício do INSS.

Em caso de dúvidas ou necessidade de esclarecimentos adicionais, solicitamos que entre em contato pelo telefone (98) 98279-0023.`,
            precisaNumero: true
        }
    },

    deferimento: {

        com_debitos: {
            titulo: "Com débitos financeiros",
            texto: `Registro INTERROMPIDO.
Anotado conforme data da abertura do protocolo (solicitação).

Embora a interrupção tenha sido deferida, é importante ressaltar que isso não isenta o profissional do pagamento das obrigações financeiras anteriores ou em aberto, conforme a Resolução Nº 141/2021, Art. 13º, Parágrafo Único e Resolução Nº 241/2023. Portanto, solicitamos gentilmente a quitação dos débitos pendentes, a fim de evitar transtornos no momento da reativação. Ressaltamos que o valor não pago permanecerá registrado em nosso sistema. Caso necessite de esclarecimentos adicionais por favor entrar em contato com  (98) 98279-0023.

Comunicamos que poderá posteriormente solicitar a reativação do seu registro profissional caso queira trabalhar na função técnica.

Ressaltamos que, conforme o Art. 35 da Resolução CFT nº 045/2018, é vedado o exercício de atividades fiscalizadas pelo sistema CFT/CRTs por profissionais técnicos industriais sem o devido registro ativo, o que destaca a importância da regularização para o desempenho das funções. Além disso, a Resolução 141/2021 do CFT, em seu Art. 19, determina que, caso seja constatado, durante o período de interrupção do registro, o exercício de atividades pelo profissional, este ficará sujeito à autuação por infração à legislação reguladora da profissão e por falta ética, sujeitando-se às cominações legais e regulamentares aplicáveis, cabendo o cancelamento da interrupção do registro.`
        },

        sem_debitos: {
            titulo: "Sem débitos financeiros",
            texto: `Registro INTERROMPIDO.
Anotado conforme data da abertura do protocolo (solicitação).

Comunicamos que poderá posteriormente solicitar a reativação do seu registro profissional caso queira trabalhar na função técnica.

Ressaltamos que, conforme o Art. 35 da Resolução CFT nº 045/2018, é vedado o exercício de atividades fiscalizadas pelo sistema CFT/CRTs por profissionais técnicos industriais sem o devido registro ativo, o que destaca a importância da regularização para o desempenho das funções. Além disso, a Resolução 141/2021 do CFT, em seu Art. 19, determina que, caso seja constatado, durante o período de interrupção do registro, o exercício de atividades pelo profissional, este ficará sujeito à autuação por infração à legislação reguladora da profissão e por falta ética, sujeitando-se às cominações legais e regulamentares aplicáveis, cabendo o cancelamento da interrupção do registro.`
        }

    }

};

function carregarSelectIndeferimento(){

    let select = document.getElementById("selectIndeferimento");
    if(!select) return;

    select.innerHTML = `<option value="">Selecione o motivo</option>`;

    Object.keys(TEXTOS_INTERRUPCAO.indeferimento).forEach(key => {

        let item = TEXTOS_INTERRUPCAO.indeferimento[key];

        let opt = document.createElement("option");
        opt.value = key;
        opt.textContent = item.titulo;

        select.appendChild(opt);
    });
}


let callbackNumero = null;

function abrirModalNumero(callback){

    callbackNumero = callback;

    let modal = document.getElementById("modalData"); // usa o mesmo modal
    let input = document.getElementById("inputData");

    if(input){
        input.value = "";
        input.placeholder = "Digite o CBO (ex: 1234-56)";
    }

    if(modal) modal.classList.remove("hidden");

    setTimeout(()=>{
        if(input){
            input.focus();

            input.onkeydown = function(e){
                if(e.key === "Enter"){
                    confirmarNumero();
                }
            }
        }
    },100);
}

function confirmarNumero(){

    let input = document.getElementById("inputData");
    if(!input) return;

    let valor = input.value.trim();

    if(!valor){
        alert("Digite o número do CBO.");
        return;
    }

    fecharModal();

    if(callbackNumero){
        callbackNumero(valor);
    }
}

function confirmarModal(){

    if(callbackNumero){
        confirmarNumero();
    }else{
        confirmarData();
    }
}
function forcarGeracaoInterrupcao(tipo){

    let selectId = tipo === "indeferimento" ? "selectIndeferimento" : "selectDeferimentoInt";

    let select = document.getElementById(selectId);
    if(!select) return;

    let chave = select.value;
    let item = TEXTOS_INTERRUPCAO[tipo][chave];

    if(item && item.precisaNumero){
        gerarInterrupcao(tipo);
    }
}

function carregarSelectDeferimento(){

    let select = document.getElementById("selectDeferimentoInt");
    if(!select) return;

    select.innerHTML = `<option value="">Selecione o tipo</option>`;

    Object.keys(TEXTOS_INTERRUPCAO.deferimento).forEach(key => {

        let item = TEXTOS_INTERRUPCAO.deferimento[key];

        let opt = document.createElement("option");
        opt.value = key;
        opt.textContent = item.titulo;

        select.appendChild(opt);
    });
}

function gerarTextoReativacao(){
    let tipo = document.getElementById("tipoReativacao").value;
    let nome = document.getElementById("nomeReativacao").value;
    let saida = document.getElementById("saidaReativacao");

    let textos = {
        "comum": `Prezado(a) ${nome},

Informamos que seu registro profissional foi reativado e encontra-se ATIVO.

Para emissão do boleto de anuidade, acesse o seu ambiente profissional. Caso prefira, entre em contato com o setor de atendimento pelo número (98) 98279-0023 para mais informações.`,

        "atualizacao": `Prezado(a) ${nome},

Informamos que seu registro profissional encontra-se ATIVO, conforme a Resolução AD Referendum Normativa nº 14, de 08 de agosto de 2022.

Identificamos que seu cadastro apresenta informações desatualizadas, o que pode impedir a emissão da carteira profissional e de outros documentos. Dessa forma, solicitamos a atualização cadastral por meio do protocolo “ATUALIZAÇÃO DE DADOS CADASTRAIS - PROFISSIONAL”, com a descrição “ATUALIZAÇÃO DE CADASTRO”, anexando os seguintes documentos:

1. Documento de identificação atualizado;
2. Certidão de quitação eleitoral atualizada;
3. Comprovante de endereço atualizado.

Observações:
- O endereço deverá ser atualizado por meio do protocolo “ALTERAÇÃO DE ENDEREÇO PARA OUTRO REGIONAL” nos casos de mudança para outro CRT;
- O comprovante de endereço deve estar atualizado, podendo estar em nome próprio, dos pais ou do cônjuge (neste caso, acompanhado da certidão de casamento), ou ser apresentada declaração de residência.

A foto deverá ser encaminhada por meio do protocolo “INCLUSÃO DE FOTO”.`,

        "definitivo": `Prezado(a) ${nome},

Informamos que seu registro profissional foi alterado para DEFINITIVO e encontra-se ATIVO.

Para emissão do boleto de anuidade, acesse o seu ambiente profissional. Caso prefira, entre em contato com o setor de atendimento pelo número (98) 98279-0023 para mais informações.`
    };

    saida.value = textos[tipo] || "";
}

function limparReativacao(){
    document.getElementById("nomeReativacao").value = "";
    document.getElementById("tipoReativacao").value = "";
    document.getElementById("saidaReativacao").value = "";

    document.getElementById("nomeReativacao").focus();
}