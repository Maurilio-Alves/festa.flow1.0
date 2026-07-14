import sqlite3

# Função para conectar rápido ao banco
def conectar():
    return sqlite3.connect("festa_flow.db")

# 1. CADASTRAR (Inserção)
def cadastrar_acessorio():
    print("\n--- CADASTRAR NOVO ACESSÓRIO ---")
    nome = input("Nome do item (ex: Vaso de Cristal, Painel Redondo): ")
    categoria = input("Categoria (ex: Louças, Móveis, Painéis): ")
    
    try:
        qtd = int(input("Quantidade Total em Estoque: ") or 0)
    except ValueError:
        print("❌ Quantidade inválida. Definida como 0.")
        qtd = 0
        
    valor_input = input("Valor de Locação por unidade (R$): ").strip().replace(",", ".")
    try:
        valor = float(valor_input or 0.0)
    except ValueError:
        print("❌ Valor inválido. Definido como R$ 0.00")
        valor = 0.0

    conexao = conectar()
    cursor = conexao.cursor()
    
    # Ao cadastrar, a quantidade disponível começa igual à quantidade total
    cursor.execute("""
    INSERT INTO acessorios (nome, categoria, quantidade_total, quantidade_disponivel, valor_locacao)
    VALUES (?, ?, ?, ?, ?)
    """, (nome, categoria, qtd, qtd, valor))
    
    conexao.commit()
    conexao.close()
    print(f"✔️ {nome} adicionado ao estoque com sucesso!")

# 2. VISUALIZAR (Listagem)
def listar_acessorios():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, categoria, quantidade_total, quantidade_disponivel, valor_locacao FROM acessorios")
    itens = cursor.fetchall()
    conexao.close()
    
    if not itens:
        print("\n📭 Nenhum acessório cadastrado no estoque ainda.")
        return False

    print("\n========================= ESTOQUE DE ACESSÓRIOS =========================")
    for item in itens:
        id_item, nome, categoria, total, disponivel, valor = item
        print(f"ID: {id_item:<3} | Item: {nome:<20} | Cat: {categoria:<10} | Qtd: {disponivel}/{total} | Aluguel: R$ {valor:.2f}")
    print("==========================================================================")
    return True

# 3. REMOVER (Exclusão)
def remover_acessorio():
    # Primeiro mostra o que tem para o usuário saber qual ID escolher
    tem_itens = listar_acessorios()
    if not tem_itens:
        return
        
    print("\n--- REMOVER ACESSÓRIO ---")
    try:
        id_remover = int(input("Digite o ID do acessório que deseja deletar do sistema: "))
    except ValueError:
        print("❌ ID inválido.")
        return

    conexao = conectar()
    cursor = conexao.cursor()
    
    # Verifica se o item realmente existe antes de deletar
    cursor.execute("SELECT nome FROM acessorios WHERE id = ?", (id_remover,))
    item = cursor.fetchone()
    
    if item:
        confirmacao = input(f"Tem certeza que deseja deletar permanentemente '{item[0]}' do estoque? (S/N): ").upper()
        if confirmacao == 'S':
            cursor.execute("DELETE FROM acessorios WHERE id = ?", (id_remover,))
            conexao.commit()
            print(f"🗑️ '{item[0]}' foi removido com sucesso!")
        else:
            print("Operação cancelada.")
    else:
        print("❌ ID não encontrado no sistema.")
        
    conexao.close()

# --- MENU INTERATIVO ---
def menu():
    while True:
        print("\n--- FESTA-FLOW 1.0 (MENU DE ACESSÓRIOS) ---")
        print("1. Cadastrar Acessório")
        print("2. Ver Estoque Completo")
        print("3. Remover Acessório")
        print("4. Sair")
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            cadastrar_acessorio()
        elif opcao == "2":
            listar_acessorios()
        elif opcao == "3":
            remover_acessorio()
        elif opcao == "4":
            print("Saindo do painel de estoque... Até mais!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()