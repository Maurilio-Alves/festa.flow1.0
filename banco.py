import sqlite3

def inicializar_banco():
    conexao = sqlite3.connect("festa_flow.db")
    cursor = conexao.cursor()
    
    # 1. TABELA DE CLIENTES (dados do evento e financeiro)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        data_evento TEXT,
        atendente_responsavel TEXT,
        status TEXT DEFAULT 'Prospecção',
        valor_total REAL DEFAULT 0.0,
        valor_pago REAL DEFAULT 0.0
    )
    """)
    
    # 2. TABELA DE ACESSÓRIOS DE LOCAÇÃO (estoque de itens para alugar)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS acessorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT,              -- Ex: Móveis, Louças, Painéis, Flores
        quantidade_total INTEGER,     -- Quantos itens a empresa tem no total
        quantidade_disponivel INTEGER, -- Quantos estão livres para alugar agora
        valor_locacao REAL DEFAULT 0.0 -- Preço cobrado pelo aluguel do item
    )
    """)
    
    # 3. TABELA DE USUÁRIOS DO SISTEMA (para o login das funcionárias)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,          -- Nome completo da funcionária (ex: Ana Silva)
        usuario TEXT UNIQUE NOT NULL, -- O nome que ela vai digitar para entrar (ex: ana.silva)
        senha TEXT NOT NULL,          -- Senha de acesso
        cargo TEXT DEFAULT 'Atendente' -- Ex: Administrador, Atendente
    )
    """)
    
    conexao.commit()
    conexao.close()
    print("✨ Banco de dados ATUALIZADO! Tabelas de Clientes, Acessórios e Usuários criadas.")

if __name__ == "__main__":
    inicializar_banco()