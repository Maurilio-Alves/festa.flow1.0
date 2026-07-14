import sys
# Importando as funções que já criamos nos outros arquivos
from cadastrar import cadastrar_cliente
from visualizar import listar_financeiro_clientes
import acessorios
import usuarios

def menu_principal():
    while True:
        print("\n=============================================")
        print("          🎉 FESTA-FLOW 1.0 - MENU 🎉         ")
        print("=============================================")
        print("1. Gerenciar Clientes (Vendas / Fluxo)")
        print("2. Gerenciar Estoque de Acessórios")
        print("3. Gerenciar Usuários / Equipe")
        print("4. Sair")
        print("=============================================")
        
        opcao = input("Escolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            menu_clientes()
        elif opcao == "2":
            # Abre o menu que já está pronto dentro de acessorios.py
            acessorios.menu()
        elif opcao == "3":
            # Abre o menu que já está pronto dentro de usuarios.py
            usuarios.menu()
        elif opcao == "4":
            print("\nObrigado por usar o Festa-Flow 1.0. Até logo!")
            sys.exit()
        else:
            print("❌ Opção inválida. Tente novamente!")

# Um mini menu para organizar as opções de clientes
def menu_clientes():
    while True:
        print("\n--- FESTA-FLOW (GERENCIAR CLIENTES) ---")
        print("1. Cadastrar Novo Cliente")
        print("2. Ver Painel Financeiro / Fluxo")
        print("3. Voltar ao Menu Principal")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            cadastrar_cliente()
        elif opcao == "2":
            listar_financeiro_clientes()
        elif opcao == "3":
            break
        else:
            print("❌ Opção inválida.")

if __name__ == "__main__":
    menu_principal()