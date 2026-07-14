import sqlite3

# Função para conectar rápido ao banco festa_flow.db
def conectar():
    return sqlite3.connect("festa_flow.db")

# 1. CADASTRAR (Inserção)
def cadastrar_usuario():
    print("\n--- CADASTRAR NOVO USUÁRIO ---")
    nome = input("Nome Completo (ex: Ana Silva): ")
    usuario = input("Nome de usuário para login (ex: ana.silva): ").strip().lower()
    senha = input("Senha de acesso: ").strip()
    cargo = input("Cargo (pressione Enter para 'Atendente'): ") or "Atendente"

    if not usuario or not senha:
        print("❌ Usuário e Senha são obrigatórios!")
        return

    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO usuarios (nome, usuario, senha, cargo)
        VALUES (?, ?, ?, ?)
        """, (nome, usuario, senha, cargo))
        conexao.commit()
        print(f"✔️ Usuário '{usuario}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print(f"❌ Erro: O nome de usuário '{usuario}' já existe no sistema. Escolha outro!")
    
    conexao.close()

# 2. VISUALIZAR (Listagem)
def listar_usuarios():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, usuario, cargo FROM usuarios")
    usuarios = cursor.fetchall()
    conexao.close()
    
    if not usuarios:
        print("\n📭 Nenhum usuário cadastrado no sistema ainda.")
        return False

    print("\n========================= LISTA DE USUÁRIOS =========================")
    for user in usuarios:
        id_user, nome, login, cargo = user
        print(f"ID: {id_user:<3} | Nome: {nome:<20} | Login: {login:<15} | Cargo: {cargo:<12}")
    print("======================================================================")
    return True

# 3. REMOVER (Exclusão)
def remover_usuario():
    # Mostra quem está cadastrado antes de pedir o ID
    tem_usuarios = listar_usuarios()
    if not tem_usuarios:
        return
        
    print("\n--- REMOVER USUÁRIO ---")
    try:
        id_remover = int(input("Digite o ID do usuário que deseja remover: "))
    except ValueError:
        print("❌ ID inválido.")
        return

    conexao = conectar()
    cursor = conexao.cursor()
    
    # Verifica se o usuário existe
    cursor.execute("SELECT nome, usuario FROM usuarios WHERE id = ?", (id_remover,))
    user = cursor.fetchone()
    
    if user:
        confirmacao = input(f"Tem certeza que deseja deletar permanentemente '{user[0]}' ({user[1]})? (S/N): ").upper()
        if confirmacao == 'S':
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_remover,))
            conexao.commit()
            print(f"🗑️ Usuário '{user[1]}' foi removido com sucesso!")
        else:
            print("Operação cancelada.")
    else:
        print("❌ ID não encontrado no sistema.")
        
    conexao.close()

# --- MENU INTERATIVO ---
def menu():
    while True:
        print("\n--- FESTA-FLOW 1.0 (CONTROLE DE USUÁRIOS) ---")
        print("1. Cadastrar Usuário/Funcionária")
        print("2. Ver Usuários Cadastrados")
        print("3. Remover Usuário")
        print("4. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_usuario()
        elif opcao == "2":
            listar_usuarios()
        elif opcao == "3":
            remover_usuario()
        elif opcao == "4":
            print("Saindo do painel de usuários...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()