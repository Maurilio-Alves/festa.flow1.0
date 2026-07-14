import sqlite3

def cadastrar_cliente():
    print("\n--- CADASTRO DE NOVO CLIENTE ---")
    nome = input("Nome do Cliente: ")
    whatsapp = input("WhatsApp (com DDD): ")
    data_evento = input("Data do Evento (DD/MM/AAAA): ")
    atendente = input("Quem está atendendo? (Fabricia/Ana/Mari): ")
    
    # Etapas: Prospecção, Orçamento, Contrato, Concluído
    status = input("Status Atual (pressione Enter para 'Prospecção'): ") or "Prospecção"
    
    # Tratando o valor do contrato
    valor_total_input = input("Valor Total do Contrato (R$): ").strip()
    # Substitui a vírgula por ponto se o usuário digitar como '8500,00'
    valor_total_input = valor_total_input.replace(",", ".")
    
    # Tratando o valor pago
    valor_pago_input = input("Quanto o cliente já pagou (R$): ").strip()
    valor_pago_input = valor_pago_input.replace(",", ".")
    
    try:
        valor_total = float(valor_total_input or 0.0)
        valor_pago = float(valor_pago_input or 0.0)
    except ValueError:
        print("❌ Valor inválido digitado. Salvando como R$ 0.00")
        valor_total, valor_pago = 0.0, 0.0

    # Conectando ao banco de dados genérico correto
    conexao = sqlite3.connect("festa_flow.db")
    cursor = conexao.cursor()
    
    # Salvando na tabela genérica 'clientes'
    cursor.execute("""
    INSERT INTO clientes (nome, whatsapp, data_evento, atendente_responsavel, status, valor_total, valor_pago)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, whatsapp, data_evento, atendente, status, valor_total, valor_pago))
    
    conexao.commit()
    conexao.close()
    
    print(f"\n✔️ {nome} cadastrado com sucesso no Festa-Flow!\n")

if __name__ == "__main__":
    cadastrar_cliente()