import streamlit as stream
import sqlite3
import datetime
from fpdf import FPDF

# Configuração inicial
# Mude de layout="wide" para layout="centered"
stream.set_page_config(page_title="Festa-Flow 1.0", page_icon="🎉", layout="centered")

def conectar():
    return sqlite3.connect("festa_flow.db")

def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, whatsapp TEXT, data_evento TEXT, atendente_responsavel TEXT, status TEXT, valor_total REAL, valor_pago REAL, observacao TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS acessorios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, quantidade_total INTEGER, quantidade_disponivel INTEGER, valor_locacao REAL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, usuario TEXT UNIQUE, senha TEXT, cargo TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS logs_alteracoes (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, tabela TEXT, registro_id INTEGER, descricao TEXT, data_hora TEXT)")
    
    # Criar admin padrão se não houver ninguém
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (nome, usuario, senha, cargo) VALUES (?, ?, ?, ?)", ('Grazi', 'grazi', '1234', 'Administradora'))
    
    conexao.commit()
    conexao.close()

inicializar_banco()

# --- LOGIN DE SEGURANÇA ---
if "autenticado" not in stream.session_state:
    stream.session_state.autenticado = False

if not stream.session_state.autenticado:
    stream.title("🔐 Login - Festa-Flow")
    user_input = stream.text_input("Usuário")
    pass_input = stream.text_input("Senha", type="password")
    
    if stream.button("Entrar"):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE usuario = ? AND senha = ?", (user_input, pass_input))
        usuario = cursor.fetchone()
        conexao.close()
        
        if usuario:
            stream.session_state.autenticado = True
            stream.session_state.usuario_logado = usuario[0]
            stream.rerun()
        else:
            stream.error("❌ Usuário ou senha inválidos!")
    stream.stop()

# A PARTIR DAQUI O SISTEMA ESTÁ LIBERADO!
stream.success(f"Bem-vinda, {stream.session_state.usuario_logado}!")
stream.write("Sistema rodando com sucesso.")

# --- A PARTIR DAQUI, O SISTEMA SÓ RODA SE ESTIVER AUTENTICADO ---
# (Você cola o restante do seu código aqui embaixo!)

# Configuração inicial da página web
stream.set_page_config(page_title="Festa-Flow 1.0", page_icon="🎉", layout="wide")

# Função para conectar ao banco de dados
def conectar():
    return sqlite3.connect("festa_flow.db")

# Criar tabelas necessárias se não existirem
def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        data_evento TEXT,
        atendente_responsavel TEXT,
        status TEXT,
        valor_total REAL DEFAULT 0.0,
        valor_pago REAL DEFAULT 0.0
    )
    """)
    
    # CÓDIGO MÁGICO: Adiciona a coluna 'observacao' se ela não existir
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN observacao TEXT")
    except sqlite3.OperationalError:
        pass 
    
    # Acessórios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS acessorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,
        quantidade_total INTEGER,
        quantidade_disponivel INTEGER,
        valor_locacao REAL
    )
    """)
    
    # Pedidos / Itens do orçamento
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        acessorio_id INTEGER,
        quantidade INTEGER,
        valor_unitario REAL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (acessorio_id) REFERENCES acessorios(id)
    )
    """)
    
    # Usuários / Equipe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        cargo TEXT
    )
    """)
    
    # Inserir usuário padrão se não existir
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (nome, usuario, senha, cargo) VALUES ('Grazi', 'grazi', '1234', 'Administradora')")
    
    # Agenda de Compromissos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compromissos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        data TEXT NOT NULL,
        hora TEXT,
        tipo TEXT,
        status TEXT DEFAULT 'Pendente'
    )
    """)
    
    # Log de Alterações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_alteracoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        tabela TEXT,
        registro_id INTEGER,
        descricao TEXT,
        data_hora TEXT
    )
    """)
    
    conexao.commit()
    conexao.close()

inicializar_banco()

# --- Restante do código segue abaixo com a mesma lógica que já validamos... ---
# (Pode manter o restante das suas funções de PDF e Menus que já estão funcionando!)


# --- REGISTRO DE LOGS DE ALTERAÇÃO ---
def registrar_alteracao(tabela, registro_id, descricao):
    usuario_atual = stream.session_state.get("usuario_logado", "Sistema")
    data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
    INSERT INTO logs_alteracoes (usuario, tabela, registro_id, descricao, data_hora)
    VALUES (?, ?, ?, ?, ?)
    """, (usuario_atual, tabela, registro_id, descricao, data_hora))
    conexao.commit()
    conexao.close()


# --- FUNÇÃO AUXILIAR PARA EVITAR ERROS DE ACENTOS NO PDF ---
def t(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')


# --- GERADORES DE PDF - GRAZI DECORAÇÕES ---
def gerar_pdf_orcamento(nome_cliente, itens, total):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, t("GRAZI DECORAÇÕES"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, t("Rua Governador Armando Sales de Oliveira, 365 - Santo Stefano - Salto/SP - CEP: 13320-210"), ln=True, align="C")
    pdf.cell(0, 5, t("Telefone / WhatsApp: (11) 99929-7089 - Email: grazicasadasflores@gmail.com"), ln=True, align="C")
    pdf.ln(5)
    pdf.line(10, 35, 200, 35) 
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, t("ORÇAMENTO DE LOCAÇÃO DE ACESSÓRIOS"), ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, t(f"  CLIENTE: {nome_cliente.upper()}"), ln=True, fill=True)
    pdf.ln(4)
    
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(85, 8, t(" Item / Acessório"), border=1, align="L", fill=True)
    pdf.cell(20, 8, t("Qtd"), border=1, align="C", fill=True)
    pdf.cell(40, 8, t("Valor Unit."), border=1, align="R", fill=True)
    pdf.cell(45, 8, t("Subtotal"), border=1, align="R", fill=True)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 10)
    for item in itens:
        _, nome_item, qtd, val_uni, subtotal = item
        pdf.cell(85, 8, t(f" {nome_item}"), border=1, align="L")
        pdf.cell(20, 8, t(qtd), border=1, align="C")
        pdf.cell(40, 8, t(f"R$ {val_uni:.2f}"), border=1, align="R")
        pdf.cell(45, 8, t(f"R$ {subtotal:.2f}"), border=1, align="R")
        pdf.ln()
        
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(145, 8, t("TOTAL DO ORÇAMENTO: "), align="R")
    pdf.cell(45, 8, t(f"R$ {total:.2f}"), border=1, align="R", fill=True)
    pdf.ln(12)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 4, t("* Este orçamento é válido por 7 dias a partir desta data."), ln=True)
    pdf.cell(0, 4, t("* A reserva dos materiais só é garantida mediante assinatura do contrato e pagamento inicial."), ln=True)
    pdf.ln(15)
    
    pdf.cell(95, 5, t("_______________________________________"), ln=False, align="C")
    pdf.cell(95, 5, t("_______________________________________"), ln=True, align="C")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 5, t("Grazi Decorações"), ln=False, align="C")
    pdf.cell(95, 5, t("Aceito pelo Cliente"), ln=True, align="C")
    
    try:
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
    except:
        pdf_bytes = pdf.output()
    return pdf_bytes


def gerar_pdf_ordem_servico(nome_cliente, data_evento, itens, atendente):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, t("GRAZI DECORAÇÕES"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, t("Rua Governador Armando Sales de Oliveira, 365 - Santo Stefano - Salto/SP - CEP: 13320-210"), ln=True, align="C")
    pdf.cell(0, 5, t("Telefone / WhatsApp: (11) 99929-7089 - Email: grazicasadasflores@gmail.com"), ln=True, align="C")
    pdf.ln(5)
    pdf.line(10, 35, 200, 35)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, t("ORDEM DE SERVIÇO - SEPARAÇÃO DE MATERIAIS"), ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, t(f"  CLIENTE / EVENTO: {nome_cliente.upper()}"), ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 8, t(f" Data de Montagem/Evento: {data_evento}"), border=1)
    pdf.cell(95, 8, t(f" Atendente Responsável: {atendente}"), border=1, ln=True)
    pdf.ln(4)
    
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(140, 8, t(" Item / Acessório para Separação"), border=1, align="L", fill=True)
    pdf.cell(50, 8, t("Quantidade Necessária"), border=1, align="C", fill=True)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 10)
    for item in itens:
        _, nome_item, qtd, _, _ = item
        pdf.cell(140, 8, t(f" [  ]  {nome_item}"), border=1, align="L")
        pdf.cell(50, 8, t(qtd), border=1, align="C")
        pdf.ln()
        
    pdf.ln(15)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, t("CONFERÊNCIA INTERNA DE LOGÍSTICA:"), ln=True)
    pdf.ln(8)
    
    pdf.cell(95, 5, t("_______________________________________"), ln=False, align="C")
    pdf.cell(95, 5, t("_______________________________________"), ln=True, align="C")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 5, t("Separado por (Estoque)"), ln=False, align="C")
    pdf.cell(95, 5, t("Conferido por (Montagem)"), ln=True, align="C")
    
    try:
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
    except:
        pdf_bytes = pdf.output()
    return pdf_bytes


# --- SESSÃO DO USUÁRIO LOGADO ---
if "usuario_logado" not in stream.session_state:
    stream.session_state.usuario_logado = "Grazi"

stream.sidebar.markdown("### 👤 Operador Atual")
conexao = conectar()
cursor = conexao.cursor()
cursor.execute("SELECT nome FROM usuarios")
todos_usuarios = [u[0] for u in cursor.fetchall()]
conexao.close()

usuario_selecionado = stream.sidebar.selectbox("Trabalhando como:", todos_usuarios, index=0 if "Grazi" in todos_usuarios else 0)
stream.session_state.usuario_logado = usuario_selecionado


# --- CONTROLE DE NAVEGAÇÃO ---
if "pagina_ativa" not in stream.session_state:
    stream.session_state.pagina_ativa = "Painel Geral (Clientes)"

stream.sidebar.title("🎈 Festa-Flow 1.0")
stream.sidebar.markdown("### Navegação")

if stream.sidebar.button("👥 Painel Geral (Clientes)", use_container_width=True):
    stream.session_state.pagina_ativa = "Painel Geral (Clientes)"
    stream.rerun()

if stream.sidebar.button("📝 Guia de Pedidos", use_container_width=True):
    stream.session_state.pagina_ativa = "📝 Guia de Pedidos"
    stream.rerun()

if stream.sidebar.button("📅 Agenda de Eventos & Compromissos", use_container_width=True):
    stream.session_state.pagina_ativa = "Agenda de Eventos & Compromissos"
    stream.rerun()

if stream.sidebar.button("📦 Estoque de Acessórios", use_container_width=True):
    stream.session_state.pagina_ativa = "Estoque de Acessórios"
    stream.rerun()

if stream.sidebar.button("🗄️ Histórico (Encerrados)", use_container_width=True):
    stream.session_state.pagina_ativa = "Histórico (Encerrados)"
    stream.rerun()

if stream.sidebar.button("⚙️ Segurança (Logs & Equipe)", use_container_width=True):
    stream.session_state.pagina_ativa = "Segurança (Logs & Equipe)"
    stream.rerun()

menu = stream.session_state.pagina_ativa

stream.title("🎉 Festa-Flow 1.0 - Painel de Controle")

# ==========================================
# 1. TELA DE CLIENTES
# ==========================================
if menu == "Painel Geral (Clientes)":
    stream.header("👥 Gestão de Clientes")
    
    aba_cadastro, aba_lista = stream.tabs(["➕ Cadastrar Novo Cliente", "📋 Lista Geral de Clientes"])
    
    with aba_cadastro:
        col1, col2 = stream.columns(2)
        with col1:
            nome = stream.text_input("Nome do Cliente")
            whatsapp = stream.text_input("WhatsApp (com DDD)")
            data_evento = stream.text_input("Data do Evento (DD/MM/AAAA)")
        with col2:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("SELECT nome FROM usuarios")
            lista_usuarios = [u[0] for u in cursor.fetchall()]
            conexao.close()
            if not lista_usuarios:
                lista_usuarios = ["Grazi"]
                
            atendente = stream.selectbox("Atendente Responsável", lista_usuarios)
            status = stream.selectbox("Etapa Inicial", ["Prospecção", "Orçamento", "Contrato Fechado"])
            
        if stream.button("Salvar Cliente", use_container_width=True):
            if nome and whatsapp:
                conexao = conectar()
                cursor = conexao.cursor()
                cursor.execute("""
                INSERT INTO clientes (nome, whatsapp, data_evento, atendente_responsavel, status, valor_total, valor_pago)
                VALUES (?, ?, ?, ?, ?, 0.0, 0.0)
                """, (nome, whatsapp, data_evento, atendente, status))
                novo_id = cursor.lastrowid
                conexao.commit()
                conexao.close()
                
                registrar_alteracao("clientes", novo_id, f"Cadastrou o cliente {nome} (Evento em {data_evento})")
                stream.success(f"✔️ {nome} cadastrado com sucesso!")
                stream.rerun()
            else:
                stream.error("❌ Nome e WhatsApp são obrigatórios!")

    with aba_lista:
        stream.subheader("📊 Todos os Clientes Cadastrados")
        conexao = conectar()
        cursor = conexao.cursor()
        # Buscando agora os 9 campos (id, nome, whatsapp, data, atendente, status, total, pago, observacao)
        cursor.execute("SELECT id, nome, whatsapp, data_evento, atendente_responsavel, status, valor_total, valor_pago, observacao FROM clientes")
        todos_clientes = cursor.fetchall()
        conexao.close()

        if todos_clientes:
            for cli in todos_clientes:
                id_cli, n, w, d, a, s, total, pago, obs = cli # Agora vai funcionar!
                
                with stream.container(border=True):
                    c1, c2, c3, c4 = stream.columns([2, 1, 1, 1])
                    c1.markdown(f"**Cliente:** {n} | 📱 {w}")
                    c2.markdown(f"**Status:** {s}")
                    c3.markdown(f"**Atendente:** {a}")
                    c4.markdown(f"**Total:** R$ {total:.2f}")
                    
                    with stream.expander("✏️ Editar Cadastro & Observações"):
                        # Organizando os campos de edição em colunas
                        col_e1, col_e2 = stream.columns(2)
                        with col_e1:
                            novo_nome = stream.text_input("Nome do Cliente:", value=n, key=f"edit_nome_{id_cli}")
                            novo_whatsapp = stream.text_input("WhatsApp:", value=w, key=f"edit_wpp_{id_cli}")
                        with col_e2:
                            nova_data = stream.text_input("Data Evento:", value=d, key=f"edit_data_{id_cli}")
                            novo_atendente = stream.text_input("Atendente:", value=a, key=f"edit_atend_{id_cli}")
                        
                        nova_obs = stream.text_area("Observações sobre o cliente:", value=obs if obs else "", key=f"obs_{id_cli}")
                        
                        if stream.button("💾 Salvar Alterações do Cliente", key=f"btn_save_{id_cli}"):
                            conexao = conectar()
                            cursor = conexao.cursor()
                            cursor.execute("""
                                UPDATE clientes 
                                SET nome = ?, whatsapp = ?, data_evento = ?, atendente_responsavel = ?, observacao = ? 
                                WHERE id = ?
                            """, (novo_nome, novo_whatsapp, nova_data, novo_atendente, nova_obs, id_cli))
                            conexao.commit()
                            conexao.close()
                            
                            registrar_alteracao("clientes", id_cli, f"Editou os dados do cliente: {n}")
                            stream.success("Cadastro atualizado com sucesso!")
                            stream.rerun()
        else:
            stream.info("Nenhum cliente cadastrado no sistema ainda.")

# ==========================================
# 2. GUIA DE PEDIDOS
# ==========================================
elif menu == "📝 Guia de Pedidos":
    stream.header("📝 Guia de Pedidos & Orçamentos")

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, status, valor_total, valor_pago FROM clientes WHERE status != 'Concluído'")
    lista_clientes = cursor.fetchall()
    cursor.execute("SELECT id, nome, quantidade_disponivel, valor_locacao FROM acessorios")
    lista_acessorios = cursor.fetchall()
    conexao.close()

    if not lista_clientes:
        stream.warning("⚠️ Não há clientes ativos cadastrados!")
    else:
        if "cliente_orcamento_id" not in stream.session_state:
            stream.session_state.cliente_orcamento_id = None

        stream.subheader("📋 Painel de Orçamentos Ativos")
        col_h1, col_h2, col_h3, col_h4, col_h5 = stream.columns([2, 1, 1, 1, 1])
        col_h1.markdown("**Cliente**")
        col_h2.markdown("**Status**")
        col_h3.markdown("**Total**")
        col_h4.markdown("**Pago**")
        col_h5.markdown("**Ação**")
        stream.divider()

        for cli in lista_clientes:
            id_cli, n, s, total, pago = cli
            col_c1, col_c2, col_c3, col_c4, col_c5 = stream.columns([2, 1, 1, 1, 1])
            col_c1.markdown(f"👤 {n}")
            col_c2.markdown(f"`{s}`")
            col_c3.markdown(f"R$ {total:.2f}")
            col_c4.markdown(f"R$ {pago:.2f}")
            if col_c5.button("🔎 Detalhes", key=f"btn_{id_cli}", use_container_width=True):
                stream.session_state.cliente_orcamento_id = id_cli
                stream.rerun()
        
        stream.divider()

        if stream.session_state.cliente_orcamento_id is not None:
            cliente_id = stream.session_state.cliente_orcamento_id
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("SELECT nome, status, valor_total, valor_pago, data_evento, atendente_responsavel FROM clientes WHERE id = ?", (cliente_id,))
            dados_cliente = cursor.fetchone()
            
            if dados_cliente:
                nome_cliente, status_cli, total_cli, pago_cli, data_env, atend_resp = dados_cliente
                
                with stream.container(border=True):
                    col_detalhe1, col_detalhe2 = stream.columns([3, 1])
                    col_detalhe1.markdown(f"## 📝 Orçamento de: **{nome_cliente}**")
                    if col_detalhe2.button("❌ Fechar Detalhes", use_container_width=True):
                        stream.session_state.cliente_orcamento_id = None
                        stream.rerun()

                    if not lista_acessorios:
                        stream.warning("⚠️ Cadastre itens no estoque primeiro!")
                    else:
                        stream.subheader("➕ Adicionar Acessório")
                        col_p1, col_p2 = stream.columns([2, 1])
                        with col_p1:
                            dicionario_acessorios = {f"{ac[1]} (Disp: {ac[2]} | R$ {ac[3]:.2f})": (ac[0], ac[3]) for ac in lista_acessorios}
                            acessorio_selecionado = stream.selectbox("Escolha o Acessório:", list(dicionario_acessorios.keys()))
                            acessorio_id, valor_unitario = dicionario_acessorios[acessorio_selecionado]
                        with col_p2:
                            qtd_aluguel = stream.number_input("Quantidade para Alugar:", min_value=1, step=1, key="qtd_add")

                        if stream.button("Adicionar Item ao Pedido", use_container_width=True):
                            cursor.execute("""
                            INSERT INTO pedidos_itens (cliente_id, acessorio_id, quantidade, valor_unitario)
                            VALUES (?, ?, ?, ?)
                            """, (cliente_id, acessorio_id, qtd_aluguel, valor_unitario))
                            cursor.execute("SELECT SUM(quantidade * valor_unitario) FROM pedidos_itens WHERE cliente_id = ?", (cliente_id,))
                            novo_total = cursor.fetchone()[0] or 0.0
                            cursor.execute("UPDATE clientes SET valor_total = ? WHERE id = ?", (novo_total, cliente_id))
                            conexao.commit()
                            
                            cursor.execute("SELECT nome FROM acessorios WHERE id = ?", (acessorio_id,))
                            nome_acessorio = cursor.fetchone()[0]
                            registrar_alteracao("pedidos_itens", cliente_id, f"Adicionou {qtd_aluguel}x '{nome_acessorio}' ao orçamento")
                            stream.success("✔️ Item adicionado!")
                            stream.rerun()

                    stream.subheader("📋 Itens Selecionados")
                    cursor.execute("""
                        SELECT p.id, a.nome, p.quantidade, p.valor_unitario, (p.quantidade * p.valor_unitario)
                        FROM pedidos_itens p
                        JOIN acessorios a ON p.acessorio_id = a.id
                        WHERE p.cliente_id = ?
                    """, (cliente_id,))
                    itens_pedido = cursor.fetchall()

                    if itens_pedido:
                        for item in itens_pedido:
                            id_pedido_item, nome_item, qtd, val_uni, subtotal = item
                            col_item1, col_item2 = stream.columns([4, 1])
                            col_item1.text(f"• {nome_item} | Qtd: {qtd} x R$ {val_uni:.2f} = R$ {subtotal:.2f}")
                            
                            if col_item2.button("🗑️ Remover", key=f"del_{id_pedido_item}"):
                                cursor.execute("DELETE FROM pedidos_itens WHERE id = ?", (id_pedido_item,))
                                cursor.execute("SELECT SUM(quantidade * valor_unitario) FROM pedidos_itens WHERE cliente_id = ?", (cliente_id,))
                                novo_total = cursor.fetchone()[0] or 0.0
                                cursor.execute("UPDATE clientes SET valor_total = ? WHERE id = ?", (novo_total, cliente_id))
                                conexao.commit()
                                registrar_alteracao("pedidos_itens", cliente_id, f"Removeu '{nome_item}' do orçamento")
                                stream.rerun()
                        
                        stream.markdown(f"### 💰 Total do Orçamento: R$ {total_cli:.2f}")
                        
                        stream.subheader("📄 Exportar Documentos")
                        col_doc1, col_doc2 = stream.columns(2)
                        with col_doc1:
                            pdf_orc = gerar_pdf_orcamento(nome_cliente, itens_pedido, total_cli)
                            stream.download_button(
                                label="📄 Baixar Orçamento Oficial (PDF)",
                                data=bytes(pdf_orc),
                                file_name=f"orcamento_{nome_cliente.lower().replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        with col_doc2:
                            pdf_os = gerar_pdf_ordem_servico(nome_cliente, data_env, itens_pedido, atend_resp)
                            stream.download_button(
                                label="🚚 Baixar Ordem de Serviço (PDF)",
                                data=bytes(pdf_os),
                                file_name=f"ordem_servico_{nome_cliente.lower().replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )

                        stream.subheader("⚙️ Fechamento & Pagamento")
                        col_f1, col_f2 = stream.columns(2)
                        with col_f1:
                            novo_status = stream.selectbox("Atualizar Status do Cliente:", ["Prospecção", "Orçamento", "Contrato Fechado", "Concluído"], index=["Prospecção", "Orçamento", "Contrato Fechado", "Concluído"].index(status_cli))
                        with col_f2:
                            novo_pago = stream.number_input("Registrar Valor Pago (R$):", min_value=0.0, value=pago_cli, step=50.0)
                        
                        if stream.button("Salvar Alterações de Fechamento", use_container_width=True):
                            cursor.execute("UPDATE clientes SET status = ?, valor_pago = ? WHERE id = ?", (novo_status, novo_pago, cliente_id))
                            conexao.commit()
                            registrar_alteracao("clientes", cliente_id, f"Alterou status de {nome_cliente} para '{novo_status}' e pagamento para R$ {novo_pago:.2f}")
                            stream.success("✔️ Alterações salvas!")
                            if novo_status == "Concluído":
                                stream.session_state.cliente_orcamento_id = None
                            stream.rerun()
            conexao.close()

# ==========================================
# 3. AGENDA DE EVENTOS & COMPROMISSOS
# ==========================================
elif menu == "Agenda de Eventos & Compromissos":
    stream.header("📅 Agenda da Grazi Decorações")
    stream.markdown("Centralize os eventos (festas) e compromissos internos (reuniões, visitas, cobranças).")
    
    aba_eventos, aba_compromissos = stream.tabs(["✨ Agenda de Eventos (Festas)", "📝 Agenda de Compromissos (Diários)"])
    
    with aba_eventos:
        stream.subheader("🎉 Próximos Eventos Cadastrados")
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, data_evento, atendente_responsavel, status FROM clientes WHERE data_evento IS NOT NULL AND data_evento != '' ORDER BY data_evento ASC")
        eventos = cursor.fetchall()
        conexao.close()
        
        if eventos:
            for ev in eventos:
                id_ev, nome_cli, data, atend, status_ev = ev
                with stream.container(border=True):
                    col_ev1, col_ev2, col_ev3 = stream.columns([2, 1, 1])
                    col_ev1.markdown(f"🌸 **Cliente:** {nome_cli}")
                    col_ev2.markdown(f"📅 **Data:** `{data}`")
                    col_ev3.markdown(f"👩‍💼 **Atendente:** {atend} | `{status_ev}`")
        else:
            stream.info("Nenhum evento com data cadastrada ainda.")
            
    with aba_compromissos:
        stream.subheader("✏️ Novo Compromisso na Agenda")
        col_comp1, col_comp2 = stream.columns(2)
        
        with col_comp1:
            titulo_comp = stream.text_input("Título do Compromisso", placeholder="Ex: Reunião com Noiva Mariana")
            tipo_comp = stream.selectbox("Tipo", ["Reunião", "Visita Técnica", "Cobrança", "Entrega", "Outros"])
            data_comp = stream.date_input("Data", datetime.date.today(), format="DD/MM/YYYY")
        with col_comp2:
            hora_comp = stream.text_input("Hora (HH:MM)", value="14:00")
            desc_comp = stream.text_area("Notas / Observações")
            
        if stream.button("Agendar Compromisso", use_container_width=True):
            if titulo_comp:
                data_str = data_comp.strftime("%d/%m/%Y")
                conexao = conectar()
                cursor = conexao.cursor()
                cursor.execute("""
                INSERT INTO compromissos (titulo, descricao, data, hora, tipo)
                VALUES (?, ?, ?, ?, ?)
                """, (titulo_comp, desc_comp, data_str, hora_comp, tipo_comp))
                novo_id = cursor.lastrowid
                conexao.commit()
                conexao.close()
                registrar_alteracao("compromissos", novo_id, f"Agendou {tipo_comp}: '{titulo_comp}' em {data_str}")
                stream.success(f"✔️ Compromisso agendado!")
                stream.rerun()
            else:
                stream.error("❌ Digite um título!")
                
        stream.divider()
        stream.subheader("📋 Compromissos")
        
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT id, titulo, descricao, data, hora, tipo, status FROM compromissos ORDER BY id DESC")
        compromissos_lista = cursor.fetchall()
        conexao.close()
        
        if compromissos_lista:
            for cp in compromissos_lista:
                id_cp, tit, desc, dt, hr, tp, st = cp
                st_icon = "⏳" if st == "Pendente" else "✅"
                with stream.container(border=True):
                    col_c1, col_c2, col_c3 = stream.columns([3, 1, 1])
                    with col_c1:
                        stream.markdown(f"**{st_icon} {tit}** ({tp})")
                        if desc: stream.caption(desc)
                    with col_c2:
                        stream.markdown(f"📅 {dt} às {hr}")
                    with col_c3:
                        if st == "Pendente":
                            if stream.button("Concluir", key=f"ok_comp_{id_cp}"):
                                conexao = conectar()
                                cursor = conexao.cursor()
                                cursor.execute("UPDATE compromissos SET status = 'Concluído' WHERE id = ?", (id_cp,))
                                conexao.commit()
                                conexao.close()
                                registrar_alteracao("compromissos", id_cp, f"Concluiu o compromisso '{tit}'")
                                stream.rerun()
                        else:
                            stream.markdown("✅ Feito")
        else:
            stream.info("Nenhum compromisso agendado.")

# ==========================================
# 4. ESTOQUE DE ACESSÓRIOS
# ==========================================
elif menu == "Estoque de Acessórios":
    stream.header("📦 Estoque de Acessórios")
    
    with stream.expander("➕ Adicionar Novo Item ao Estoque"):
        col1, col2 = stream.columns(2)
        with col1:
            nome_item = stream.text_input("Nome do Acessório")
            categoria = stream.text_input("Categoria")
        with col2:
            quantidade = stream.number_input("Quantidade Total", min_value=1, step=1)
            valor_aluguel = stream.number_input("Valor de Locação (R$)", min_value=0.0, step=10.0)
            
        if stream.button("Cadastrar Item", use_container_width=True):
            if nome_item:
                conexao = conectar()
                cursor = conexao.cursor()
                cursor.execute("""
                INSERT INTO acessorios (nome, categoria, quantidade_total, quantidade_disponivel, valor_locacao)
                VALUES (?, ?, ?, ?, ?)
                """, (nome_item, categoria, quantidade, quantidade, valor_aluguel))
                novo_id = cursor.lastrowid
                conexao.commit()
                conexao.close()
                registrar_alteracao("acessorios", novo_id, f"Adicionou {quantidade}x de '{nome_item}' ao estoque")
                stream.success(f"✔️ {nome_item} cadastrado!")
                stream.rerun()

    stream.subheader("📋 Itens em Estoque")
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, categoria, quantidade_disponivel, quantidade_total, valor_locacao FROM acessorios")
    itens = cursor.fetchall()
    conexao.close()

    if itens:
        for item in itens:
            id_it, n_it, cat_it, disp_it, tot_it, v_it = item
            with stream.container(border=True):
                # Aumentamos para 4 colunas para caber o botão de lixeira no final
                col_i1, col_i2, col_i3, col_i4 = stream.columns([2, 1, 1, 0.5])
                col_i1.markdown(f"**{n_it}** ({cat_it})")
                col_i2.markdown(f"🔄 **Disponível:** {disp_it} de {tot_it}")
                col_i3.markdown(f"💰 **Aluguel:** R$ {v_it:.2f}")
                
                # Botão para excluir
                if col_i4.button("🗑️", key=f"del_item_{id_it}"):
                    conexao = conectar()
                    cursor = conexao.cursor()
                    cursor.execute("DELETE FROM acessorios WHERE id = ?", (id_it,))
                    conexao.commit()
                    conexao.close()
                    
                    # Log da exclusão
                    registrar_alteracao("acessorios", id_it, f"Excluiu o item '{n_it}' do estoque")
                    
                    stream.success(f"✔️ {n_it} removido com sucesso!")
                    stream.rerun()
    else:
        stream.info("Nenhum item em estoque.")

# ==========================================
# 5. HISTÓRICO
# ==========================================
elif menu == "Histórico (Encerrados)":
    stream.header("🗄️ Histórico de Contratos Encerrados")
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, whatsapp, data_evento, atendente_responsavel, valor_total, valor_pago FROM clientes WHERE status = 'Concluído'")
    encerrados = cursor.fetchall()
    conexao.close()

    if encerrados:
        for enc in encerrados:
            id_cli, n, w, d, a, total, pago = enc
            with stream.expander(f"👤 {n} | 📅 Evento: {d} | 💰 Pago: R$ {pago:.2f}"):
                stream.markdown(f"**WhatsApp:** {w} | **Atendido por:** {a}")
                if stream.button("🔓 Reativar Cliente", key=f"reabrir_{id_cli}", use_container_width=True):
                    conexao = conectar()
                    cursor = conexao.cursor()
                    cursor.execute("UPDATE clientes SET status = 'Contrato Fechado' WHERE id = ?", (id_cli,))
                    conexao.commit()
                    conexao.close()
                    registrar_alteracao("clientes", id_cli, f"Reativou o cliente {n}")
                    stream.success(f"✔️ {n} reativado!")
                    stream.rerun()
    else:
        stream.info("Nenhum contrato arquivado.")

# ==========================================
# 6. SEGURANÇA & EQUIPE
# ==========================================
elif menu == "Segurança (Logs & Equipe)":
    stream.header("🛡️ Painel de Segurança")
    aba_logs, aba_equipe = stream.tabs(["📋 Logs de Alteração", "👥 Equipe"])
    
    with aba_logs:
        stream.subheader("🔍 Histórico de Operações")
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT usuario, tabela, descricao, data_hora FROM logs_alteracoes ORDER BY id DESC LIMIT 100")
        logs = cursor.fetchall()
        conexao.close()
        
        if logs:
            for lg in logs:
                usr, tbl, desc, dt_hr = lg
                stream.markdown(f"⏱️ **{dt_hr}** | 👤 **{usr}** em `{tbl}`: {desc}")
                stream.divider()
        else:
            stream.info("Nenhum log registrado.")
            
    with aba_equipe:
        stream.subheader("➕ Cadastrar Funcionária")
        with stream.form("cad_equipe"):
            nome_eq = stream.text_input("Nome")
            user_eq = stream.text_input("Login").strip().lower()
            senha_eq = stream.text_input("Senha", type="password")
            cargo_eq = stream.text_input("Cargo", value="Atendente")
            if stream.form_submit_button("Cadastrar"):
                if nome_eq and user_eq and senha_eq:
                    conexao = conectar()
                    cursor = conexao.cursor()
                    try:
                        cursor.execute("INSERT INTO usuarios (nome, usuario, senha, cargo) VALUES (?, ?, ?, ?)", (nome_eq, user_eq, senha_eq, cargo_eq))
                        conexao.commit()
                        registrar_alteracao("usuarios", cursor.lastrowid, f"Cadastrou {nome_eq}")
                        stream.success("Cadastrado!")
                    except:
                        stream.error("Erro ou usuário já existe!")
                    conexao.close()
                    stream.rerun()